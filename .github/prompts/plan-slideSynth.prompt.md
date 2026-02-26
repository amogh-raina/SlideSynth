# SlideSynth: Multi-Agent PDF-to-PPT System — Definitive Plan

# IMPORTANT RULE THAT YOU HAVE TO FOLLOW EVERYTIME YOU WORK ON THIS PROJECT: DO NOT READ THE ".env" file and the files which are mentioned in .gitignore.

## TL;DR

Build a deep agent-powered system using LangChain's `deepagents` SDK that converts academic PDFs into Reveal.js presentations. The orchestrator deep agent delegates to five specialized subagents (Research/Content Analyst, Planner, Designer, Generator, Editor) via the built-in `task()` tool. Parsing stays deterministic (Docling tool), while planning is split from research, giving cognitive-driven narrative planning its own dedicated agent with a plan-verification gate before generation. The harness provides the filesystem, todo tracking, and context management for free. Start with a CLI backend + simple web viewer MVP, Docling for parsing, and configurable API-based models. HTML slides are the source of truth; PDF export via Playwright. The architecture mirrors the MiniMax interaction pattern (transparent thinking, todo lists, batch generation, user approval gates).

---

## System Architecture

```
User (CLI or Web)
    │
    ▼
┌──────────────────────────────────────────────────┐
│  FastAPI Server (WebSocket streaming)             │
│  POST /chat, WS /ws, POST /resume                │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│  ORCHESTRATOR DEEP AGENT                          │
│  create_deep_agent(                               │
│    model=config.orchestrator,                     │
│    tools=[parse_pdf,                              │
│           combine_presentation, export_to_pdf],   │
│    system_prompt=orchestrator_prompt,              │
│    subagents=[research, planner, verifier, design, │
│               generator, editor],                 │
│    backend=CompositeBackend(                      │
│      default=StateBackend,                        │
│      routes={"/memories/": StoreBackend}          │
│    ),                                             │
│    skills=["./skills/"],                          │
│    checkpointer=MemorySaver(),                    │
│    interrupt_on={"submit_plan": True,             │
│                  "export_to_pdf": True}           │
│  )                                                │
│                                                   │
│  Built-in: write_todos, ls, read_file,            │
│            write_file, edit_file, glob, grep,     │
│            task() [subagent delegation]            │
└───────┬──────────┬──────────┬──────────┬─────────┘
        │       │       │       │       │
   task()  task() task() task() task()
        │       │       │       │       │
        ▼       ▼       ▼       ▼       ▼
  ┌────────┐┌────────┐┌───────┐┌───────┐┌───────┐
  │Research││Planner ││Design ││  Gen  ││Editor │
  │ Agent  ││ Agent  ││ Agent ││ Agent ││ Agent │
  │        ││        ││       ││       ││       │
  │read_   ││read_   ││read_  ││gen_   ││read_  │
  │write_  ││write_  ││write_ ││slide_ ││edit_  │
  │file    ││file    ││file   ││html   ││file   │
  │grep    ││grep    ││       ││qual_  ││write_ │
  │        ││        ││       ││check  ││file   │
  │        ││        ││       ││       ││switch_│
  │        ││        ││       ││       ││templ. │
  └────────┘└────────┘└───────┘└───────┘└───────┘
        │       │       │       │       │
        └───────┴───────┴───────┴───────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Filesystem     │
              │ (State + Store) │
              │                 │
              │ /project/       │ ← StateBackend (ephemeral)
              │   docs/         │
              │   images/       │
              │   slides/       │
              │   presentation/ │
              │                 │
              │ /memories/      │ ← StoreBackend (persistent)
              │   preferences   │
              │   instructions  │
              │   history       │
              └─────────────────┘
```

---

## Project Structure

```
slidesynth/
├── pyproject.toml
├── slidesynth/
│   ├── __init__.py
│   ├── agent.py              # Main deep agent creation
│   ├── config.py             # Model/API config (YAML/env-based)
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── parse_pdf.py      # Docling PDF→Markdown tool
│   │   ├── html_generator.py # Render Jinja2 slide templates → HTML
│   │   ├── asset_manager.py  # Image/table/equation file operations
│   │   ├── export.py         # Playwright HTML→PDF
│   │   ├── quality_check.py  # Validate generated slides
│   │   ├── verify_plan.py    # Minimal structural checks (asset IDs, figure/table separation)
│   │   └── enhanced_extract.py  # Optional LangExtract integration (NEW)
│   ├── skills/
│   │   ├── research/SKILL.md         # Research/content analysis skill
│   │   ├── planning/SKILL.md         # Cognitive-driven planning skill (NEW)
│   │   ├── verification/SKILL.md     # Semantic plan evaluation skill (NEW)
│   │   ├── design/SKILL.md           # Design skill + template refs + layout constraints
│   │   ├── slide-generation/SKILL.md # Slide generation patterns
│   │   └── editing/SKILL.md          # Edit/refine skill
│   ├── templates/
│   │   ├── title_slide.html
│   │   ├── content_text.html
│   │   ├── content_image_right.html
│   │   ├── content_image_left.html
│   │   ├── two_column.html
│   │   ├── full_image.html
│   │   ├── table_slide.html
│   │   ├── equation_slide.html
│   │   └── conclusion.html
│   ├── server/
│   │   ├── __init__.py
│   │   ├── app.py            # FastAPI + WebSocket server
│   │   └── routes.py         # REST endpoints
│   └── cli.py                # CLI entry point
├── web/                       # Simple HTML viewer (no React yet)
│   └── index.html            # Reveal.js presentation viewer
└── tests/
```

---

## Step 1: Project Scaffolding & Dependencies

Set up the Python package in `pyproject.toml`:

**Core dependencies:**
- `deepagents` — LangChain deep agents SDK (orchestration, subagents, filesystem, todos)
- `langchain` + `langgraph` — Agent framework and runtime
- `fastapi` + `uvicorn` + `websockets` — HTTP/WS server
- `docling` — PDF-to-Markdown parsing
- `playwright` — HTML-to-PDF export
- `jinja2` — Slide template rendering
- `pyyaml` — Config loading

