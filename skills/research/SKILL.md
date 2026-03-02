---
name: research
description: Unified content analysis and slide planning for academic papers. Reads the parsed paper and assets, performs knowledge extraction, and produces an enriched slide_outline.json with narrative_direction briefs, key_data, and visual_notes per slide. Does not produce bullet lists — produces communication briefs for the generator.
---

# Research & Slide Planning Skill — Knowledge-to-Brief Architecture

## Purpose

Transform a parsed academic paper into a complete `slide_outline.json` where
each slide is represented as a **communication brief** — not a pre-rendered
bullet list. You are a creative director briefing a visual designer (the
generator). Your job is to define what argument each slide must make and what
evidence supports it. The generator decides the visual form.

## Core Philosophy

**You write arguments. The generator builds slides.**

You are responsible for:
- What claim each slide must establish
- What evidence from the paper supports each claim
- How each argument should be framed and what tone it should carry
- Which assets are relevant and what transformation they need

You are NOT responsible for:
- Whether content becomes bullets, metric cards, or a two-column layout
- Specific HTML structure or styling
- Visual composition decisions (left vs right, full vs partial image)

The `narrative_direction` field is your primary output per slide.
`key_data`, `visual_notes`, and `slide_goal` complete the brief.
`bullets[]` does not exist in your output.

## Reading Strategy (Ordered)

1. Read `/docs/assets_manifest.json` first — understand available visual assets.
2. Read `/docs/document.md` from top to bottom:
   - Abstract: extract central_message candidate
   - Introduction: background context + problem motivation
   - Related Work: enrich understanding of what's unsolved
   - Methods: solution overview + technical approach
   - Results: evidence, key numbers, comparisons, ablation findings
   - Conclusion: impact and future directions
3. For each figure/table in the manifest, note type, caption, and relevance.
4. Only after reading fully: begin planning slides.

---

## Slide Title Writing Guide

This is the first thing you write for each slide and the most important.

### The One Rule
> A slide title is the CONCLUSION, not the SUBJECT.

