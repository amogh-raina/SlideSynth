# SlideSynth — Persistent Agent Memory

This file is loaded at the start of every SlideSynth session (MemoryMiddleware).
The agent can update it via `edit_file /memories/AGENTS.md` to record preferences,
project conventions, and lessons learned across multiple PDF conversion sessions.

---

## Project File Conventions

- Output directory layout: `/docs/`, `/design/`, `/slides/`, `/images/`, `/tables/`
- Slide files are named `slide01.html` … `slideNN.html` (zero-padded to 2 digits)
- Design tokens live at `/design/design_tokens.json`
- Content analysis lives at `/docs/content_analysis.md`
- Slide outline lives at `/docs/slide_outline.json`
- Assets manifest lives at `/docs/assets_manifest.json`
- Final combined presentation: `/presentation.html`

---

## Presentation Style Preferences

- Maximum 5 bullets per slide — prefer diagrams/images over long bullet lists
- Speaker notes must be substantive: 2–3 sentences per slide expanding the key point
- White or near-white backgrounds (#ffffff or #f8f9fa) for readability and printing
- Avoid text overload — if audience visible text exceeds ~400 words on one slide, split it
- Every slide must reinforce the paper's `central_message` at least indirectly

---

## Domain Colour Defaults

| Domain | Primary Colour |
|--------|---------------|
| Computer Science / ML / AI | `#1a3a6b` (navy blue) |
| Biology / Medicine / Neuroscience | `#1a5c3a` (forest green) |
| Physics / Engineering / Robotics | `#1a4a5c` (dark teal) |
| Mathematics / Statistics | `#3d1a6b` (deep purple) |
| Chemistry / Materials Science | `#6b1a2a` (dark crimson) |

---

## Quality Standards

- All slides must pass `quality_check` with no FAIL status before export
- Tables must be rendered as HTML (`.html` table files from asset manifest), not images
- Equations must be valid KaTeX-compatible LaTeX, rendered via MathJax in Reveal.js
- Every figure/table rated "recommended" in content_analysis.md must appear in a slide
- No section may contain more than 50% of total slides

---

## Context Management Rules (enforce these in every session)

- **Subagent outputs**: Each subagent must return ≤250 words. Large data → filesystem only.
- **Filesystem over context**: Always write large content (HTML, JSON, Markdown) to disk;
  never return raw file contents in agent-to-agent messages.
- **Incremental reading**: Use `read_file` with `offset` and `limit` for files > 200 lines.
- **Grep before read**: Use `grep` to locate relevant sections before reading entire files.

---

## Session History & Learned Preferences

<!-- The agent appends entries here as preferences are expressed or discovered. -->
<!-- Format: "YYYY-MM-DD: <preference or convention learned>" -->