---
name: planning
description: PMRC-framework slide planning with adaptive slide count, intelligent figure/table assignment, content deduplication, and goal-oriented section design.
---

# Slide Planning Skill — PMRC Framework

## Purpose

Transform a content_analysis.md into a presentation_plan (slide_outline.json)
that follows the PMRC (Problem -> Method -> Results -> Conclusion) narrative
framework. The plan must intelligently assign assets, prevent content
duplication, and adapt slide count to paper complexity.

## PMRC Framework — The Four Phases

Every academic presentation follows this audience journey:

### Phase 1: Problem (2-4 slides)
**Goal:** Make the audience care about the problem before showing the solution.

Slide progression:
1. **Title slide** — paper title, authors, venue
2. **Background/Context** — Why does this field matter? (use background_context)
3. **Problem Statement** — What specific gap exists? (use problem_motivation)
4. **Optional: Problem Illustration** — Visual showing the challenge (figure if available)

Key principle: Start with FIELD IMPORTANCE, not paper details. The audience must
understand why they should care before you explain what you did.

### Phase 2: Method (4-8 slides)
**Goal:** Explain the core insight first, then progressively reveal details.

Slide progression:
1. **Solution Overview** — One-slide high-level idea (use solution_overview)
2. **Architecture/Framework** — System diagram if available (figure)
3. **Key Component 1** — Most novel part of the method
4. **Key Component 2** — Supporting mechanism
5. **Optional: Training/Implementation Details** — Only if novel

Key principle: Progressive disclosure. Each slide should build on the previous.
The audience should understand the high-level idea before seeing details.

### Phase 3: Results (3-6 slides)
**Goal:** Prove the method works with evidence, not just data.

Slide progression:
1. **Experimental Setup** — Brief: datasets, baselines, metrics (1 slide max)
2. **Main Results** — Table 1 or headline figure (ALWAYS a table slide)
3. **Analysis** — What the numbers mean (NOT just "we outperform X")
4. **Ablation** — What each component contributes (if important)
5. **Optional: Qualitative Results** — Visual examples

Key principle: Present the HEADLINE RESULT first, then support with details.

### Phase 4: Conclusion (1-3 slides)
**Goal:** Leave the audience with a clear takeaway and future vision.

Slide progression:
1. **Summary & Impact** — Central message + 3-4 bullet takeaways
2. **Future Work** — Open questions and directions (if substantial)
3. **Thank You / Q&A** — Optional

## Adaptive Slide Count

Do NOT use a fixed slide count. Assess paper complexity:

| Paper Type | Indicator | Recommended Slides |
|---|---|---|
| Workshop / Short paper | 4 pages or fewer, 1-2 tables, simple method | 8-12 |
| Standard conference | 8-10 pages, 3-5 tables/figures | 12-16 |
| Content-rich / systems | 10+ pages, 6+ assets, complex architecture | 16-22 |
| Survey / tutorial | Broad coverage, many comparisons | 15-20 |

Decision factors:
- Number of HIGH-priority assets in content_analysis -> more assets = more slides
- Number of key components in technical_approach -> more components = more method slides
- Number of experiments in evidence_proof -> more experiments = more result slides
- Presence of ablation study -> +1-2 slides

## Figure/Table Assignment Rules

### ABSOLUTE RULE: NEVER put both a figure AND a table on the same slide.

This is a layout constraint, not a preference. Slides must use EITHER:
- content_image_left / content_image_right / full_image — for figures
- table_slide — for tables

### Figure Assignment Heuristics
- Architecture diagrams -> Method overview slide (Phase 2)
- Problem illustrations -> Problem statement slide (Phase 1)
- Results charts/graphs -> Analysis slides (Phase 3)
- Qualitative examples -> After quantitative results (Phase 3)
- Asset coverage target: 40-60% of content slides should have a figure

### Table Assignment Heuristics
- Table 1 (main results) -> ALWAYS gets its own dedicated table_slide
- Ablation tables -> Own table_slide after main results
- Comparison tables -> Own table_slide in results phase
- Dataset tables -> Only if essential; prefer text summary