**Model provider packages (installed based on config):**
- `langchain-openai` — GPT-4.1, GPT-4o
- `langchain-anthropic` — Claude Sonnet 4
- Any OpenAI-compatible endpoint (MiniMax M2.1, Kimi K2, DeepSeek, Qwen) via `ChatOpenAI(base_url=...)`

---

## Step 2: Orchestrator Deep Agent

The main deep agent in `agent.py` uses `create_deep_agent()`. This is the MiniMax-style orchestrator:

```python
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

agent = create_deep_agent(
    name="slidesynth-orchestrator",
    model=config.models["orchestrator"],  # e.g. "anthropic:claude-sonnet-4-5-20250929"
    tools=[parse_pdf, combine_presentation, export_to_pdf, submit_plan],
    system_prompt=ORCHESTRATOR_PROMPT,
    subagents=[research_subagent, planner_subagent, verifier_subagent, design_subagent, generator_subagent, editor_subagent],
    backend=lambda rt: CompositeBackend(
        default=StateBackend(rt),
        routes={"/memories/": StoreBackend(rt)}
    ),
    skills=["./skills/"],
    checkpointer=MemorySaver(),
    store=InMemoryStore(),
    interrupt_on={
        "submit_plan": True,           # Pause for user plan approval
        "export_to_pdf": True,         # Pause before export
    },
)
```

### Orchestrator System Prompt

```
You are SlideSynth, an AI system that converts academic research papers (PDFs)
into professional conference presentations.

## Your Workflow

1. PARSE: When a user uploads a PDF, use the parse_pdf tool to extract it into
   markdown + assets. Files are written to /project/docs/, /project/images/, etc.

2. RESEARCH: Delegate to research-agent via task() to perform deep content analysis:
   identify paper structure, key contributions, section roles, and asset significance.
   Output: /project/docs/content_analysis.md

3. PLAN: Delegate to planner-agent via task() to create a cognitive-driven slide plan
   that maps the paper's narrative arc (Problem→Motivation→Method→Results→Conclusion)
   to individual slides with 1 central message each.
   Output: /project/docs/slide_outline.json + /project/docs/plan_summary.md

4. VERIFY: Delegate to verifier-agent via task() for semantic evaluation.
   The verifier reads document.md + content_analysis.md + slide_outline.json and
   produces a scored evaluation at /project/docs/plan_evaluation.md (5 dimensions,
   each scored 1-10: coverage, narrative flow, redundancy, PMRC arc, audience clarity).
   - Score >= 7.0: proceed to plan presentation
   - Score < 7.0: verifier provides improvement directions; re-delegate to planner
     with those directions. Re-verify ONCE. If still < 7.0, proceed anyway.
   Allow at most 1 revision cycle.

5. PRESENT PLAN: Present plan_summary.md + evaluation score to user via submit_plan.
   Include slide count, narrative structure, and estimated time.

6. DESIGN: Delegate to design-agent via task() to present 3 style options and
   generate design tokens after user selection.

7. GENERATE: Delegate to generator-agent via task() to create HTML slides in
   batches of 5. After each batch, update the todo list progress.

8. REVIEW: After all slides are generated, use combine_presentation to create
   the final presentation.html. Allow user to request edits via editor-agent.

9. EXPORT: When user requests export, use export_to_pdf (this pauses for approval).

## Important

- Show your thinking process for every decision
- Update write_todos after each phase completion
- Save project decisions to /memories/project.md
- Read /memories/user_preferences.txt at start for returning users
- Always present the plan before executing
- Generate slides in batches of 5 with progress updates
```

---

## Step 3: Specialized Subagents

Each subagent is defined as a dictionary with its own tools, model, system prompt, and skills. The orchestrator delegates via `task(name="...", task="...")`. The pipeline is sequential: Research → Planner → Verifier → Design → Generator → Editor.

### 3a. Research Subagent (Content Analyst)

```python
research_subagent = {
    "name": "research-agent",
    "description": (
        "Performs deep content analysis of academic papers: identifies narrative structure, "
        "key contributions, section roles, critical figures, and equation significance. "
        "Use immediately after parse_pdf to produce /project/docs/content_analysis.md. "
        "Does NOT create slide outlines — delegate that to planner-agent."
    ),
    "system_prompt": RESEARCH_PROMPT,
    "tools": [],  # Uses built-in filesystem tools (read_file, write_file, grep, glob)
    "model": config.models.get("research"),  # Optional override
    "skills": ["/skills/research/"],
}
```

**Research System Prompt:**
```
You are a content analyst specialized in academic papers. Your job is to produce a
deep semantic understanding of the paper — NOT to plan slides.

1. Read /project/docs/document.md (the full paper in markdown)
2. Read /project/docs/assets_manifest.json (available figures, tables, equations)
3. Read /project/docs/metadata.json (title, authors, venue)

4. Analyze the paper structure and identify:
   - Narrative role of each section: which sections establish Problem, Motivation,
     Contribution, Method, Results, Limitations, Conclusion
   - Main contribution and key results (2-4 concise sentences)
   - Critical figures: which figures are central to understanding the contribution
     (not just illustrative)
   - Key equations: which formulas must appear in a talk vs. which are supplementary
   - Terminology: domain-specific terms an audience may not know
   - Paper venue conventions (ICLR/NeurIPS/CVPR/EMNLP etc.) if identifiable

5. Write outputs:
   - /project/docs/content_analysis.md — Structured analysis with sections:
     * Paper Overview (title, venue, contribution summary)
     * Section Role Map (section name → narrative role)
     * Key Assets (figure/table IDs with significance rating + rationale)
     * Core Terminology
     * Talk Constraints (15-min conference talk assumptions)

Return a concise summary of findings (key contribution, section count, asset significance).
Do NOT create a slide outline — that is the planner-agent's job.
Do NOT include raw document content in your response.
```

### 3b. Planner Subagent (NEW)

