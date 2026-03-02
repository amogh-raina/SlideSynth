## Plan: Conversational SlideSynth — Chat-First Architecture

**TL;DR:** Reshape SlideSynth from a pipeline-triggered tool into a chat-first application. The orchestrator becomes a conversational agent that can discuss the PDF, answer questions, and only triggers the presentation pipeline when the user is ready. Design options stream in chat (no `options.md`). The editor becomes on-demand (user asks for edits). The orchestrator does its own brief QA scan instead of a separate verifier. SQLite persistence ensures conversation state survives server restarts. Context window management prevents long chats from crashing. The frontend upload flow stops auto-commanding the pipeline.

---

### Phase 1 — Conversational Orchestrator & Pipeline Restructure

**1. Rewrite `ORCHESTRATOR_PROMPT`** in agent.py (lines 99-198)

Replace the rigid 7-step pipeline with a two-mode system:

- **Chat mode (default)**: The orchestrator is a knowledgeable AI assistant. When a PDF is uploaded, it reads the parsed `document.md` and can answer questions about the paper, discuss its content, help the user think about what they want. It asks about the user's role (author vs reader), audience, emphasis. It does NOT auto-start the pipeline.
- **Pipeline mode**: Triggered when the user explicitly wants slides (e.g., "create the presentation", "let's make slides", or after the orchestrator has gathered enough context and proposes: "Ready to start building your slides?"). Then it follows the pipeline: Parse → Research → Design → Generate → QA scan → Combine.

Key sections of the new prompt:
- **Identity**: "You are SlideSynth, an AI assistant for academic presentations. You can chat about papers, answer questions, and create polished Reveal.js presentations."
- **Context gathering**: "When a user uploads a PDF, read it and give a brief overview. Ask what kind of presentation they want. If they provide context with the upload, incorporate it. If they say 'just make it', proceed with sensible defaults."
- **Pipeline steps**: Same as current but — (a) no automatic editor step, (b) design options presented in chat not from a file, (c) after Combine, tell user presentation is ready and they can request edits in chat.
- **On-demand editing**: "When the user asks for changes after the presentation is ready, delegate to the `editor` subagent with the specific request."
- **QA scan**: After generation, before combine, the orchestrator reads a few slide files and does a 2-3 sentence quality note. No separate verifier.
- **Document Q&A**: "You can read /docs/document.md to answer user questions about the paper. Use the built-in `read_file` tool."

**2. Update `RESEARCH_PROMPT`** in agent.py (lines 166-364)

Add a preamble section: "You may receive additional context about the user's goals, audience, role (author/reader), and emphasis preferences. If provided, tailor the narrative arc, slide emphasis, and content selection accordingly."

**3. Update `DESIGN_PROMPT`** in agent.py (lines 366-478)

- Mode A: Remove the instruction to write `/design/options.md`. Instead: "Return a well-formatted summary of all 3 options in your response text. Do NOT write any file. The orchestrator will present your options directly in the chat."
- Mode B: Unchanged (writes `design_tokens.json`).

**4. Update `EDITOR_PROMPT`** in agent.py (lines 660-770)

Reframe from "automatic two-pass review" to "on-demand editing agent":
- "You receive specific edit requests from the user (via the orchestrator). Apply the requested changes to the relevant slide files."
- "If the user asks for general improvements without specifics, use the quality checklist below to guide your review."
- Keep the full two-pass checklist as reference, but frame it as a tool the editor uses when asked, not something it runs automatically.

**5. Update `_make_subagents()`** in agent.py (lines 777-859)

- Editor: update description to "On-demand presentation editor — activated when the user requests changes to slides via chat." Add `generate_slide_html`, `copy_asset_to_slide`, `resolve_asset`, `list_assets` to its tools (currently only has `switch_template`, `quality_check`) so it can make substantive edits.
- Design: update description to note it returns options as text (no file output for Mode A).

**6. Add `quality_check` to orchestrator tools** in agent.py (lines 905-907)

Add `quality_check` to the orchestrator's tool list so it can do a quick QA scan after generation without delegating to a separate agent.

**7. Update upload flow in App.vue** (lines 112-142)

- **No message with upload**: Change the auto-sent message from `"Convert the uploaded PDF '${file.name}' into a Reveal.js presentation. The PDF is at '${data.pdf_path}'."` to `"I've uploaded a research paper: '${file.name}'. The PDF is at '${data.pdf_path}'."` — This provides the PDF path without commanding the pipeline, letting the orchestrator engage conversationally.
- **Message with upload**: Keep the user's message + PDF path info, but remove the trailing `" Convert it into a Reveal.js presentation."` — trust the user's own message.

**8. Update skills/design/SKILL.md**

Remove references to writing `options.md`. Frame Mode A as "return options in your response text."

**9. Update skills/editing/SKILL.md**

Reframe from "automatic review" to "on-demand editing with quality checklist as reference material."

**10. Fix duplicate line in `_DEFAULT_AGENTS_MD`** in agent.py (lines 52-53)

Remove the duplicate "Slide outline lives at /docs/slide_outline.json" line.

---

### Phase 2 — Persistence (SQLite Checkpointer)