### Table Priority Ranking
When there are more tables than available table slides, prioritise:
1. Table 1 (main results) — MANDATORY
2. Ablation tables — HIGH (include if >= 3 slides in Phase 3)
3. Comparison tables — MEDIUM
4. Dataset statistics — LOW (summarise in text instead)
5. Hyperparameter tables — SKIP (never include)

## Content Deduplication

### The DISTINCT VALUE RULE
Every slide must teach the audience something NEW that no other slide teaches.

Before adding a slide, ask: "Does this slide contain at least one insight that
does NOT appear on any other slide?" If no -> MERGE with an existing slide.

### Common Deduplication Scenarios
- Background + Problem -> Often merge-worthy if background is thin
- Main Results + Analysis -> Merge if analysis is just restating numbers
- Multiple ablation slides -> Merge unless each proves a genuinely different point
- Summary + Conclusion -> Almost always merge into one slide

### Detection Patterns
Flag these as potential duplicates:
- Two slides about "experimental setup" (combine into one)
- A slide that just reformats a table already shown (delete)
- Key contributions listed on one slide AND repeated on summary (remove from one)

## Goal-Oriented Slide Design

Every slide in the plan must have a slide_goal field answering:
> "After seeing this slide, the audience should understand/believe/feel ___."

Examples:
- BAD: "Present the architecture" (procedural, not goal-oriented)
- GOOD: "Audience understands that the system has three main components and how they connect"
- BAD: "Show Table 1" (just asset placement)
- GOOD: "Audience is convinced the method outperforms baselines on all five benchmarks"

## Template Selection Guide

| Template | Use When | PMRC Phase |
|---|---|---|
| title_slide | Opening slide only | — |
| content_text | Concept explanation, no visual needed | Any |
| content_image_left | Figure supports text on the right | 1, 2 |
| content_image_right | Figure supports text on the left | 2, 3 |
| full_image | Visual IS the content (diagram, workflow) | 2 |
| two_column | Compare/contrast, before/after | 1, 2 |
| table_slide | Quantitative data, benchmarks | 3 |
| equation_slide | Mathematical formulation is key | 2 |
| conclusion | Final summary, takeaways, Q&A | 4 |

## Content Overflow Prevention

### Density Assessment Per Slide
- Text slides: MAX 5 bullet points, MAX 12 words per bullet
- Image slides: MAX 3 bullet points alongside the image
- Table slides: MAX 2 context sentences above/below the table
- Equation slides: MAX 1 equation + 3 lines of explanation

### Smart Splitting
If content exceeds density limits:
1. Split into two slides with different slide_goals
2. Do NOT just "continue" — each split slide must have independent value
3. Re-check deduplication after splitting

### Priority Ordering Within Slides
When content must be trimmed, keep in this order:
1. Key insight (the one thing the audience must remember)
2. Supporting evidence (number, figure reference)
3. Context / background
4. Details / caveats (move to speaker notes)

## Speaker Notes Strategy

Every slide should have speaker notes guidance with:
- The main talking point (what to say when this slide appears)
- Transition cue (how to connect to the next slide)
- Time estimate (seconds, aiming for 60-90 per slide)
- Optional: audience engagement prompt (question to ask, analogy to use)

## verify_plan Pre-Flight

Before writing slide_outline.json, mentally run this checklist:
- [ ] Plan follows PMRC phase order (Problem -> Method -> Results -> Conclusion)
- [ ] Title slide is first
- [ ] Conclusion slide is last
- [ ] No slide has both a figure AND a table assigned
- [ ] Table 1 has a dedicated table_slide
- [ ] Every slide has a unique slide_goal
- [ ] Slide count matches adaptive count table for paper type
- [ ] HIGH-priority assets from content_analysis are all assigned
- [ ] No two adjacent slides cover the same topic without progression
- [ ] Content density is within limits for each template type
```