```python
planner_subagent = {
    "name": "planner-agent",
    "description": (
        "Creates a cognitive-driven slide plan from the content analysis. Maps the paper's "
        "narrative arc (Problem→Motivation→Method→Results→Conclusion) to individual slides, "
        "enforcing the 1-slide = 1-central-message principle, assigning assets to slides, "
        "and allocating slide counts by narrative section. "
        "Use after research-agent has produced /project/docs/content_analysis.md."
    ),
    "system_prompt": PLANNER_PROMPT,
    "tools": [],
    "model": config.models.get("planner"),
    "skills": ["/skills/planning/"],
}
```

**Planner System Prompt:**
```
You are a presentation planner for academic conference talks.

1. Read /project/docs/content_analysis.md (from the research agent)
2. Read /project/docs/assets_manifest.json
3. Read /project/docs/metadata.json

4. Apply cognitive-driven planning principles:
   - Narrative arc: every slide must serve Problem→Motivation→Contribution→
     Method→Results→Conclusion (some sections may span multiple slides)
   - 1 central message per slide: each slide answers exactly one question
     ("What is the problem?" / "What is our key idea?" / "What do these results show?")
   - Slide count flexibility: a complex topic may need 2-3 slides; a minor one may
     share space. Aim for 12-15 slides for a 15-minute talk.
   - Section allocation targets: Intro/Motivation 15%, Related Work 10%,
     Method 35-40%, Results 25-30%, Conclusion 5-10%
   - Front-load the hook: slides 2-3 must establish the problem compellingly

5. Asset-to-slide assignment:
   - Each critical figure should appear on the slide whose central message it
     directly supports (not the slide where it is merely mentioned)
   - Tables go on results slides; architecture diagrams go on method slides
   - Ensure every key result has exactly one supporting visual

6. Template selection for each slide:
   - title_slide: slide 1 only
   - content_image_right / content_image_left: when a figure or diagram is central
   - full_image: for the single most important figure in the paper
   - table_slide: for quantitative results tables
   - equation_slide: for 1-2 key formulas with explanation
   - two_column: for comparisons (ours vs. baseline, before/after)
   - content_text: for text-heavy slides (related work, limitations)
   - conclusion: final slide only

7. Write outputs:
   - /project/docs/slide_outline.json — Structured outline (see schema below)
   - /project/docs/plan_summary.md — Human-readable plan for user approval

Slide outline JSON schema:
{
  "slides": [
    {
      "number": 1,
      "title": "...",
      "central_message": "One sentence: what this slide answers",
      "narrative_role": "title|problem|motivation|contribution|method|results|discussion|conclusion",
      "template": "title_slide|content_text|...",
      "content_points": ["bullet 1", "bullet 2"],  // 3-5 max
      "assets": ["fig_1", "table_2"],  // IDs from manifest, or []
      "speaker_note_guidance": "What to say and how long (~N seconds)"
    }
  ],
  "total_slides": 14,
  "estimated_talk_time_min": 15
}

Return a concise summary: total slides, narrative structure overview, key asset assignments.
```

### 3c. Design Subagent

```python
design_subagent = {
    "name": "design-agent",
    "description": (
        "Presents 3 academic design style options and generates CSS design tokens. "
        "Use when the planner-agent has completed the slide outline and plan approval "
        "has been received from the user."
    ),
    "system_prompt": DESIGN_PROMPT,
    "tools": [],
    "model": config.models.get("design"),
    "skills": ["/skills/design/"],
}
```

**Design System Prompt:**
```
You are a presentation designer specializing in academic conferences.

> Note: This is MVP template-based design. Future versions will support
> reference-based editing where users upload an example presentation to
> match its visual language.

1. Read /project/docs/content_analysis.md to understand the paper topic and venue.

2. Present exactly 3 design options by writing them to /project/design/options.md:

   Option A: Academic Professional
   - Colors: Navy blue (#1e3a8a), White (#ffffff), Gray (#6b7280)
   - Fonts: Merriweather (headings), Inter (body)
   - Best for: Scientific conferences, formal academic venues

   Option B: Modern Minimal
   - Colors: Black (#111827), White (#ffffff), Blue accent (#3b82f6)
   - Fonts: Inter (all), monospace for code
   - Best for: Tech conferences, ML/AI venues

   Option C: Swiss Design
   - Colors: Black (#000000), White (#ffffff), Red (#dc2626)
   - Fonts: Helvetica/Arial exclusively
   - Best for: Design-focused venues, formal presentations

3. After receiving the user's choice (via the task description), generate:
   - /project/design/design_spec.md — Full design specification
   - /project/design/design_tokens.json — CSS custom properties:
     {
       "colors": {"primary": "#1e3a8a", "background": "#ffffff", ...},
       "fonts": {"heading": "Merriweather", "body": "Inter"},
       "sizes": {"h1": "36px", "h2": "24px", "body": "18px"},
       "spacing": {"slide_padding": "60px", "content_gap": "24px"}
     }

Return a summary of the selected design and token file location.
```

### 3d. Generator Subagent

```python
generator_subagent = {
    "name": "generator-agent",
    "description": (
        "Generates individual HTML slides in batches using Reveal.js templates, "
        "applying design tokens and content from the outline. Use after research "
        "and design phases are complete."
    ),
    "system_prompt": GENERATOR_PROMPT,
    "tools": [generate_slide_html, quality_check],
    "model": config.models.get("generator"),
    "skills": ["/skills/slide-generation/"],
}
```

**Generator System Prompt:**
```
You are an HTML slide generator for academic presentations using Reveal.js.

1. Read these files:
   - /project/docs/slide_outline.json — What to put on each slide
   - /project/design/design_tokens.json — How it should look
   - /project/docs/document.md — Source content for accurate text

2. Generate slides in batches of 5. For each slide:
   a. Select the appropriate template from the outline
   b. Fill in content from the outline and source document
   c. Apply design tokens as CSS custom properties
   d. Reference assets by their paths (e.g., /project/images/fig_1.png)
   e. Write speaker notes in <aside class="notes"> tags
   f. Use generate_slide_html tool to render and save the slide

3. After each batch of 5, run quality_check on the generated slides.
   Fix any issues before proceeding to the next batch.

4. Content guidelines:
   - 4-6 bullet points per slide maximum
   - ~30 words per bullet point
   - Speaker notes: 30-60 seconds of talking points per slide
   - Include transitions to next slide in notes
   - Use the paper's exact terminology and notation

5. Write each slide to /project/slides/slide{N}.html (1-indexed, zero-padded: slide01.html)

Return a summary: total slides generated, any quality issues found, generation time.
```

