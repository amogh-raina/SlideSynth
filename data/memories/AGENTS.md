# SlideSynth — Persistent Agent Memory

## Project Conventions
- Output directory layout: /docs/, /design/, /slides/, /images/, /tables/
- Slide files are named slide01.html … slideNN.html (zero-padded to 2 digits)
- Design tokens live at /design/design_tokens.json
- Content analysis lives at /docs/content_analysis.md
- Slide outline lives at /docs/slide_outline.json

## Presentation Style Preferences
- Prefer visually rich slides over text-heavy bullet lists
- Use metric cards and visual callouts for key numbers
- Use white or near-white backgrounds for readability
- Speaker notes must be substantive (4–6 sentences each)
- Transform small tables (2-4 rows) into metric cards when sensible
- Never show grey "No image" placeholders — switch template instead
- Avoid 3+ consecutive slides of the same template type

## Visual Design Principles
- Design options should have evocative names (e.g., "Scholarly Precision")
- Extended colour system: primary, secondary, accent, highlight, highlight_background
- Accent colour for metric cards, callout backgrounds, and data highlights
- All custom HTML must use colours from design_tokens.json

## Data Visualisation Approach
- Key numbers → metric cards (up to 4 per slide)
- Small comparison tables → horizontal bar charts
- Large tables → highlighted tables with best results emphasised
- Complex tables → simplified with non-essential columns removed
- Always include context with numbers (e.g., "+2.1% vs SOTA")

## Quality Standards
- Every slide must reinforce the paper’s central_message
- All tables rendered as HTML (not images)
- Equations rendered with MathJax (KaTeX-compatible LaTeX)
- Final export must pass quality_check with no FAIL status
- Asset decisions (USE_AS_IS/TRANSFORM/DESCRIBE/SKIP) based on relevance, not visual inspection
- Images are extracted at high quality by docling — do NOT re-assess image quality via vision

## Memory Update Instructions
Update this file whenever the user expresses a preference, corrects a default,
or when a project reveals useful conventions to remember for future sessions.
Write updates to /memories/AGENTS.md using write_file or edit_file.

## Session History & Learned Preferences
<!-- The agent appends entries here as preferences are expressed or discovered. -->
<!-- Format: "YYYY-MM-DD: <preference or convention learned>" -->
