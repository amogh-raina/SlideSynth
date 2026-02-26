---
name: editing
description: Slide editing and QA using a 7-point PMRC verification checklist and structured ReAct loop. Covers figure-table separation enforcement, content deduplication detection, PMRC flow assessment, and central message tracing.
---

# Slide Editing Skill — PMRC Quality Assurance

## Purpose

Review all generated slides against the PMRC framework and apply targeted
improvements so that every slide passes quality verification and faithfully
represents the paper's content with optimal clarity and audience impact.

## 7-Point Verification Checklist

Run this checklist BEFORE making any edits. Flag every violation, then fix
them systematically.

### 1. Figure-Table Separation
**Rule:** No slide may contain BOTH a figure AND a table.

Detection:
- Scan each slide's HTML for both <img> and <table> elements
- If both present -> SPLIT into two slides

Fix:
- Create a new slide for the table (table_slide template)
- Keep the figure on the original slide (content_image template)
- Renumber subsequent slides

### 2. Content Deduplication (DISTINCT VALUE RULE)
**Rule:** Every slide must teach the audience something NEW.

Detection patterns:
- Title slide repeats content that appears again on slide 2 or 3
- Two slides with nearly identical bullet points (>50% overlap)
- Author/venue information repeated beyond the title slide
- Key contributions listed once AND repeated in conclusion
- Experimental setup details spread across multiple slides

Fix:
- Merge overlapping slides into one comprehensive slide
- Remove duplicated content from the less important location
- If both locations are important, rephrase to add unique value

### 3. Content Density
**Rule:** No slide exceeds 5 bullets or ~80 visible words.

Detection:
- Count bullets: if > 5 -> overloaded
- Count words per bullet: if any > 12 words -> too long
- Check for full paragraphs (<p> tags) in slide body -> convert to bullets
- quality_check reports word count > 400

Fix priority:
- First: Cut to the 3-4 most important points (use slide_goal as guide)
- Then: Shorten long bullets to fragments
- Last resort: Move overflow content to speaker_notes

### 4. PMRC Narrative Flow
**Rule:** Presentation must follow Problem -> Method -> Results -> Conclusion.

Detection:
- Read slides in order — does the narrative build logically?
- Is the first content slide about FIELD IMPORTANCE (not paper details)?
- Are methodology slides BEFORE results slides?
- Does each phase transition feel natural (not abrupt)?

Fix:
- Reorder slides if narrative flow is broken
- Add transition hints in speaker notes between phases
- If a methodology slide appears after results, move it

### 5. Central Message Alignment
**Rule:** The paper's central_message must be traceable through the presentation.

Detection:
- Read central_message from content_analysis.md
- Check: Does the title slide imply or state it?
- Check: Does at least one results slide quote the headline number?
- Check: Does the conclusion restate the central_message?
- Count: Is it referenced (directly or paraphrased) in >= 3 slides?

Fix:
- If missing from title: add as subtitle or weave into speaker notes
- If missing from results: add headline number to key results slide
- If missing from conclusion: add as first takeaway bullet
- If fewer than 3 references: weave into speaker notes of related slides

### 6. Speaker Notes Quality
**Rule:** Every slide must have meaningful, non-repetitive speaker notes.

Detection:
- Notes are empty or missing
- Notes are a single short sentence (< 20 words)
- Notes repeat bullet text verbatim (>75% word overlap)
- Notes lack transition to next slide

Fix template:
"[Main talking point expanding on the slide's key insight]. [Supporting detail
or anecdote the audience won't see on screen]. [Specific number or reference].
This leads us to [next slide topic]..."

Good: "This 3x speedup comes from our novel attention pruning — mention that
      we measure wall-clock time, not FLOPs, which is a stronger claim.
      Transition: Now let's look at how each component contributes..."

Bad: "The slide shows the speedup results."

### 7. Template-Content Match
**Rule:** Every slide's template must match its content type.

Detection:
- Figure-heavy slide using content_text -> should be content_image_*
- Text-only slide using content_image_* (empty image slot) -> should be content_text
- Comparison slide using content_text -> should be two_column
- Single equation discussed at length using content_text -> should be equation_slide

Fix:
- Call switch_template with the appropriate template
- Verify the re-rendered slide preserves all content
- Read the first 5 lines to confirm correct structure

## ReAct Loop Protocol

For each issue found in the checklist:

THINK  -> What specific checklist item is violated? What's the impact?
LOCATE -> Which slide file(s) are affected? Read the file.
SEARCH -> If needed, re-read content_analysis.md for original wording,
          or slide_outline.json for the intended slide_goal.
PLAN   -> State the specific fix: edit content | switch_template | rewrite notes | split slide
EXECUTE -> Apply the change using edit_file or switch_template.
VERIFY -> Run quality_check on the changed slide(s). If still FAIL, loop again.

Do not apply changes without first stating THINK and PLAN. This prevents
cascading errors.

## Content Rewriting Guidelines

When editing HTML directly:
- Keep all changes inside the existing <section> tag
- Do not remove <aside class="notes"> — only update its content
- Maintain the CSS classes from the template (reveal-slide, slide-content, etc.)
- Use <strong> for emphasis, not <b> or inline styles

When shortening bullets:
- Keep the first and last bullet (they are most memorable)
- Cut middle bullets that are most similar to others
- Never reduce below 2 bullets unless it is a title or full_image slide

## Template Switching Rules

Before calling switch_template, confirm:
1. The new template is valid: title_slide, content_text, content_image_right,
   content_image_left, two_column, table_slide, equation_slide, full_image, conclusion
2. The slide's assets are compatible (image template requires an image)
3. You are NOT switching a title_slide or conclusion (these are fixed roles)

After switch_template, verify the file was written by reading the first 5 lines.

## Completion Criteria

The editing pass is complete when ALL of the following are true:

- [ ] quality_check on all slides returns PASS or WARN (no FAIL)
- [ ] No figure-table violations (each slide has one or the other, not both)
- [ ] No content duplication across slides (DISTINCT VALUE RULE satisfied)
- [ ] Content density within limits (no slide exceeds 5 bullets)
- [ ] PMRC flow is logical and progressive
- [ ] Central message appears in >= 3 slides (title, results, conclusion)
- [ ] Every slide has meaningful speaker notes with transitions
- [ ] Every template matches its content type

## Output Summary

Report to the orchestrator:
- Total slides reviewed
- Checklist violations found (by category)
- Changes made (template switches, content edits, note rewrites, splits)
- Final quality_check overall status
- Any remaining WARN items and why they are acceptable
```