### 3e. Editor Subagent

```python
editor_subagent = {
    "name": "editor-agent",
    "description": (
        "Modifies specific slides based on user feedback in a ReAct-style loop: "
        "Understand → Locate → Search → Plan → Execute → Verify. "
        "Supports condensing, expanding, relayout, asset add/remove, speaker note edits, "
        "slide insert/delete/reorder. Use when the user requests changes to existing slides."
    ),
    "system_prompt": EDITOR_PROMPT,
    "tools": [switch_template, quality_check],
    "model": config.models.get("editor"),
    "skills": ["/skills/editing/"],
}
```

**Editor System Prompt:**
```
You are a slide editor operating in a ReAct-style loop. For each user request:

THINK: What change is being requested? Which slide(s)? What type of edit?
LOCATE: Read the target slide with read_file. Identify the exact region to change.
SEARCH: If expanding content, read /project/docs/document.md for source material.
         If adding an asset, read /project/docs/assets_manifest.json to find its path.
         Use grep to locate specific text if the slide references it.
PLAN: Briefly describe the specific edit before executing. Confirm it preserves
      the 1-central-message-per-slide principle.
EXECUTE: Use edit_file to make changes. Preserve all CSS custom properties
          and Reveal.js structure (<section>, <aside class="notes">, fragments).
VERIFY: Run quality_check on the modified slide. Fix any issues before returning.

Available operations:
- Condense: Reduce to max 4 bullets, tighten to ~25 words each
- Expand: Pull supporting detail from /project/docs/document.md
- Restyle: Update CSS custom properties (colors, fonts) from /project/design/design_tokens.json
- Relayout: Use switch_template tool to re-render with a different template while preserving content
- Asset add: Insert figure/table from manifest with responsive styling
- Asset remove: Remove image/table, reflow remaining content
- Speaker notes: Add/edit/remove talking points in <aside class="notes">
- Insert slide: Write a new slide{N}.html, shift subsequent slides to maintain order
- Delete slide: Remove slide{N}.html, update subsequent numbering
- Reorder: Move a slide from position A to position B, renumber affected slides

Always preserve:
- All CSS custom properties (--primary-color, --font-heading, etc.)
- Reveal.js section structure
- Design token consistency (read /project/design/design_tokens.json if unsure)

Return a summary of changes made (what changed, what was preserved, quality check result).
```

---

## Step 4: Custom Tools

### 4a. `parse_pdf` — Docling PDF→Markdown

```python
from langchain.tools import tool

@tool
def parse_pdf(pdf_path: str, project_path: str = "/project") -> str:
    """Parse an academic PDF into structured markdown + extracted assets.

    Uses Docling to convert the PDF into:
    - {project_path}/docs/document.md (full paper in markdown)
    - {project_path}/docs/metadata.json (title, authors, page count)
    - {project_path}/docs/assets_manifest.json (index of all images, tables, equations)
    - {project_path}/images/fig_*.png (extracted figures)
    - {project_path}/tables/table_*.html (extracted tables)
    - {project_path}/equations/eq_*.png (rendered equations)

    Returns a summary of extracted content.
    """
    # Implementation wraps docling.DocumentConverter
    ...
```

### 4b. `generate_slide_html` — Template Renderer

```python
@tool
def generate_slide_html(
    slide_number: int,
    template_name: str,
    content: dict,
    design_tokens: dict,
    output_path: str,
) -> str:
    """Render a Jinja2 slide template with content and design tokens into HTML.

    Args:
        slide_number: Slide number (1-indexed)
        template_name: Template to use (title_slide, content_text, content_image_right, etc.)
        content: Dict with keys like title, bullets, image_path, speaker_notes
        design_tokens: CSS custom properties dict from design_tokens.json
        output_path: Where to write the HTML file

    Returns confirmation with file path and any warnings.
    """
    ...
```

### 4c. `combine_presentation` — Assemble Final Reveal.js

```python
@tool
def combine_presentation(slides_dir: str = "/project/slides", output_path: str = "/project/presentation.html") -> str:
    """Combine individual slide HTML files into a single Reveal.js presentation.

    Reads all slide{N}.html files from slides_dir, wraps them in the Reveal.js
    scaffold with navigation, and outputs the final presentation.html.

    Returns the output path and total slide count.
    """
    ...
```

### 4d. `quality_check` — Validate Slides

```python
@tool
def quality_check(slide_paths: list[str]) -> str:
    """Validate generated HTML slides for common issues.

    Checks:
    - No empty content sections
    - Referenced images exist
    - Text not too long (>200 words per slide = warning)
    - Valid HTML structure
    - Design tokens applied consistently
    - Speaker notes present

    Returns a report with pass/fail per slide and specific issues.
    """
    ...
```

### 4e. `export_to_pdf` — Playwright Export

```python
@tool
def export_to_pdf(presentation_path: str = "/project/presentation.html", output_path: str = "/project/exports/presentation.pdf") -> str:
    """Export the Reveal.js presentation to PDF using Playwright.

    Renders presentation.html in a headless Chromium browser and saves as PDF.
    Each slide becomes one page.

    Returns the output path and file size.
    """
    ...
```

### 4f. `verify_plan` — Minimal Structural Checks (Utility)

```python
@tool
def verify_plan(
    outline_path: str = "/project/docs/slide_outline.json",
    manifest_path: str = "/project/docs/assets_manifest.json",
) -> str:
    """Run fast structural integrity checks on a slide outline.

    Only two deterministic checks (no LLM calls):
    1. Asset ID integrity — every asset referenced exists in the manifest.
    2. Figure/table separation — no slide references both a figure and a table.

    NOTE: This tool is NOT wired into the main pipeline. Semantic evaluation
    is handled by the verifier subagent. This exists as an optional utility
    for quick structural sanity checks.

    Returns: {"status": "PASS"|"FAIL", "issues": [...]}
    """
    ...
```

