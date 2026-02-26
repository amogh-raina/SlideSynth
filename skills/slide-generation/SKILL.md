---
name: slide-generation
description: Slide HTML generation using Jinja2 templates and Reveal.js. Covers template variable reference, figure-table separation enforcement, content density rules, overflow prevention, and batch generation workflow.
---

# Slide Generation Skill

## Purpose

Render each slide in slide_outline.json into a valid Reveal.js HTML fragment
(<section>...</section>) using the appropriate Jinja2 template with design
tokens applied.

## Template Variable Reference

Each call to generate_slide_html passes a content JSON with these keys:

| Key | Required | Description |
|---|---|---|
| title | Always | Slide heading text |
| bullets | Most templates | List of strings, max 5 items, max 12 words each |
| image_path | Image templates | Relative path from slides/ root (use copy_asset_to_slide) |
| speaker_notes | Always | Presenter notes (2-3 sentences) |
| equation | equation_slide | LaTeX string, e.g. "E = mc^2" |
| table_html | table_slide | Raw HTML of the table (inline the .html asset file) |
| subtitle | title_slide | Authors and venue line |
| col_left / col_right | two_column | Separate bullet lists for each column |

Never leave title or speaker_notes empty.

## Figure-Table Separation (CRITICAL)

### The Rule
Each slide may contain EITHER a figure OR a table — NEVER BOTH.

### Enforcement Procedure
Before generating each slide:
1. Check the assets list from the outline
2. If it contains both figure and table IDs:
   - Generate Slide A: figure + relevant bullets (content_image template)
   - Generate Slide B: table + key takeaway bullets (table_slide template)
   - Increment all subsequent slide numbers
3. Log the split in your summary

### Template-Asset Compatibility
| Template | Accepts Figure? | Accepts Table? |
|---|---|---|
| content_image_right | YES | NO |
| content_image_left | YES | NO |
| full_image | YES | NO |
| table_slide | NO | YES |
| content_text | NO | NO |
| two_column | NO | NO |
| equation_slide | NO | NO |

## Content Density Rules

### Assessment Before Generation
For each slide, count:
- Number of bullets (max 5)
- Words per bullet (max 12)
- Total visible text (max ~80 words excluding speaker notes)

### Overflow Prevention
If the outline specifies too much content:
1. Keep the 3-4 most important points (guided by slide_goal)
2. Move secondary content to speaker_notes
3. If still too much: split into two slides with different goals
4. NEVER cram — adding a slide is always better than overloading one

### Slide-Type Density Limits
| Template | Max Bullets | Max Words/Bullet | Additional |
|---|---|---|---|
| content_text | 5 | 12 | — |
| content_image_* | 3-4 | 10 | Image takes ~45% width |
| table_slide | 1-2 | 15 | Table is primary content |
| equation_slide | 2-3 | 12 | Equation is primary content |
| full_image | 0-1 | 8 | Caption only |
| two_column | 3/3 | 10 | Per column |
| title_slide | 0 | — | Subtitle only |
| conclusion | 3-4 | 15 | Complete sentences OK |

## Template Usage Rules

### title_slide
- title: Full paper title (may be long)
- subtitle: "Author1, Author2 . Venue Year"
- bullets: Leave empty ([])
- image_path: Leave empty (no image on title slide)

### content_text
- For pure-text slides with no figure
- bullets: 3-5 items
- image_path: Empty

### content_image_right / content_image_left
- bullets: 3-4 items (shorter to leave room for image)
- image_path: MUST be set — call copy_asset_to_slide first
- Image goes on the named side; text on the opposite side
- NEVER pair with a table

### two_column
- col_left: List of strings for left column
- col_right: List of strings for right column
- Label each column with a heading via the first item

### table_slide
- Read the .html asset file (from resolve_asset), then pass its content as table_html
- bullets: Optional 1-2 items highlighting the key takeaway
- Do NOT pass an image_path
- Table 1 (main results) deserves detailed analysis bullets

### equation_slide
- equation: LaTeX string — Reveal.js supports MathJax
- bullets: 2-3 lines explaining the equation's terms
- Do NOT wrap the equation in $ — the template handles that

### full_image
- image_path: Must be a high-resolution figure
- title: Short (6 words or fewer)
- bullets: Empty or 1 caption-style sentence

### conclusion
- bullets: Exactly 3 takeaways framed as complete sentences
- Last bullet should be a call-to-action ("Code at github.com/..." or "Questions welcome")

## PMRC Phase Awareness

When generating slides, be aware of the narrative phase:
- **Phase 1 (Problem)**: Emphasise accessibility and engagement
- **Phase 2 (Method)**: Emphasise clarity and progressive detail
- **Phase 3 (Results)**: Emphasise data and evidence
- **Phase 4 (Conclusion)**: Emphasise impact and takeaways

Adjust bullet tone accordingly — Phase 1 bullets should hook interest,
Phase 3 bullets should convey data confidence.

## Asset Embedding Workflow

For every non-empty assets entry in the slide outline:

1. Call copy_asset_to_slide(asset_id, slide_number) — copies the file and returns the relative path.
2. Use the returned path as image_path in the content JSON.
3. For table_slide: call resolve_asset(asset_id) to get the path, read the file, pass as table_html.

Never hardcode paths. Always use asset IDs from the manifest.

## Table Processing Rules

- Tables retain their EXACT structure from the manifest — never reformat
- Large tables (>6 rows): consider highlighting the most important rows
- Always pair a table with 1-2 bullets that interpret the data
- The headline result (from content_analysis) should be referenced in the bullet

## Quality Checklist (per batch of 5 slides)

Call quality_check(slide_paths=[...]) every 5 slides. For each FAIL:

| Issue | Fix |
|---|---|
| Missing <section> wrapper | Regenerate — template may have failed |
| Missing speaker notes | Re-render with non-empty speaker_notes |
| Word count > 400 | Reduce bullets or shorten text |
| Image not found | Re-run copy_asset_to_slide, update image_path |

Do not proceed past a batch until all FAIL items are resolved. WARN items
should be logged and reported to the orchestrator but do not block generation.

## Final Quality Gate

After generating ALL slides:
1. Collect all slide paths: /slides/slide*.html
2. Call quality_check on the full list
3. If overall status is FAIL -> fix all FAIL slides, re-run quality_check
4. Report final status summary to orchestrator

## Batch Generation Workflow

1. Read the full slide_outline.json
2. Group slides into batches of 5
3. For each batch:
   a. Generate each slide (resolve assets, render template)
   b. Run quality_check on the batch
   c. Fix any FAIL issues
   d. Report batch progress
4. After all batches: run final quality gate
```