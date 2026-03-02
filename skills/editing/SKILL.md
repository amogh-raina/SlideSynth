---
name: editing
description: On-demand slide editing with quality checklists for content accuracy and visual impact. Used when the user requests specific changes or general improvements to generated slides.
---

# Slide Editing Skill — On-Demand Quality & Editing

## Purpose

Apply targeted edits to generated slides based on user requests, or perform
a systematic quality review when asked for general improvements. This skill
provides the quality checklists and editing protocols used when the user
asks for changes via chat after the presentation is created.

Think like a presentation designer AND a fact-checker — apply precise fixes
when given specific requests, or use the checklists below for general reviews.

## How This Skill Is Used

1. **Specific edit requests**: User asks for particular changes (e.g., "Make
   slide 5 more visual"). Apply the requested changes directly.
2. **General improvement requests**: User asks for overall review. Use the
   two-pass quality checklist below to guide a systematic review.

## Quality Checklist (reference material for general reviews)

### Pass 1: Content Integrity (fix first — visual polish is wasted on wrong content)
### Pass 2: Visual Impact (elevate every slide from correct to compelling)

---

## Pass 1: Content Integrity Checklist

### 1.1 Figure-Table Separation
**Rule:** No slide may contain BOTH a figure/image AND a table.

Detection:
- Scan each slide's HTML for both `<img>` and `<table>` elements
- If both present → SPLIT into two slides

Fix:
- Create a new slide for the table (table_slide template)
- Keep the figure on the original slide
- Renumber subsequent slides

### 1.2 Content Deduplication (DISTINCT VALUE RULE)
**Rule:** Every slide must teach the audience something NEW.

Detection patterns:
- Title slide content repeated on slide 2 or 3
- Two slides with >50% bullet overlap
- Author/venue info repeated beyond title slide
- Key contributions listed twice (overview AND conclusion verbatim)
- Same data point quoted on multiple slides without new insight

Fix:
- Merge overlapping slides into one comprehensive slide
- Remove duplicated content from the less important location
- If both locations are important, rephrase to add unique value
- For repeated data points, add different context ("...but at 2x lower cost")

### 1.3 Content Density
**Rule:** No slide exceeds 5 bullets or ~80 visible words.

Detection:
- Count bullets: if > 5 → overloaded
- Count words per bullet: if any > 12 words → too long
- Full paragraphs in slide body → should be converted to bullets or visual
- quality_check reports word count > 400

Fix priority:
1. Cut to the 3-4 most important points (use slide_goal as guide)
2. Shorten long bullets to fragments
3. Move overflow content to speaker_notes
4. If still too dense, split into two slides

### 1.4 Narrative Flow
**Rule:** Presentation must build progressively — each slide earns the next.

Detection:
- Read slides in order — does the narrative build logically?
- Is the first content slide about CONTEXT, not paper details?
- Does each transition feel natural (not abrupt)?
- Does the conclusion reference the central_message?

Fix:
- Reorder slides if flow is broken
- Add transition hints in speaker notes between sections
- If a methodology slide appears after results, move it

### 1.5 Central Message Alignment
**Rule:** The paper's central_message must be traceable through the presentation.

Detection:
- Read central_message from slide_outline.json metadata
- Check: Does the title slide imply or state it?
- Check: Does at least one results slide quote the headline number?
- Check: Does the conclusion restate the central_message?
- Count: Is it referenced in >= 3 slides?

Fix:
- If missing from title: add as subtitle or weave into speaker notes
- If missing from results: add headline number to key results slide
- If missing from conclusion: add as first takeaway bullet

### 1.6 Speaker Notes Quality
**Rule:** Every slide must have meaningful, non-repetitive speaker notes.

Detection:
- Notes empty or < 20 words
- Notes repeat bullet text verbatim (>60% word overlap)
- Notes lack transition to next slide
- Notes are purely descriptive ("This slide shows...")

Fix template:
\`\`\`
[Main talking point expanding on slide's key insight — what to SAY, not
what the slide shows]. [Supporting detail or anecdote]. [Specific number
or reference for credibility]. This leads us to [next slide topic]...
\`\`\`

### 1.7 Template-Content Match
**Rule:** Every template must match its content type.

| Symptom | Fix |
|---|---|
| Figure-heavy slide using content_text | → content_image_right/left |
| Text-only slide using content_image_* (empty image) | → content_text |
| Comparison slide using content_text | → two_column |
| Single equation discussed at length | → equation_slide |
| Slide with custom_html using basic template | → content_text with custom_html |

---

## Pass 2: Visual Impact Checklist

### 2.1 Data Presentation Quality
**Rule:** Numerical data should be SHOWN, not just told.

Detection — Flag these anti-patterns:
- Raw table pasted as-is when it should be a metric card or chart
- More than 3 numbers in bullet text without visual treatment
- Table with only 2-3 rows that would be better as metric cards
- Comparison data in prose form instead of two_column layout

Fix:
- For small tables (2-4 rows): rewrite as metric cards in custom_html
- For comparison data: rewrite as styled two-column or bar chart
- For key numbers: promote to callout/metric card format
- For large tables: ensure proper styling with highlighted best results

Metric card example (inject via custom_html):
\`\`\`html
<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem;">
  <div style="text-align: center; padding: 1.2rem; background: #f0f4ff; border-radius: 12px;">
    <div style="font-size: 2.2rem; font-weight: 700; color: var(--primary);">84.3%</div>
    <div style="font-size: 0.85rem; color: var(--muted); margin-top: 0.3rem;">Accuracy</div>
  </div>
  <!-- more cards... -->
</div>
\`\`\`

### 2.2 Image Quality Assessment
**Rule:** No grey placeholder boxes. No low-quality images without justification.

Detection:
- Grep for "No image" text or grey placeholder divs
- Look for content_image templates without an actual image_path set
- Check if assigned images actually exist at the referenced path

Fix:
- If image is missing: switch to content_text template (remove image)
- If image is low quality but data is important: extract key info from
  slide_outline.json metadata and create a custom_html replacement
- NEVER leave a grey "No image" placeholder — it looks broken

### 2.3 Template Variety & Visual Rhythm
**Rule:** No more than 3 consecutive slides of the same template type.

Detection:
- List all slides and their templates in order
- If 3+ consecutive content_text → monotonous "wall of bullets"
- If no visual slides in a run of 5+ slides → visually boring

Fix:
- Break monotony by converting a suitable slide to two_column
- If appropriate data exists, create a metric card or highlight box
- Consider whether a content_text could become content_image_* if a
  relevant diagram exists in the assets
- Use section transition slides (styled content_text with a single
  powerful statement) between major narrative phases

### 2.4 Title Slide Impact
**Rule:** The title slide should make a strong first impression.

Detection:
- Is the title just the paper name with no visual interest?
- Does it lack a subtitle (authors + venue)?
- Is there an opportunity for a key metric callout?

Fix:
- Ensure subtitle includes authors and venue/year
- If the paper has a striking headline number, consider adding it
  as a visual accent element in the title slide
- Title should be concise — shorten if > 10 words

### 2.5 Conclusion Slide Impact
**Rule:** The conclusion should leave a lasting impression.

Detection:
- Are takeaways just bullet points?
- Does the conclusion introduce new information (anti-pattern)?
- Is the central_message prominently restated?

Fix:
- Ensure 3 takeaway bullets — concise, memorable sentences
- First bullet should restate the central_message in impact terms
- Consider whether a key metric deserves a visual callout
- Do NOT introduce any information not previously covered

### 2.6 Colour & Accent Consistency
**Rule:** All colour usage must follow design_tokens.json.

Detection:
- Read design_tokens.json for the active palette
- Scan for hardcoded colours that don't match the token values
- Check that primary colour is used for headings consistently
- Check that secondary colour is used for bullet markers

Fix:
- Replace hardcoded colours with token values
- Ensure custom_html blocks use token colours, not arbitrary values

---

## ReAct Loop Protocol

For each issue found in either pass:

\`\`\`
THINK  → What specific checklist item is violated? What's the impact on audience?
LOCATE → Which slide file(s) are affected? Read the file.
SEARCH → If needed, re-read slide_outline.json metadata for source data,
         or slide_outline.json for intended slide_goal.
PLAN   → State the specific fix: edit content | switch_template | 
         rewrite notes | split slide | add custom_html | remove placeholder
EXECUTE → Apply the change using edit_file or switch_template.
VERIFY → Run quality_check on changed slide(s). If still FAIL, loop again.
\`\`\`

Do NOT apply changes without first stating THINK and PLAN.

## Content Rewriting Guidelines

When editing HTML directly:
- Keep all changes inside the existing `<section>` tag
- Do not remove `<aside class="notes">` — only update its content
- Maintain CSS classes from the template (slide-content-text, etc.)
- Use `<strong>` for emphasis, not `<b>` or inline styles
- When adding custom_html blocks, ensure they use design token colours

When shortening bullets:
- Keep the first and last bullet (most memorable positions)
- Cut middle bullets that are most similar to others
- Never reduce below 2 bullets unless it's a title or full_image slide

## Template Switching Rules

Before calling switch_template, confirm:
1. The new template is valid: title_slide, content_text, content_image_right,
   content_image_left, two_column, table_slide, equation_slide, full_image, conclusion
2. The slide's assets are compatible (image template requires an actual image)
3. You are NOT switching a title_slide or conclusion (fixed roles)

After switch_template, verify by reading the first 5 lines.

## Completion Criteria

The editing pass is complete when ALL of the following are true:

### Content Integrity
- [ ] quality_check on all slides returns PASS or WARN (no FAIL)
- [ ] No figure-table violations
- [ ] No content duplication across slides
- [ ] Content density within limits (max 5 bullets per slide)
- [ ] Narrative flow is logical and progressive
- [ ] Central message appears in >= 3 slides
- [ ] Every slide has meaningful speaker notes with transitions
- [ ] Every template matches its content type

### Visual Impact
- [ ] No grey placeholder images on any slide
- [ ] No more than 3 consecutive same-template slides
- [ ] Key numbers use visual treatments (metric cards, callouts) when applicable
- [ ] Tables are appropriately styled or transformed
- [ ] Title slide has subtitle and visual presence
- [ ] Conclusion restates central_message prominently
- [ ] Colour usage is consistent with design tokens

## Output Summary

Report to the orchestrator:
- Total slides reviewed
- Pass 1 violations found (by category)
- Pass 2 improvements made (by category)
- Template switches, content edits, note rewrites, splits performed
- Visual improvements applied (metric cards, placeholder removals, etc.)
- Final quality_check overall status
- Any remaining WARN items and why they are acceptable
- Recommendations for future improvements in content generation to reduce editing load