### 4f-bis. Verifier Subagent (Replaces rule-based verify_plan in the pipeline)

```python
verifier_subagent = {
    "name": "verifier-agent",
    "description": (
        "Semantic plan evaluator. Reads document.md, content_analysis.md, and "
        "slide_outline.json. Scores 5 dimensions (coverage, narrative, redundancy, "
        "PMRC arc, clarity) each 1-10. Writes /project/docs/plan_evaluation.md. "
        "Produces improvement directions when score < 7.0."
    ),
    "system_prompt": VERIFIER_PROMPT,
    "tools": [],  # Uses built-in filesystem tools
    "model": config.models.get("verifier"),
    "skills": ["/skills/verification/"],
}
```

### 4g. `switch_template` — Relayout Existing Slide (NEW)

```python
@tool
def switch_template(
    slide_path: str,
    new_template: str,
    design_tokens_path: str = "/project/design/design_tokens.json",
) -> str:
    """Re-render an existing slide HTML with a different template.

    Extracts content (title, bullets, assets, speaker notes) from the current
    slide HTML, then renders it into the specified new template with design
    tokens applied. Overwrites the slide file in place.

    Args:
        slide_path: Path to slide{N}.html to relayout
        new_template: Target template name (content_text, content_image_right, etc.)
        design_tokens_path: Path to design_tokens.json

    Returns confirmation with the old and new template names.
    Used by the editor-agent for layout change operations.
    """
    ...
```

### 4h. `enhanced_extract` — Optional LangExtract Integration (NEW)

```python
@tool
def enhanced_extract(
    document_path: str = "/project/docs/document.md",
    output_path: str = "/project/docs/enhanced_analysis.json",
    model_id: str = "gemini-2.5-flash",
) -> str:
    """Optional: use LangExtract to produce source-grounded structured extraction
    from the parsed markdown.

    LangExtract (github.com/google/langextract) maps every extraction to its exact
    location in the source text, enabling verification that key claims and figures
    cited in the slide plan actually exist verbatim in the paper.

    Extracts:
    - Key claims (with text span provenance)
    - Section roles (introduction/method/results labels)
    - Figure caption → semantic label mappings
    - Equation significance flags

    Outputs enhanced_analysis.json for the research-agent to incorporate.
    Enabled via config: parsing.enhanced_extraction: true.
    Falls back gracefully if LangExtract API call fails.

    NOTE: This is an additive complement to Docling, not a replacement.
    Docling handles PDF layout + asset extraction; LangExtract handles
    semantic structuring of the resulting text.
    """
    ...
```

### 4i. `submit_plan` — Human-in-the-Loop Plan Approval

```python
@tool
def submit_plan(plan_summary: str, slide_count: int, estimated_time_minutes: int) -> str:
    """Submit the presentation plan for user approval.

    This tool triggers an interrupt — the agent pauses and waits for
    the user to approve, modify, or reject the plan.

    Args:
        plan_summary: Markdown-formatted plan with phases and deliverables
        slide_count: Proposed number of slides
        estimated_time_minutes: Estimated generation time

    Returns the user's decision after resumption.
    """
    return f"Plan submitted: {slide_count} slides, ~{estimated_time_minutes} min"
```

---

## Step 5: Skills (Progressive Disclosure)

Skills are directories with `SKILL.md` files. The agent reads frontmatter to decide relevance, then loads full instructions only when needed.

### 5a. Research Skill (`/skills/research/SKILL.md`)

```yaml
---
name: academic-paper-research
description: Use this skill when performing content analysis of academic papers. Provides heuristics for identifying section narrative roles, assessing asset significance, and extracting key contributions. Does NOT cover slide planning.
---
```

**Contents:**
- Section role identification (Abstract, Intro, Related Work, Method, Experiments, Conclusion → narrative role mapping)
- Asset significance scoring (central figure vs. illustrative figure)
- Key equation flagging criteria
- Venue convention notes (ICLR/NeurIPS/CVPR/EMNLP format differences)
- Output schema for content_analysis.md

### 5b. Planning Skill (`/skills/planning/SKILL.md`) (NEW)

```yaml
---
name: cognitive-driven-planning
description: Use this skill when creating slide plans from content analysis. Contains narrative arc templates, slide allocation heuristics, asset assignment rules, and the slide_outline.json schema.
---
```

**Contents:**
- Narrative arc templates (15-min conference talk, 5-min lightning talk, 30-min seminar)
- Slide count allocation by section (Intro 15%, Related Work 10%, Method 35-40%, Results 25-30%, Conclusion 5-10%)
- 1-slide = 1-central-message enforcement rules
- Asset-to-slide assignment decision tree
- Template selection guide (when to use full_image vs. content_image_right vs. two_column)
- slide_outline.json schema reference with examples
- Anti-patterns to avoid (crowded slides, orphaned assets, motivation buried after method)

### 5c. Design Skill (`/skills/design/SKILL.md`)

```yaml
---
name: academic-design
description: Use this skill when creating design specifications for academic presentations. Contains the 3 design option presets, CSS token schema, and template catalog. MVP is template-based; reference-based editing is a future phase.
---
```

**Contents:**
- Full specification for 3 design options (colors, fonts, spacing, layout rules)
- CSS custom properties schema
- Template catalog with layout descriptions and when to use each
- Color contrast accessibility guidelines
- Academic venue-specific recommendations

### 5d. Slide Generation Skill (`/skills/slide-generation/SKILL.md`)

```yaml
---
name: slide-generation
description: Use this skill when generating HTML slides. Contains Reveal.js patterns, content density guidelines, speaker note format, and batch generation workflow.
---
```

**Contents:**
- Reveal.js HTML structure patterns (`<section>`, `<aside class="notes">`, fragments)
- Content density rules (4-6 bullets, ~30 words each, one key idea per slide)
- Speaker note format (talking time, transitions, emphasis cues)
- Batch generation workflow (5 at a time, quality check between batches)
- Asset insertion patterns (responsive images, styled tables, equation rendering)
- Template HTML snippets for each template type

