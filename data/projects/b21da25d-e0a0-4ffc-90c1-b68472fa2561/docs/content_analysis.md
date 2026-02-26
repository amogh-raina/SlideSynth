# Content Analysis: SlideTailor

## paper_info

**Title:** SlideTailor: Personalized Presentation Slide Generation for Scientific Papers

**Authors:** 
- Wenzheng Zeng (National University of Singapore)
- Mingyu Ouyang (National University of Singapore)
- Langyuan Cui (National University of Singapore)
- Hwee Tou Ng (National University of Singapore, corresponding author)

**Venue:** AAAI 2026 (Association for the Advancement of Artificial Intelligence)

**Project Website:** https://github.com/nusnlp/SlideTailor

---

## central_message

SlideTailor automatically generates personalized presentation slides from scientific papers by learning implicit user preferences from example slide decks and templates, while introducing a chain-of-speech mechanism to align visual content with oral narration.

---

## key_contributions

1. **Novel task formulation:** Introduces preference-guided paper-to-slides generation, explicitly conditioning slide generation on user-specified content and aesthetic preferences captured through natural, real-world inputs (paper-slides pairs and templates).

2. **Implicit preference distillation:** Develops a dual-branch approach to extract and represent both content preferences (narrative flow, emphasis patterns, formatting) and aesthetic preferences (layout, design elements) from unlabeled, entangled user inputs without explicit annotation.

3. **Chain-of-speech mechanism:** Proposes a novel design where the system simultaneously generates slide content and accompanying speech scripts, ensuring coherence between visual and oral delivery while enabling downstream video presentation applications.

4. **Comprehensive benchmark dataset (PSP):** Constructs the largest paper-to-slides benchmark (200 papers, 50 example pairs, 10 templates = 100,000 unique combinations) with interpretable evaluation metrics covering both preference-based and preference-independent dimensions.

5. **Agentic modular framework:** Implements a human-inspired three-stage pipeline (preference distillation → preference-guided planning → slide realization) using specialized LLM and VLM agents that progressively generates editable, high-quality slides aligned with user intent.

---

## methodology

### Overview
SlideTailor is an agentic framework that progressively generates personalized slides through three main stages: implicit preference distillation, preference-guided planning, and slide realization. The system is designed to mirror how human presenters create slides—by internalizing personal style, organizing content, and producing final slides for delivery.

### Stage 1: Implicit Preference Distillation
The system extracts user preferences from two complementary, naturally-provided inputs without explicit annotation:

- **Content preference extraction:** Uses GPT-4.1 to analyze a provided paper-slides sample pair, inferring how the user transforms source content into presentation by examining narrative structure (e.g., Title → Background → Methods → Results → Future Work), section-level emphasis or omission patterns, and formatting preferences (bullet points, visuals). This yields a structured content preference profile (P_C) capturing how much detail is emphasized or condensed across different sections.

- **Aesthetic preference extraction:** Employs a vision-language model to analyze the provided .pptx template file, identifying functional roles of both slide-level components (title, main content, conclusion) and element-level components (text boxes, image placeholders). The system also parses raw .pptx metadata (bounding boxes, positions, sizes) to create a structured aesthetic preference schema (P_A) that serves as a layout grounding mechanism.

The union of content and aesthetic preferences (P = P_C ∪ P_A) forms a modular, symbolic representation guiding subsequent generation.

### Stage 2: Preference-Guided Slide Planning
Guided by the distilled preference profile P, three specialized LLM agents progressively plan the presentation:

- **Paper reorganizer agent:** Restructures the input paper to reflect user-specific content priorities, adjusting narrative flow and detail level to match the presentation preferences extracted from the sample pair. This produces a presentation-oriented document.

- **Slide outline designer with chain-of-speech:** Segments the reorganized content into a slide-wise outline where each slide specifies intended messages and visual cues. Uniquely, this agent simultaneously drafts speech narration for each slide (chain-of-speech mechanism), ensuring alignment between visual content and anticipated oral delivery. This generates both a structured outline and speech script.

- **Template selector agent:** Matches each planned slide to the most appropriate layout from the provided template by comparing slide content with the aesthetic schema (P_A), ensuring visual presentation aligns with user preferences while maintaining coherence.