**11. Add `langgraph-checkpoint-sqlite` dependency** in pyproject.toml

Add `"langgraph-checkpoint-sqlite>=2.0.0"` to the `dependencies` list. This transitively brings in `aiosqlite`.

**12. Replace `MemorySaver` with `SqliteSaver`** in agent.py (line 903)

```python
from langgraph.checkpoint.sqlite import SqliteSaver
```

In `create_agent()`, replace `MemorySaver()` with `SqliteSaver.from_conn_string("data/checkpoints.db")`. This stores all conversation state (message history, interrupt state, todo progress) in a SQLite file at `data/checkpoints.db`.

The `InMemoryStore` stays — it's only needed for SDK requirements, and the actual cross-session memory (`/memories/AGENTS.md`) already uses `FilesystemBackend` which writes to disk.

**13. Update `get_agent()` cache** in agent.py (lines 925-948)

The agent cache currently creates a new `MemorySaver` per project. With SQLite, all projects can share a single DB file (LangGraph namespaces by `thread_id`). Adjust the cache to share one `SqliteSaver` instance across all agents, or create one DB per project directory.

**Decision**: One global `data/checkpoints.db` shared across projects. Simpler, and LangGraph's checkpointer already namespaces state by `thread_id`. Update `create_agent()` to accept an optional checkpointer parameter, and have `get_agent()` create it once.

---

### Phase 3 — Context Window Management

**14. Add message trimming** in app.py (lines 140-151)

Before passing messages to `agent.astream_events()`, implement a trimming strategy:

- Use LangGraph's `trim_messages` utility (from `langchain_core.messages`) to keep the conversation within a token budget.
- Strategy: Keep the system message + last N messages (e.g., last 20 turns or ~100k tokens). Older messages are summarized or dropped.
- This prevents long chat sessions from exceeding the model's context window.
- The full history remains in `chat_history.json` for UI display — trimming only affects what's sent to the LLM.

**Note**: The actual trimming is lightweight — LangGraph's checkpointer stores full history, but we control what's passed to the LLM via the messages input. Since `_stream_agent` currently sends only the latest user message (`{"messages": messages}`) and the checkpointer provides history, the trimming happens at the checkpointer's message retrieval level. We may need to configure `create_deep_agent` with a `messages_modifier` or apply trimming in a custom callback.

---

### Phase 4 — Frontend Resilience

**15. Add WebSocket reconnection** in useWebSocket.js (lines 24-28)

Add auto-reconnect with exponential backoff in the `onclose` handler. When the connection drops, attempt to reconnect after 1s, 2s, 4s, 8s (max 30s). Show a "Reconnecting..." status in the UI.

**16. Persist active project in `localStorage`** in App.vue / app.js

Save `store.threadId` and project name to `localStorage` on project switch. On page load, auto-restore the last active project and reconnect.

---

### Phase 5 — Cleanup & Verification

**17. Remove stale references**

- Grep for `options.md` across all files and remove references (design skill, agent prompts, any comments).
- Grep for `plan_evaluation` (should already be gone, double-check).
- Grep for `content_analysis` (should already be gone, double-check).

**18. Syntax verification**

- `python3 -c "import ast; ast.parse(open('agent.py').read()); print('OK')"`

**19. Frontend build**

- `cd web-app && npx vite build`

**20. Manual test checklist**

- Upload PDF without message → orchestrator gives paper overview, asks what user wants
- Upload PDF with "I'm the author presenting at NeurIPS" → orchestrator incorporates context
- Ask a question about the paper → orchestrator reads document.md and answers
- Say "create the slides" → pipeline runs
- Design options appear in chat text (no options.md created on disk)
- After presentation is ready, ask "make the title bigger" → editor handles it
- Restart server → reconnect → conversation state preserved

---

### Future Work (not in this plan's implementation scope)

| Item | Priority | Notes |
|------|----------|-------|
| Authentication (API key or OAuth) | P1 | Required before any public deployment |
| CORS middleware | P1 | `app.add_middleware(CORSMiddleware, ...)` |
| Rate limiting | P2 | Per-IP or per-session throttling |
| Rich chat history (persist tool events, thinking) | P2 | Currently only final messages saved |
| Agent cache eviction (LRU/TTL) | P2 | Prevents memory leak with many projects |
| Concurrent message queuing | P2 | Queue user messages if agent is busy |
| RAG for very long documents | P3 | Embedding + vector search for 50+ page papers |
| Pipeline resume after crash | P3 | Detect existing slides and continue from where it stopped |
| Project metadata (rename, created_at) | P3 | Better UX |
| File size limits on upload | P3 | Prevent abuse |
| Project export (ZIP download) | P3 | Convenience feature |

---

### Decisions

- SQLite checkpointer for persistence (zero-cost, no infra, `langgraph-checkpoint-sqlite`)
- Full-document reads for Q&A (no RAG — sufficient for most papers)
- Auth deferred — documented as P1 future work
- Editor is on-demand only — no automatic QA pass
- Orchestrator does its own brief QA scan (no verifier subagent)
- Design options streamed in chat text, `options.md` eliminated
- One global `data/checkpoints.db` for all projects
