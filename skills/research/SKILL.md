---
name: research
description: PMRC-aligned content analysis for academic papers. Covers presentation-logic reorganisation, asset significance scoring, central message extraction, and structured output for downstream agents.
---

# Content Analysis Skill — PMRC-Aligned Knowledge Extraction

## Purpose

Transform a parsed academic paper into a content_analysis.md that reorganises
information by PRESENTATION LOGIC — not paper structure. This ensures downstream
agents (planner, generator, editor) receive pre-structured input that maps
directly to the four PMRC narrative phases.

## Core Philosophy

You are not summarising the paper. You are performing **knowledge transfer
architecture**: identifying what the audience needs to know, in what order, and
at what depth, to understand the paper's contribution and significance.

## Reading Strategy (Ordered)

1. Read `/docs/assets_manifest.json` first — understand available visual assets.
2. Read `/docs/document.md` from top to bottom with this focus:
   - Abstract — extract central_message candidate
   - Introduction — extract background_context + problem_motivation
   - Related Work — enrich background_context (what exists, what's missing)
   - Methods — extract solution_overview + technical_approach
   - Results — extract evidence_proof (numbers, tables, figures)
   - Conclusion — extract impact_significance + future directions

## PMRC Section Extraction Guide

### background_context (maps to PMRC Phase 1: Problem)

Answer: "Why does this field matter to someone outside it?"
- Look for: opening paragraphs of Introduction that discuss the field broadly
- Include: compelling statistics, real-world applications, market/societal impact
- Include: basic concepts a non-expert needs (define key terms)
- Tone: accessible, engaging, big-picture
- Length: 3-5 paragraphs

Common sources in the paper:
- First 2-3 paragraphs of Introduction
- Motivation section (if separate)
- Abstract opening sentence

### problem_motivation (maps to PMRC Phase 1: Problem)

Answer: "Given this important field, what specific problem remains unsolved?"
- Look for: "however", "despite", "limitation", "challenge", "gap" in Introduction
- Include: specific failure cases of existing methods
- Include: why the problem is hard (technical barriers)
- Include: what happens if we don't solve it (consequences)
- Tone: concrete, specific, urgent
- Length: 2-4 paragraphs

### solution_overview (maps to PMRC Phase 2: Method — overview)

Answer: "What is the core idea, in one paragraph?"
- This is the 30-second elevator pitch of the paper
- Include: main contribution in one sentence
- Include: key insight that makes this approach different
- Include: high-level design philosophy
- Do NOT include implementation details — those go in technical_approach
- Length: 1-2 paragraphs

### technical_approach (maps to PMRC Phase 2: Method — details)

Answer: "How does the method actually work?"
- Structure as a numbered list of key components/modules
- For each component: name, what it does, why it's designed this way
- Note the overall pipeline/architecture flow
- Include training protocol if novel
- Length: 3-6 paragraphs (proportional to method complexity)

### evidence_proof (maps to PMRC Phase 3: Results)

Answer: "What data proves this method works?"
- Always quote numbers with context: "84.3% on SQuAD 2.0 (Table 3)"
- Flag the HEADLINE RESULT (biggest improvement, most impressive number)
- Identify Table 1 explicitly — it almost always contains main results
- List ablation findings with what each proves about the method
- Note whether results are SOTA, competitive, or mixed
- Length: 2-4 paragraphs

### impact_significance (maps to PMRC Phase 4: Conclusion)

Answer: "Why does this matter beyond the paper?"
- Practical applications and deployment scenarios
- Limitations the authors acknowledge (be honest)
- Future directions proposed
- Broader field impact
- Length: 1-3 paragraphs

## Central Message Extraction

The central_message is ONE sentence answering:
> "What is the most important thing this paper proves or demonstrates?"

Quality criteria:
- Falsifiable or verifiable (a claim, not a topic)
- 25 words or fewer
- Uses the paper's own quantitative results where possible
- Example: **"Our pruning algorithm achieves 3x speedup with < 1% accuracy loss on ImageNet."**

Anti-patterns:
- BAD: "This paper proposes a new method for X" (too vague)
- BAD: "We study the problem of X" (not a claim)
- GOOD: Specific + measurable claim with numbers

## Asset Assessment Heuristics

### Figure Priority Scoring

| Criterion | Priority |
|---|---|
| Architecture / flow diagram of the method | HIGH — always include |
| Main result visualisation (performance curves, comparisons) | HIGH |
| Problem illustration (showing the challenge) | MEDIUM-HIGH |
| Ablation visualisation | MEDIUM |
| Qualitative examples / samples | MEDIUM |
| Related work comparison diagram | LOW-MEDIUM |
| Supplementary / appendix figures | LOW |

### Table Priority Scoring

| Criterion | Priority |
|---|---|
| Table 1 (main experimental results) | MANDATORY — always include |
| Ablation study tables | HIGH |
| Comparison with baselines | MEDIUM-HIGH |
| Dataset statistics | LOW-MEDIUM |
| Hyperparameter settings | LOW |

### Assessment Format (per asset)

For each figure/table in the manifest, output:

- **[asset_id]** (figure/table): [one-sentence description]
  - Relevance: HIGH / MEDIUM / LOW
  - Recommended PMRC phase: problem / method / results / conclusion
  - Reason: [why include or skip]

## Keywords Strategy

Keywords serve two purposes:
1. Help the planner match domain vocabulary to slide content
2. Help the designer choose appropriate visual tone

Include:
- 3-4 domain terms (e.g., "natural language processing", "transformer")
- 2-3 method-specific terms (e.g., "attention pruning", "knowledge distillation")
- 2-3 application terms (e.g., "real-time inference", "medical diagnosis")

## Quality Checklist

Before writing content_analysis.md:
- [ ] central_message is 25 words or fewer and contains a measurable claim
- [ ] background_context explains field importance without paper-specific details
- [ ] problem_motivation clearly states what's unsolved and why it's hard
- [ ] solution_overview gives a clear high-level picture in 1-2 paragraphs
- [ ] technical_approach lists all key components with purpose
- [ ] evidence_proof includes at least 2 specific numbers with context
- [ ] Table 1 is explicitly identified in asset_assessment
- [ ] keywords contains 8-15 terms
- [ ] All HIGH-priority assets are flagged with recommended PMRC phase

## Output Contract (for downstream agents)

The planner will use these sections directly:
- background_context -> Phase 1 slides (Problem)
- problem_motivation -> Phase 1 slides (Problem)
- solution_overview + key_contributions -> Phase 2 overview slides (Method)
- technical_approach -> Phase 2 detail slides (Method)
- evidence_proof -> Phase 3 slides (Results)
- impact_significance -> Phase 4 slides (Conclusion)

The designer will use:
- paper_info -> determine domain/venue
- background_context -> understand visual tone
- keywords -> domain-appropriate colour palette

Ensure all sections are rich enough for downstream consumption.