### 5e. Editing Skill (`/skills/editing/SKILL.md`)

```yaml
---
name: slide-editing
description: Use this skill when modifying existing slides in a ReAct loop. Contains the THINK→LOCATE→SEARCH→PLAN→EXECUTE→VERIFY workflow, all edit operation patterns, and slide insert/delete/reorder procedures.
---
```

**Contents:**
- ReAct loop procedure for each operation type
- Condense/expand patterns with word-count targets
- Relayout procedure using switch_template tool
- Asset add/remove HTML patterns with responsive styling
- Slide insert/delete/reorder: file naming convention and how to update numbering
- Design consistency preservation rules (CSS custom properties must-keep list)
- Future: shallow reference search for cited papers (Phase 3+)

---

## Step 6: Memory Architecture

### CompositeBackend Layout

| Path | Backend | Lifespan | Purpose |
|------|---------|----------|---------|
| `/project/*` | StateBackend | Single thread (one session) | All working files — parsed docs, slides, intermediate outputs |
| `/memories/*` | StoreBackend | Persistent (cross-session) | User preferences, self-improving instructions, project history |

### Persistent Memory Files

```
/memories/
├── user_preferences.txt    # Design preferences, favorite templates, model prefs
├── instructions.txt        # Self-improving agent instructions from user feedback
└── project_history.md      # Log of past projects for reference
```

### Built-in Todo Tracking

The `write_todos` tool (auto-included by `create_deep_agent`) handles MiniMax-style todo tracking. The orchestrator's system prompt instructs it to use `write_todos` at each phase:

```
Todos:
- [x] Parse PDF (23s)
- [x] Content Analysis (4.1s)
- [~] Design Selection (waiting for user)
- [ ] Slide Generation (batch 1/3)
- [ ] Review & Polish
- [ ] Export
```

---

## Step 7: Human-in-the-Loop Approval Gates

Configure `interrupt_on` in `create_deep_agent`:

| Gate | Tool | When | User Actions |
|------|------|------|--------------|
| Plan approval | `submit_plan` | After orchestrator creates todo list | Approve / Modify / Cancel |
| Design selection | Orchestrator asks in chat | After design agent presents 3 options | Select A/B/C |
| Export confirmation | `export_to_pdf` | Before generating PDF | Approve / Cancel |

**Implementation pattern:**

```python
# In FastAPI server
result = agent.invoke({"messages": [...]}, config=config)

if result.get("__interrupt__"):
    interrupts = result["__interrupt__"][0].value
    action_requests = interrupts["action_requests"]
    # Send to frontend via WebSocket for user decision
    await websocket.send_json({"type": "interrupt", "actions": action_requests})

    # Wait for user decision from frontend
    user_decision = await websocket.receive_json()
    decisions = [{"type": user_decision["decision"]}]

    # Resume agent
    result = agent.invoke(Command(resume={"decisions": decisions}), config=config)
```

---

## Step 8: FastAPI Backend + WebSocket Streaming

Minimal server in `server/app.py`:

### REST Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/projects` | Upload PDF, create project thread |
| `POST` | `/api/projects/{id}/chat` | Send message to agent |
| `POST` | `/api/projects/{id}/resume` | Resume from interrupt (approve/edit/reject) |
| `GET` | `/api/projects/{id}/files/{path:path}` | Serve project files (slides, images, exports) |
| `GET` | `/api/projects/{id}/presentation` | Serve the combined presentation.html |

### WebSocket

| Path | Purpose |
|------|---------|
| `WS /ws/projects/{id}` | Stream agent events in real-time |

**Streaming implementation:** Use `agent.astream_events()` to stream LangGraph events. Each event includes `lc_agent_name` metadata to identify which subagent is working. Events sent to frontend:

```json
{"type": "thinking", "agent": "orchestrator", "content": "Analyzing paper structure..."}
{"type": "tool_call", "agent": "research-agent", "tool": "read_file", "args": {...}}
{"type": "todo_update", "todos": [...]}
{"type": "slide_generated", "slide_number": 1, "path": "/project/slides/slide01.html"}
{"type": "interrupt", "action": "submit_plan", "data": {...}}
{"type": "complete", "message": "All 14 slides generated!"}
```

---

## Step 9: Simple Web Viewer (MVP Frontend)

A single `index.html` page — no React, no build step:

- **Left panel**: Chat messages + text input (WebSocket connection)
- **Right panel**: Reveal.js iframe pointing at `presentation.html`
- **Status bar**: Current agent activity, todo progress, active subagent name
- **Styled with**: Tailwind CSS CDN
- **Interactions**: Send messages, approve/reject interrupts, download exports

This mirrors the MiniMax three-panel layout with minimal frontend investment. Upgrade to full React in Phase 5.

---

## Step 10: Model Configuration

### `config.yaml`

```yaml
models:
  orchestrator: "anthropic:claude-sonnet-4-5-20250929"
  research: "deepseek:deepseek-chat"     # Strong reasoning for content analysis
  planner: "anthropic:claude-sonnet-4-5-20250929"  # Structured narrative planning
  verifier: "anthropic:claude-haiku-4-5-20251001"  # Semantic plan evaluation
  design: "anthropic:claude-sonnet-4-5-20250929"
  generator: "openai:gpt-4.1"           # Good at structured HTML generation
  editor: "anthropic:claude-sonnet-4-5-20250929"

parsing:
  enhanced_extraction: false  # Set true to enable LangExtract complementary extraction
  langextract_model: "gemini-2.5-flash"  # Model for enhanced_extract tool

# For providers with OpenAI-compatible APIs
custom_endpoints:
  minimax:
    base_url: "https://api.minimax.chat/v1"
    api_key_env: "MINIMAX_API_KEY"
    model: "MiniMax-M2.1"
  kimi:
    base_url: "https://api.moonshot.cn/v1"
    api_key_env: "KIMI_API_KEY"
    model: "kimi-k2"
  deepseek:
    base_url: "https://api.deepseek.com/v1"
    api_key_env: "DEEPSEEK_API_KEY"
    model: "deepseek-chat"
  qwen:
    base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    api_key_env: "QWEN_API_KEY"
    model: "qwen-max"
```

