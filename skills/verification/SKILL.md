---
name: verification
description: Semantic evaluation of slide plans against the source paper and content analysis. Covers contribution coverage, narrative flow, redundancy detection, PMRC arc coherence, and actionable improvement directions. Produces a scored assessment that feeds back to the planner for revision.
---

# Plan Verification Skill — Semantic Evaluation

## Purpose

Evaluate a slide_outline.json holistically by reading the original paper
(document.md), the structured content analysis (content_analysis.md), and the
proposed plan. Produce a scored assessment with per-dimension reasoning and,
when the score is below threshold, actionable improvement directions that the
planner can use to revise.

This is an LLM-driven semantic evaluation — it judges meaning, not syntax.
Structural integrity checks (asset ID existence, figure/table separation) are
handled separately by the lightweight `verify_plan` tool; you do NOT need to
repeat those here.

## Inputs (read from the virtual filesystem)

| File | Purpose |
|---|---|
| `/docs/document.md` | The full parsed paper — ground truth for claims and evidence |
| `/docs/content_analysis.md` | PMRC-aligned analysis from the research agent |
| `/docs/slide_outline.json` | The slide plan to evaluate |
| `/docs/assets_manifest.json` | Available figures, tables, equations (for context) |

Read ALL four files before beginning evaluation.

## Evaluation Dimensions (5 dimensions, each scored 1-10)

### 1. Contribution Coverage

**Question:** Does the plan cover every key contribution identified in
content_analysis.md, and does it do so with appropriate depth?

Evaluation steps:
- Extract the key_contributions list from content_analysis.md
- For each contribution, check whether at least one slide's title, bullets,
  or slide_goal directly addresses it
- Check that the HEADLINE RESULT (from evidence_proof) appears on a dedicated
  results slide
- Check that Table 1 (main results) has a dedicated table_slide

Scoring guide:
- **9-10**: Every contribution is covered with appropriate depth; headline
  result and Table 1 are prominently featured
- **7-8**: Most contributions covered; minor gaps in supporting evidence
- **5-6**: Key contributions present but some are superficial or missing
  supporting data
- **3-4**: Multiple contributions missing or badly represented
- **1-2**: Plan barely relates to the paper's actual contributions

### 2. Narrative Flow & Coherence

**Question:** Does the presentation tell a coherent story that builds
understanding progressively, or does it feel like a disconnected list of facts?

Evaluation steps:
- Read slide titles and slide_goals in order — does each build on the previous?
- Check for abrupt topic jumps (e.g., jumping from background to results
  without explaining the method)
- Verify the first content slide (slide 2) is about FIELD IMPORTANCE or
  CONTEXT, not immediately about the paper's technique
- Check that transitions between PMRC phases feel natural
- Verify the conclusion references the central_message from content_analysis.md

Scoring guide:
- **9-10**: Clear narrative arc with smooth transitions; audience can follow
  without confusion
- **7-8**: Generally coherent with 1-2 awkward transitions
- **5-6**: Logical order exists but several jumps feel disconnected
- **3-4**: Disjointed — feels like slide soup
- **1-2**: No discernible narrative structure

### 3. Redundancy & Duplication

**Question:** Does every slide teach the audience something NEW, or are there
slides that repeat information from other slides?

Evaluation steps:
- Compare slide_goals — are any two slides trying to achieve the same thing?
- Compare bullet content across slides — look for paraphrased repetition
- Check if author/venue info from the title slide is repeated on later slides
- Check if key contributions are listed AND then repeated verbatim in the
  conclusion (restatement is fine; verbatim repetition is not)
- Verify that background and problem are distinct (not re-explaining the same
  gap twice)

Scoring guide:
- **9-10**: Every slide adds unique value; no detectable repetition
- **7-8**: Minor overlap in 1-2 places but each slide still has distinct purpose
- **5-6**: Noticeable redundancy in 2-3 slides
- **3-4**: Several slides feel interchangeable or repetitive
- **1-2**: Heavy duplication throughout

### 4. PMRC Arc Adherence

**Question:** Does the plan follow the Problem → Method → Results → Conclusion
framework with appropriate section allocation?

Evaluation steps:
- Map each slide's section field to PMRC phases
- Check phase ordering: Problem slides should precede Method, Method before
  Results, Results before Conclusion
- Check section allocation against content complexity:
  - Problem (Phase 1): 2-4 slides (15-20%)
  - Method (Phase 2): 4-8 slides (35-45%)
  - Results (Phase 3): 3-6 slides (25-35%)
  - Conclusion (Phase 4): 1-3 slides (5-15%)
- Check that no single phase is drastically over/under-represented relative
  to the paper's content richness
- Verify title_slide is first and conclusion template is last

Scoring guide:
- **9-10**: Perfect PMRC progression with balanced allocation matching
  paper complexity
- **7-8**: Correct order; minor allocation imbalance (one phase slightly
  over/underweight)
- **5-6**: Order is correct but allocation is off (e.g., 8 method slides
  for a simple method)