### Stage 3: Slide Realization
Two specialized agents execute the final generation:

- **Layout-aware agent:** Maps planned content (titles, text, visuals) to specific elements within the selected template layout, modifying or replacing elements as needed for coherence.

- **Code agent:** Generates executable Python code that directly edits the .pptx file to apply content and styling modifications, preserving the original theme while producing fully editable slides.

### Downstream Application: Video Presentations
The chain-of-speech mechanism generates speech scripts paired with each slide, which can be converted to personalized narration using text-to-speech systems while preserving vocal identity, enabling automated video presentation generation.

---

## results

### Quantitative Performance (PSP Dataset)

**Overall Performance (Table 2):**
- SlideTailor (GPT-4.1): **75.80% overall score** (highest among all methods)
- Baseline ChatGPT: 62.86% overall
- Baseline AutoPresent (GPT-4.1): 48.78% overall
- Baseline PPTAgent (GPT-4.1): 67.30% overall

**Preference-Based Metrics:**
- **Coverage** (subtopic alignment): 74.47% (SlideTailor-GPT4.1) vs 72.84% (AutoPresent)
- **Flow** (subtopic ordering): 66.65% (SlideTailor-GPT4.1) vs 59.58% (AutoPresent)
- **Content Structure** (stylistic alignment): 72.80% (SlideTailor-GPT4.1) vs 80.80% (ChatGPT baseline, but lower on other metrics)
- **Aesthetic** (visual alignment with template): 98.00% (SlideTailor-GPT4.1) vs 97.20% (PPTAgent)

**Preference-Independent Metrics:**
- **Content quality**: 67.64% (SlideTailor-GPT4.1) vs 47.00% (ChatGPT), 28.05% (AutoPresent), 58.36% (PPTAgent)
- **Aesthetic quality**: 75.24% (SlideTailor-GPT4.1) vs 71.96% (PPTAgent), 68.32% (ChatGPT)

**Robustness Across Models:**
- Open-source variant (Qwen2.5 + Qwen2.5VL): 69.21% overall score, demonstrating strong adaptability without model-specific tuning

### Ablation Study Results (Table 3, 30-sample subset)
- **Removing content preference guidance:** Overall score drops from 74.31% to 68.61%, with notable degradation in coverage (74.82% → 65.80%), flow (68.38% → 56.83%), and content structure (66.00% → 54.67%)
- **Disabling chain-of-speech mechanism:** Overall score drops to 69.91%, with significant impact on general content quality (66.40% → 47.33%), validating the importance of aligning slide planning with anticipated narration

### Human Evaluation
- **Win rate vs. PPTAgent (strongest baseline):** 81.63% preference rate for SlideTailor across 60 independent human ratings
- **Correlation with automated metrics:** Average Pearson correlation of 0.64 between human ratings and MLLM-based evaluations

### Cost Analysis
- GPT-4.1 variant: Average $0.665 per 10-slide deck
- Qwen2.5 variant: Average $0.016 per 10-slide deck

### Key Observations
- No method achieves >80% overall score, highlighting task difficulty
- AutoPresent fails to reflect aesthetic preferences due to text-only input
- ChatGPT struggles with visual style consistency and often omits figures/tables
- PPTAgent preserves templates well but lacks content structure alignment and has higher image extraction failure rates
- SlideTailor consistently outperforms across both preference-based and preference-independent dimensions

---

## narrative_arc

**Problem:** 
Existing automatic slide generation systems treat the task as a one-size-fits-all document-to-slides conversion, ignoring the inherently subjective nature of presentations and diverse user preferences regarding narrative structure, emphasis, conciseness, and aesthetics (Section 1).

**Motivation:** 
Different users have distinct presentation preferences that fall into two categories: content preferences (narrative flow, level of detail, emphasis) and aesthetic preferences (layout, colors, visual design). Current systems fail to capture these preferences, resulting in misaligned outputs (Sections 1-2).

**Solution Proposed:**
Rather than requiring explicit textual instruction, SlideTailor takes user-friendly inputs—example slide decks and templates—to implicitly encode preferences. The paper introduces a novel task formulation for preference-guided paper-to-slides generation and proposes a human-inspired agentic framework that progressively distills implicit preferences and generates personalized slides with a novel chain-of-speech mechanism (Sections 3-4).