For models not natively supported by LangChain's `init_chat_model`, use `ChatOpenAI` with custom `base_url`:

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    base_url="https://api.minimax.chat/v1",
    api_key=os.environ["MINIMAX_API_KEY"],
    model="MiniMax-M2.1",
)
```

---

## Step 11: CLI Entry Point

`cli.py` provides a terminal interaction mode for development and quick use:

```bash
# Parse and convert a PDF
slidesynth convert paper.pdf

# Start the web server
slidesynth serve --port 8000

# Parse only (for debugging)
slidesynth parse paper.pdf --output ./parsed/
```

The CLI reads agent streaming output, displays thinking process with timestamps, renders todo progress bars, and handles interrupt prompts interactively.

---

## Step 12: Parsing Strategy — Docling First, Agent Later

### Phase 1: Docling (Deterministic)

Docling provides reliable, deterministic PDF-to-Markdown conversion:
- Handles academic paper layouts well (two-column, figures, equations)
- Extracts images, tables as separate files
- Outputs clean markdown that LLMs can reason about naturally
- No API cost — runs locally

### Phase 2+ : Parsing Agent (Agentic, Future)

Once the output structure is stable, add an optional Parsing Agent that:
- Uses document AI APIs (Mistral Document AI, Qwen-Doc, DeepSeek OCR) for complex layouts
- Handles scanned PDFs and poor-quality images
- Enhances asset captions with AI descriptions
- Falls back to Docling if API parsing fails

### Why Markdown > JSON

| Aspect | Markdown | JSON |
|--------|----------|------|
| Token count (15-page paper) | ~30,000 | ~45,000 |
| LLM readability | Natural | Requires parsing logic |
| Human debugging | Open file, read it | Need JSON viewer |
| Agent reasoning | Works directly | Extra prompt engineering |
| Editing | Simple text edits | Schema-aware edits |

---

## Step 13: Slide Templates

Nine Jinja2 templates covering all common academic slide layouts:

| Template | Layout | Best For |
|----------|--------|----------|
| `title_slide.html` | Centered title, authors, venue | First slide |
| `content_text.html` | Full-width bullet points | Methodology, related work |
| `content_image_right.html` | 60/40 text-image split | Results with figures |
| `content_image_left.html` | 40/60 image-text split | Architecture diagrams |
| `two_column.html` | 50/50 two-column | Comparisons |
| `full_image.html` | Full-bleed image with caption | Key figures |
| `table_slide.html` | Styled HTML table | Results tables |
| `equation_slide.html` | Centered equation(s) + explanation | Key formulas |
| `conclusion.html` | Summary + future work + references | Last slide |

Each template accepts design tokens as CSS custom properties and content as Jinja2 variables.

---

## Step 14: Complete Workflow (User Perspective)

### Phase 0: Upload

```
User: Uploads paper.pdf

Orchestrator: "PDF uploaded! Parsing with Docling..."
[Thinking Process 1.2s]
"This is a 15-page PDF. I'll extract markdown, figures, tables, and equations."

✅ Completed: PDF Parsing (23s)
Files: document.md, 5 figures, 3 tables, 8 equations
```

### Phase 1: Research → Plan → Verify → User Approval

```
Orchestrator: [Delegates to research-agent]
Research Agent: [Thinking Process 4.2s]
  "The paper is a 15-page ML paper on adaptive learning rates.
   Sections: Abstract, Intro, Related Work, Method (AdaptLR algorithm),
   Experiments (4 datasets), Ablation, Conclusion.
   Critical assets: fig_2 (architecture), fig_4 (main results), table_1 (comparison)."
✔️ Content Analysis written to /project/docs/content_analysis.md

Orchestrator: [Delegates to planner-agent]
Planner Agent: [Thinking Process 3.1s]
  "Narrative arc for 15-min talk:
   - Slides 1-3: Title + Problem hook + Motivation
   - Slide 4: Contribution overview
   - Slide 5: Related Work (brief)
   - Slides 6-9: AdaptLR Method (4 slides, core contribution)
   - Slides 10-12: Experimental Results with fig_4 and table_1
   - Slide 13: Ablation study
   - Slide 14: Conclusion"
✔️ slide_outline.json and plan_summary.md written.

Orchestrator: [Delegates to verifier-agent]
Verifier Agent: [Evaluates plan semantically]
   Score: 8.4/10 (PASS)
   - Coverage: 9/10 — all contributions represented
   - Narrative: 8/10 — smooth flow, minor transition gap between slides 5-6
   - Redundancy: 9/10 — no duplication detected
   - PMRC Arc: 8/10 — good allocation
   - Clarity: 8/10 — well-designed slides
✔️ plan_evaluation.md written.

📋 Plan submitted for approval:
  ☐ Content Analysis (done, 4.2s)
  ☐ Slide Plan: 14 slides, ~15 min talk, 3 design options next
  ☐ Design Selection (~1 min + user choice)
  ☐ Slide Generation (~5 min, 3 batches)
  ☐ Review & Export

[Approve Plan] [Modify] [Cancel]

User: [Approves]
```

### Phase 2: Research → Plan → Verify → Design → Generate → Export

The orchestrator delegates to subagents in sequence via `task()`, updating todos after each phase:

1. **Research**: `task(name="research-agent", task="Perform content analysis of the parsed paper")` → writes `content_analysis.md`
2. **Plan**: `task(name="planner-agent", task="Create 14-slide cognitive-driven plan from content_analysis.md")` → writes `slide_outline.json` + `plan_summary.md`
3. **Verify**: `task(name="verifier-agent", task="Evaluate the slide plan semantically")` → writes `plan_evaluation.md` with score + improvement directions. If score < 7.0: re-delegate to planner with directions.
4. **Design**: `task(name="design-agent", task="Present 3 style options. User selected Option A: Academic Professional")` → writes `design_tokens.json`
5. **Generate**: `task(name="generator-agent", task="Generate slides 1-5")` → repeats for batches 2 and 3
6. **Export**: `combine_presentation` → `export_to_pdf` (interrupt for approval)

### Phase 3: Editing via Chat

```
User: "Make slide 3 more visual, add the motivation diagram"