- **3-4**: Phase ordering violations or major allocation problems
- **1-2**: No recognisable PMRC structure

### 5. Audience Clarity & Slide Design Quality

**Question:** Would a conference audience understand the presentation? Are
slides well-designed for knowledge transfer?

Evaluation steps:
- Check bullet count per slide (ideal: 3-5, never > 5)
- Check that slide_goals are goal-oriented ("audience understands X") not
  procedural ("show Table 1")
- Check that speaker_notes add value beyond the bullets (not just restating them)
- For methodology slides: verify progressive disclosure (overview first, then
  details)
- For results slides: verify that numbers have context (not just raw values)
- Check template selection appropriateness (e.g., table data should use
  table_slide, not content_text)

Scoring guide:
- **9-10**: Every slide is crisp, focused, and educationally designed
- **7-8**: Most slides are well-designed; 1-2 could be improved
- **5-6**: Several slides have density or clarity issues
- **3-4**: Many slides are overcrowded or poorly structured
- **1-2**: Slides are unusable for a real presentation

## Scoring & Output

### Overall Score
Compute the average of all 5 dimension scores (rounded to 1 decimal).

### Thresholds
- **Score >= 7.0**: PASS — plan is ready for user review at the HITL pause.
  Include the score and brief rationale as advisory context.
- **Score < 7.0**: NEEDS_IMPROVEMENT — produce improvement directions and
  recommend the orchestrator re-delegate to the planner.

### Output Format

Write your evaluation to `/docs/plan_evaluation.md` with this structure:

```markdown
# Slide Plan Evaluation

## Overall Score: X.X / 10

## Dimension Scores

| Dimension | Score | Summary |
|---|---|---|
| Contribution Coverage | X/10 | [one sentence] |
| Narrative Flow | X/10 | [one sentence] |
| Redundancy | X/10 | [one sentence] |
| PMRC Arc | X/10 | [one sentence] |
| Audience Clarity | X/10 | [one sentence] |

## Detailed Reasoning

### Contribution Coverage
[2-3 sentences with specific references to which contributions are/aren't covered]

### Narrative Flow
[2-3 sentences about the story arc quality]

### Redundancy
[2-3 sentences identifying any specific duplications]

### PMRC Arc
[2-3 sentences about phase ordering and allocation]

### Audience Clarity
[2-3 sentences about slide design quality]

## Improvement Directions (only if score < 7)

[Numbered list of specific, actionable changes the planner should make.
Each direction should reference specific slide numbers and what to change.]

1. ...
2. ...
```

## Evaluation Strategy

### Reading Order
1. Read `/docs/content_analysis.md` first — this is your reference for what
   the plan SHOULD cover (key_contributions, central_message, evidence_proof).
2. Read `/docs/slide_outline.json` — this is what you're evaluating.
3. Skim `/docs/document.md` — only if you need to verify a specific claim
   or check whether the plan misrepresents something.
4. Read `/docs/assets_manifest.json` — to understand what visuals are available
   and whether the plan uses them well.

### Calibration Guidance
- Be generous with novel or creative approaches to presenting the material —
  the PMRC framework is a guide, not a straitjacket.
- Be strict about contribution coverage — if a key result is missing, that's
  a clear gap.
- Narrative flow matters more than rigid phase boundaries — a paper with a
  strong visual contribution might front-load the hero figure and that's fine.
- Redundancy detection should be semantic, not just textual — two slides about
  "attention mechanism" are fine if one covers architecture and the other covers
  training dynamics.

### Improvement Directions Quality
When score < 7, improvement directions must be:
- **Specific**: "Add a dedicated slide for Contribution 3 (multi-scale fusion)
  between slides 7 and 8" — not "cover more contributions"
- **Actionable**: The planner should be able to execute each direction without
  re-reading the paper
- **Prioritised**: Most impactful changes first
- **Bounded**: 3-6 directions maximum — don't overwhelm the planner

## Anti-patterns to Flag

- **The literature review dump**: 3+ slides of "Related Work" recounting what
  other people did, without connecting to this paper's contribution
- **The figure gallery**: Slides that show a figure with no interpretive bullets
- **The conclusion that introduces new information**: Summary slides should
  only restate, not introduce
- **The method slide with no visually**: If an architecture diagram exists in the
  manifest but isn't assigned to any method slide, flag it
- **The wall of text**: Any slide with > 5 bullets or bullets > 15 words
- **The orphaned asset**: A HIGH-priority asset from content_analysis that
  appears nowhere in the plan

## Return Summary

Return a concise summary (≤ 200 words) to the orchestrator stating:
1. Overall score (X.X / 10)
2. Verdict: PASS or NEEDS_IMPROVEMENT
3. Strongest dimension and weakest dimension
4. If NEEDS_IMPROVEMENT: top 2-3 improvement directions (abbreviated)
5. Path of the evaluation file written

Do NOT return the full evaluation — the orchestrator can read the file if needed.