**Evidence:**
The paper constructs the PSP dataset (200 papers, 50 preference examples, 10 templates = 100,000 combinations) with interpretable metrics and demonstrates that SlideTailor achieves 75.80% overall score, significantly outperforming three strong baselines (ChatGPT, AutoPresent, PPTAgent). Human evaluation confirms an 81.63% win rate, and ablation studies validate the importance of each component (Sections 5-7).

**Impact:**
The work establishes a new research direction in personalized slide generation, provides a comprehensive benchmark for future research, and enables downstream applications like automated video presentations. The modular preference distillation approach could inspire similar preference-aware systems in other document-to-visual domains (Section 8).

---

## keywords

Presentation slide generation, user preference learning, implicit preference distillation, personalization, agentic systems, conditional summarization, multimodal generation, chain-of-speech, paper-to-slides, aesthetic preferences, content preferences, visual design, automated narration, benchmark dataset, preference-guided generation, vision-language models

---

## assets_to_use

### Critical Assets (Must Include)

1. **fig_1** - Overview visualization
   - **Rationale:** Provides the high-level system concept showing preference-guided paper-to-slides generation flow with input (paper, example slides, template) and output (personalized slides + speech script). Essential for establishing the problem and solution framing.

2. **fig_2** - Conceptual pipeline diagram
   - **Rationale:** Shows the three-stage architecture (preference distillation → preference-guided planning → slide realization). Critical for explaining the methodology and how the system progresses from inputs to outputs.

3. **fig_3** - Content preference example
   - **Rationale:** Concrete visualization of how content preferences are extracted from sample pairs, showing narrative structure and section-level emphasis patterns. Helps audience understand implicit preference distillation.

4. **fig_4** - Aesthetic preference example
   - **Rationale:** Demonstrates aesthetic preference extraction from templates, showing layout schema and design element parsing. Essential for explaining the dual-branch distillation approach.

5. **fig_5** - Component outputs example
   - **Rationale:** Shows practical outputs from three key agents (paper reorganizer, slide outline designer, template selector) demonstrating the preference-guided planning stage in action.

### Supporting Assets (Recommended)

6. **fig_6** - Content structure analysis with baselines
   - **Rationale:** Comparative visualization showing how SlideTailor vs. ChatGPT and AutoPresent handle the same inputs, demonstrating superior content structure alignment and preference capture.

7. **fig_7** - Content structure analysis with PPTAgent comparison
   - **Rationale:** Shows SlideTailor vs. PPTAgent on content structure preservation, particularly useful for highlighting advantages over the strongest baseline.

### Data/Results Assets (For Results Slides)

- **Table 1** - Dataset comparison: Shows PSP dataset is largest (100,000 combinations vs. prior benchmarks' ≤595), establishing contribution novelty.
- **Table 2** - Quantitative results: Primary results showing 75.80% overall score vs. baselines, with breakdowns across 7 metrics.
- **Table 3** - Ablation results: Validates contribution of content preference distillation (→68.61%) and chain-of-speech mechanism (→47.33% content quality) to overall performance.

---

## additional_insights

### Technical Depth Points for Slides
- The system uses GPT-4.1 and Qwen2.5 as backbone LMs, demonstrating cross-model robustness
- Vision-Language Models (VLMs) are employed for both preference extraction and evaluation
- The evaluation framework uses both automatic (MLLM-as-judge) and human evaluation, with Pearson correlation of 0.64
- Cost ranges from $0.016 (open-source) to $0.665 (GPT-4.1) per slide deck, making the approach practical

### Key Limitations (For Balanced Presentation)
- Limited to scientific papers; extension to business/educational domains needed
- Training-free approach sacrifices potential performance gains from end-to-end multimodal training
- Gap remains between MLLM-based evaluation and human judgment; cross-judge evaluations show better alignment

### Downstream Potential
The chain-of-speech mechanism enables video presentation generation through text-to-speech synthesis while preserving vocal identity, and could be extended to include audio-driven talking heads for enhanced realism.