Orchestrator: task(name="editor-agent", task="Modify slide 3: condense to 3 bullets,
switch to image-right layout, add fig_2.png")

Editor: Reads slide03.html, applies changes, writes back.

✅ Modified: Slide 3
- Text: 6 → 3 bullets
- Layout: text-only → image-right
- Added: fig_2.png
```

---

## Implementation Phases

| Phase | Duration | Goal | Deliverable |
|-------|----------|------|-------------|
| **1: Foundation** | Week 1-2 | Project setup, Docling parsing, basic deep agent | CLI: `slidesynth parse paper.pdf` → markdown output |
| **2: Core Pipeline** | Week 3-5 | Research + Planner + Verifier + Design + Generator subagents, 5 templates | CLI: PDF → 12+ HTML slides with design tokens |
| **3: Interactive** | Week 6-7 | HITL (plan approval, design selection), FastAPI + WebSocket, web viewer | Web: Upload PDF, approve plan, see slides generated live |
| **4: Export & Polish** | Week 8-9 | Playwright PDF export, quality checks, speaker notes, editor ReAct loop, memory | PDF export, insert/delete/reorder slides via chat |
| **5: Full UI** | Week 10-12 | React three-panel UI (MiniMax-style), PostgresSaver, multi-model testing | Production-ready web app |
| **6: Advanced** | Week 13+ | LangExtract enhanced extraction, reference-based design, PPTX export, cited paper search | Extended feature set |

---

## Deep Agents Features Mapping

| Deep Agents Feature | SlideSynth Usage |
|-----|------|
| `create_deep_agent()` | Orchestrator agent with full harness |
| `task()` tool + Subagents | 6 specialized subagents (research/planner/verifier/design/generator/editor) |
| `CompositeBackend` | Ephemeral project files (`StateBackend`) + persistent memories (`StoreBackend`) |
| `write_todos` (TodoListMiddleware) | Phase tracking visible to user — MiniMax-style todo list |
| `interrupt_on` | Plan approval, export confirmation |
| Skills (progressive disclosure) | Research, planning, design, generation, editing domain instructions |
| `astream_events()` | Real-time thinking process + progress streamed to WebSocket |
| `SummarizationMiddleware` | Long edit conversations stay within context window |
| `ModelFallbackMiddleware` | Graceful degradation if primary model API is down |
| `ToolRetryMiddleware` | Retry Docling parsing or Playwright export on transient failure |
| `FilesystemMiddleware` (built-in) | `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep` — agents read/write project files |
| Long-term memory (`StoreBackend`) | User preferences and self-improving instructions persist across sessions |
| Conversation history summarization | Automatically compresses old conversation when context window fills |
| Large tool result eviction | Docling output (30K+ tokens) auto-evicted to filesystem, agent reads back as needed |
| Prompt caching (Anthropic) | System prompts cached across turns — reduces latency and cost for Claude models |

---

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Agent framework | `deepagents` SDK (`create_deep_agent`) | Built-in filesystem, todos, subagents, HITL, summarization — no need to build custom LangGraph state machine |
| PDF parsing (Stage 1) | Docling (deterministic tool, not agent) | Handles layout, figure extraction, OCR; no LLM reasoning needed at this stage |
| PDF parsing (Stage 2, optional) | LangExtract complementary extraction | Additive source-grounded semantic extraction from markdown; enabled via config flag; does NOT replace Docling |
| Research vs. Planning | Split into 2 subagents | Context isolation: research stuffs context with paper; planner gets clean context with distilled analysis |
| Plan validation | Verifier subagent (LLM-based semantic evaluation) + minimal `verify_plan` tool (structural checks only, not wired into pipeline) | Verifier scores 5 dimensions (1-10) with actionable improvement directions; structural tool kept as optional utility for asset ID integrity and figure/table separation |
| Slide format | HTML (Reveal.js) source of truth | LLMs generate HTML naturally; PDF export via Playwright; PPTX deferred |
| MVP frontend | CLI + simple web viewer (vanilla HTML) | Validate agent pipeline before investing in React |
| LLM models | API-based only (no local inference) | One model per subagent, configurable; MiniMax M2.1, Kimi K2, DeepSeek, Qwen via OpenAI-compatible endpoints |
| Parsing format | Markdown over JSON | 30% fewer tokens, natural for LLMs, human-debuggable |
| Domain knowledge | Skills with progressive disclosure | Reduces startup tokens; only loads instructions relevant to current task |
| Memory | `CompositeBackend`: ephemeral + persistent | Project files are session-scoped; user preferences persist forever |
| Approval flow | `interrupt_on` on `submit_plan` + `export_to_pdf` | User approves plan before execution; confirms before generating export |
| Template system | 9 Jinja2 templates (MVP) → reference-based (future) | Template-based is deterministic and debuggable for MVP; reference-based editing deferred to Phase 6 |
| Editor pattern | ReAct loop (THINK→LOCATE→SEARCH→PLAN→EXECUTE→VERIFY) | Explicit structure prevents blind edits; insert/delete/reorder supported via file operations |

---

## Verification Criteria

| Phase | Test |
|-------|------|
| Phase 1 | `slidesynth parse test_paper.pdf` → `/project/docs/document.md` created with sections, `assets_manifest.json` lists all figures |
| Phase 2 | End-to-end: PDF → `presentation.html` with 12+ slides; verifier scores >= 7.0; correct design tokens applied; speaker notes on every slide |
| Phase 3 | Interrupt flow: agent pauses at `submit_plan`, user approves via WebSocket, agent resumes. Todo progress streams in real-time |
| Phase 4 | PDF export renders all slides. Editor ReAct loop: "insert a new slide after slide 3", "delete slide 7", "move slide 5 to position 8" → correct renumbering |
| Phase 6 | LangExtract enhanced extraction: `enhanced_extract` tool runs on document.md, returns source-grounded JSON with text span provenance for each claim |
| Integration | Upload a real 15-page ICLR/NeurIPS paper → complete presentation with accurate content, proper design, speaker notes, plan verification PASS, PDF export |