The audience reads the title first. A topic label ("The Framework") forces
them to read the whole slide to understand the point. A claim ("A framework
that learns your style from examples you already have") lets them understand
the point immediately — the slide body becomes supporting evidence.

### Title Formula by Narrative Phase

**Hook slides (problem/context):** Make the stakes clear.
- Pattern: "[Phenomenon] because [reason]" or "[X] fails to [Y]"
- "Creating slides manually costs researchers 4-8 hours per paper"
- "Current AI tools produce generic output because they ignore the presenter"

**Explain slides (method):** State the design decision, not the design.
- Pattern: "[Approach] by [key mechanism or insight]"
- "A three-stage pipeline that mirrors how humans actually prepare talks"
- "Preferences are learned implicitly from examples the user already has"

**Prove slides (results):** State the finding. Include a number if possible.
- Pattern: "[Method] outperforms/achieves/demonstrates [claim with evidence]"
- "SlideTailor outperforms all baselines across every evaluation dimension"
- "81.63% of expert reviewers preferred our output over the best baseline"

**Inspire slides (conclusion):** State the broader takeaway.
- Pattern: "[This work] enables/proves/shows [implication]"
- "Personalization transforms automated slide generation from tool to collaborator"

### Anti-Patterns (never use)
| Bad title | Why | Fix |
|---|---|---|
| "The [X] Framework" | Topic label — no claim | "A [X] framework that [key claim]" |
| "Experimental Results" | Section label | State the headline finding directly |
| "Related Work" | Section label | "Prior methods fail on [specific problem]" |
| "Limitations" | Neutral label | "Two limitations remain before broader deployment" |
| "Method Overview" | No claim | "The core insight: [one sentence]" |

---

## Narrative Direction Writing Guide

`narrative_direction` is a prose communication brief of 80-150 words.
It is the most important field in the slide object.

### What it must contain
1. **The argument** — what claim must the audience accept? State it first.
2. **The evidence** — what specific paper content supports it? Name it.
3. **The framing** — how to position it: "contrast with prior work",
   "emphasise practical implication", "walk through each component in order"
4. **The tone** — urgent (problem), explanatory (method), confident (results),
   inspiring (conclusion)

### Format
- 80-150 words
- One coherent paragraph
- No hyphens, no numbered lists, no bullet syntax inside the direction
- Write it as you would brief a designer colleague verbally

### Quality Check Before Writing
Ask yourself:
1. Does my first sentence state a claim, not a topic?
2. Do I name specific evidence (numbers, mechanisms, failure cases)?
3. Does a generator reading this know HOW to frame the content?
4. Is the tone right for this moment in the narrative?

## key_data Writing Guide

`key_data` is a short list of facts that must appear on the slide verbatim.
It is your insurance that the generator does not approximate or drop critical
numbers.

**Include:**
- Exact percentages: "75.80% overall score", "81.63% human win rate"
- Exact comparisons: "+8.5pp vs PPTAgent (67.30%)"
- Specific cost or scale figures: "$0.016 per deck (Qwen2.5)"
- System/model names that must be spelled accurately: "PPTAgent", "AutoPresent"

**Do NOT include:**
- General descriptions (those belong in narrative_direction)
- Anything that should be paraphrased rather than quoted exactly

**Leave as `[]`** for slides with no hard numerical requirements.

**Example for a results slide:**
```json
"key_data": [
  "SlideTailor: 75.80% overall score",
  "PPTAgent: 67.30% (best baseline, +8.5pp gap)",
  "Human win rate: 81.63% (40 wins / 9 losses / 11 ties)",
  "Cost: $0.665/deck (GPT-4.1) vs $0.016/deck (Qwen2.5)"
]
```

---

## visual_notes Writing Guide

`visual_notes` tells the generator what content form fits this narrative
and how to handle the key_data visually. It is REQUIRED on every slide
except title_slide and conclusion.

### Always state:
1. What content form fits the narrative? (large callout, metric cards,
   two-column contrast, annotated figure, styled table, or bullet list)
2. What should dominate visually?
3. How to render key_data — do not let it become a buried bullet

## Slide Object Schema (Full Reference)

```json
{
  "slide_number": 1,
  "title": "Argumentative claim (8-15 words) — what the audience concludes from this slide",
  "template": "title_slide | content_text | content_image_right | content_image_left | table_slide | full_image | two_column | equation_slide | conclusion",
  "section": "hook | explain | prove | inspire",
  "narrative_direction": "80-150 word prose brief: argument + evidence + framing + tone. No bullets.",
  "key_data": ["Exact number or fact that must appear verbatim", "..."],
  "assets": ["asset_id"],
  "asset_decision": "USE_AS_IS | TRANSFORM | DESCRIBE | SKIP | null",
  "asset_transform": "metric_cards | html_bar_chart | highlighted_table | simplified_table | two_column_comparison | null",
  "visual_notes": "Required (except title/conclusion). Content form + visual emphasis + key_data rendering.",
  "speaker_notes": "4-6 sentences. What to SAY, not what the slide shows. Include transition.",
  "slide_goal": "After this slide, the audience understands/believes ___"
}
```

---

## Asset Decision Framework

For EVERY asset in the manifest, make an explicit decision.
Base decisions on TYPE, CAPTION, and RELEVANCE — not visual inspection.

### Figure Assessment
| Figure Type | Default Decision | Template |
|---|---|---|
| Architecture / flow diagram | USE_AS_IS | full_image or content_image_* |
| Results chart/graph | USE_AS_IS or TRANSFORM | content_image_* or content_text |
| Problem illustration | USE_AS_IS | content_image_* |
| Complex multi-part figure | TRANSFORM (describe key panel) | content_text |
| Qualitative examples | USE_AS_IS | content_image_* |
| Supplementary figures | Usually SKIP | — |

### Table Assessment
| Table Type | Best Presentation | asset_transform |
|---|---|---|
| Main results (< 5 methods) | Highlighted table | highlighted_table |
| Main results (> 5 methods) | Top rows + metric cards | metric_cards |
| Ablation study | Highlighted table | highlighted_table |
| Dataset statistics | Compact metric cards | metric_cards |
| Hyperparameters | SKIP — speaker notes only | null |

### Priority Rules
| Asset Type | Priority |
|---|---|
| Architecture / flow diagram | HIGH — always include |
| Main result table (Table 1) | MANDATORY — always include |
| Main result visualisation | HIGH |
| Problem illustration | MEDIUM-HIGH |
| Ablation tables | HIGH |
| Qualitative examples | MEDIUM |
| Dataset statistics tables | LOW — summarise as metric cards |
| Hyperparameter tables | SKIP |
| Supplementary figures | LOW |

---

## Template Selection Guide

| Situation | Template |
|---|---|
| Text argument with no figure | content_text |
| Argument + supporting figure | content_image_right or content_image_left |
| Hero diagram (self-explanatory, high quality) | full_image |
| Two sides being contrasted | two_column |
| Data comparison table | table_slide |
| Key numbers / headline metrics | content_text (generator adds custom_html metric cards) |
| Key equation | equation_slide |
| Final summary | conclusion |

---

## Slide Planning Rules

### Adaptive Slide Count
| Paper Complexity | Recommended Slides |
|---|---|
| Short / workshop (< 6 pages) | 8-12 |
| Standard single-contribution | 12-16 |
| Rich multi-contribution | 16-22 |
| Survey / review paper | 15-20 |

Quality over quantity. 12 excellent slides beat 18 mediocre ones.

### Section Allocation
| Section | Purpose | Target % |
|---|---|---|
| hook | Title, context, problem statement | 15-20% |
| explain | Solution overview, architecture, components | 35-45% |
| prove | Results, comparisons, ablations | 25-35% |
| inspire | Implications, future work, closing | 5-15% |

### Layout Rules
- **Figure-Table Separation:** NEVER assign both a figure AND a table to one slide
- **Template Variety:** No more than 3 consecutive same-template slides
- **Visual Coverage:** 40-60% of content slides should have a visual element
- **Text Run Limit:** No more than 3 consecutive text-only slides

### Monotony Prevention Check
Before writing the JSON, list your planned templates in order.
If you see 3+ consecutive content_text entries → STOP. Fix at least one:
- Any comparison in those slides? → two_column
- Any figure available? → content_image_*
- Any numbers? → content_text (generator will build metric cards from key_data)
- One strong claim? → content_text with bold callout (specified in visual_notes)

A run of 5+ slides with no visual element is always a planning failure. Fix here.

### Content Deduplication
Every slide must teach something NEW. If two slides overlap > 50%, merge them.
Ask: "Does this slide contain at least one insight that does NOT appear anywhere else?"

### Speaker Notes (per slide)
- 4-6 sentences (80-150 words)
- What the presenter SAYS, not what the slide SHOWS
- Include specific numbers or context not visible on the slide
- Include transition to next slide ("This brings us to...")
- NEVER repeat slide content verbatim

---

## Quality Checklist

Before writing slide_outline.json, verify:

### Titles
- [ ] Every title is an argumentative claim (8-15 words), not a topic label
- [ ] No title starts with "The [X]" or names a section of the paper
- [ ] Every title passes the "stand-alone readability" test

### Narrative Directions
- [ ] Every slide (except title and conclusion) has a narrative_direction > 60 words
- [ ] Every narrative_direction opens with a claim, not a description
- [ ] No narrative_direction contains bullet syntax (hyphens, numbered lists)
- [ ] Every narrative_direction names specific evidence from the paper

### Key Data
- [ ] All critical numbers are captured verbatim in key_data
- [ ] key_data uses exact figures (never "about 75%" or "approximately 80%")

### Visual Notes
- [ ] Every content slide has a visual_notes entry (not empty, not generic)
- [ ] Every visual_notes entry specifies a content form, not just "show the figure"
- [ ] key_data rendering is specified in visual_notes for data-heavy slides

### Structure
- [ ] central_message is 30 words max with a measurable claim
- [ ] key_numbers has 3-8 entries suitable for metric cards
- [ ] Title slide is first, conclusion slide is last
- [ ] No slide has both a figure AND a table
- [ ] Every asset has an explicit decision (USE/TRANSFORM/DESCRIBE/SKIP)
- [ ] No more than 3 consecutive same-template slides
- [ ] No more than 3 consecutive text-only slides
- [ ] HIGH-priority assets are all assigned to slides
- [ ] Every slide has a unique slide_goal

---

## Output Summary (IMPORTANT: keep context clean)

Return a concise summary (400 words max) stating:
1. Paper title and authors
2. Central message (one sentence)
3. Narrative arc chosen and rationale
4. Total slide count and section breakdown (hook/explain/prove/inspire)
5. Template distribution
6. Asset decisions summary (USE_AS_IS / TRANSFORM / DESCRIBE / SKIP counts)
7. Top 3 narrative_direction highlights (the 3 slides you're most confident about)
8. Key numbers extracted (top 3 key_data candidates)
9. Path of file written

Do NOT return the full JSON contents.