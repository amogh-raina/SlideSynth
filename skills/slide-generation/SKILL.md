---
name: slide-generation
description: Slide HTML generation driven by narrative_direction briefs, key_data rendering, and visual_notes from the research agent. Covers visual form selection, token-based custom HTML patterns, asset composition, and batch generation workflow. Bullets are one option among many — metric cards, callouts, annotated figures, and two-column contrasts are equally primary.
---

# Slide Generation Skill

## Purpose

Execute the communication briefs produced by the research agent into polished,
visually compelling Reveal.js HTML. You are a visual designer reading a brief —
not a template filler reading a bullet list.

Each slide's `narrative_direction` tells you what argument to make.
`key_data` tells you what numbers must appear verbatim.
`visual_notes` tells you what form fits.
Your job is to build the best possible HTML that executes all three.

## How This Skill Receives Input

Slides in `slide_outline.json` do NOT have a `bullets[]` field.
Instead each slide has:

- `narrative_direction` — 80-150 word prose brief: the argument, evidence, and framing
- `key_data` — list of exact numbers/facts that must appear verbatim
- `visual_notes` — recommended content form and visual emphasis
- `assets`, `asset_decision`, `asset_transform` — asset handling
- `template` — suggested template (you may override with justification)
- `speaker_notes`, `slide_goal` — for notes and priority decisions

Read all fields before generating anything.

---

## Step 0: Extract Design Tokens

Before any slide, read `/design/design_tokens.json` in full.
In every custom HTML block you write, substitute actual hex values —
never use placeholder names like PRIMARY or ACCENT_COLOR.

Key values to extract and reuse everywhere:
```
colors.primary, colors.primary_dark, colors.secondary
colors.accent, colors.accent_light
colors.highlight, colors.highlight_background
colors.background, colors.text_primary, colors.text_secondary, colors.muted
colors.success, colors.warning, colors.error
fonts.heading, fonts.body
spacing.card_gap, spacing.card_padding, spacing.card_border_radius, spacing.callout_padding
typography.metric_size, typography.metric_label, typography.metric_weight
```

---

## Step 1: Read the Brief

For every slide, read in this order:

1. `title` — render it at full h2 size. It is an argumentative claim. Do not truncate.
2. `narrative_direction` — understand the argument before deciding anything else.
3. `key_data` — these numbers are non-negotiable. Plan how to render each one visually.
4. `visual_notes` — the intended content form. Follow it unless Step 2 overrides.
5. `asset_decision` — how to handle any assigned asset.

---

## Step 2: Visual Form Selection

Based on `visual_notes` and narrative, select the primary content structure.
Bullets are valid — but they are ONE option among six, not the default.

| Visual_notes indicates | Content form to build | Template |
|---|---|---|
| 1 headline number | Large standalone callout | content_text |
| 2-4 key numbers | Metric card grid | content_text |
| Key insight / finding | Callout highlight box | content_text |
| Two sides contrasted | Two-column panels | two_column |
| Figure + annotation | Image with ≤4 short bullets | content_image_* or full_image |
| Comparison data | Bar chart or highlighted table | content_text or table_slide |
| Genuinely enumerable list | Bullet list | content_text |

**When visual_notes is empty or ambiguous**, infer from narrative_direction:
- Multiple specific numbers in key_data → metric cards
- "contrast", "compare", "vs", "unlike" in narrative → two_column
- An asset is assigned → annotated figure
- One strong claim + one stat → callout box
- Actually enumerable items with no visual alternative → bullets

---

## Step 3: key_data Must Be Rendered Visually

Every item in `key_data` MUST appear on the slide in exact form.
Do NOT paraphrase. Do NOT move to speaker_notes unless the slide is
split-worthy (and then split the slide first).

Rendering rules:

| key_data count | Render as |
|---|---|
| 1 number | Large standalone callout, 3rem bold, full width centered |
| 2-4 numbers | Metric card grid |
| A pair of contrasting values | Side-by-side in two_column or bar chart |
| Table result | Highlighted row + standalone headline number above table |

The worst rendering for a key_data number is a bullet point.
"- 75.80% overall score" has zero visual weight. A 2.4rem bold
number in the paper's primary colour on a tinted card has presence.

---

## Custom HTML Patterns

Use these patterns with actual token values substituted throughout.
Never use hardcoded colours.

### Metric Card Grid (2-4 cards)
```html
<div style="display: grid; grid-template-columns: repeat(3, 1fr);
  gap: [card_gap]; margin: 1rem 0;">
  <div style="text-align: center; padding: [card_padding];
    background: [highlight_background]; border-radius: [card_border_radius];
    border-left: 4px solid [accent];">
    <div style="font-size: [metric_size]; font-weight: [metric_weight];
      color: [primary];">75.80%</div>
    <div style="font-size: [metric_label]; color: [muted];
      margin-top: 0.3rem;">Overall Score</div>
    <div style="font-size: 0.75rem; color: [success];
      margin-top: 0.2rem;">+8.5pp vs PPTAgent</div>
  </div>
  <!-- repeat for each key_data number -->
</div>
```
Adjust columns: 2 cards → `repeat(2, 1fr)`, 4 cards → `repeat(4, 1fr)`.

Add optional hover interactivity on metric cards when detail would help:
```html
style="... transition: transform 0.15s, box-shadow 0.15s; cursor: default;"
onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.1)'"
onmouseout="this.style.transform=''; this.style.boxShadow=''"
```

### Single Large Callout (1 headline number)
```html
<div style="text-align: center; padding: 2rem 1rem; margin: 1rem auto;
  max-width: 420px;">
  <div style="font-size: 3rem; font-weight: 700; color: [primary];
    line-height: 1.1;">81.63%</div>
  <div style="font-size: 1rem; color: [text_secondary]; margin-top: 0.5rem;
    font-weight: 600;">Human Win Rate</div>
  <div style="font-size: 0.85rem; color: [muted]; margin-top: 0.3rem;">
    40 wins / 9 losses / 11 ties — 60 expert-evaluated pairs</div>
</div>
```

### Callout / Highlight Box (key finding or framed insight)
```html
<div style="background: [highlight_background]; border-left: 4px solid [accent];
  border-radius: 8px; padding: [callout_padding]; margin: 0.8rem 0;">
  <div style="font-weight: 600; color: [primary]; margin-bottom: 0.4rem;
    font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.04em;">
    Key Finding</div>
  <div style="font-size: 1rem; color: [text_primary]; line-height: 1.55;">
    Removing content preference distillation drops overall performance by 5.7pp,
    with coverage falling 9pp and flow falling 11.5pp — proving the preference
    pipeline is essential, not decorative.
  </div>
</div>
```

### Horizontal Bar Chart (method comparison)
```html
<div style="display: flex; flex-direction: column; gap: 0.65rem;
  margin: 1rem 0; max-width: 580px;">
  <!-- Best method (ours) -->
  <div style="display: flex; align-items: center; gap: 1rem;">
    <div style="width: 110px; font-size: 0.85rem; text-align: right;
      color: [text_primary]; font-weight: 600;">SlideTailor</div>
    <div style="flex: 1; background: [highlight_background]; border-radius: 4px;
      height: 30px; position: relative;">
      <div style="width: 75.8%; height: 100%; background: [primary];
        border-radius: 4px; display: flex; align-items: center; padding: 0 10px;">
        <span style="color: white; font-size: 0.78rem; font-weight: 700;">75.80%</span>
      </div>
    </div>
  </div>
  <!-- Baselines — use [muted] for their bars -->
  <div style="display: flex; align-items: center; gap: 1rem;">
    <div style="width: 110px; font-size: 0.85rem; text-align: right;
      color: [muted];">PPTAgent</div>
    <div style="flex: 1; background: [highlight_background]; border-radius: 4px;
      height: 30px; position: relative;">
      <div style="width: 67.3%; height: 100%; background: [muted];
        border-radius: 4px; display: flex; align-items: center; padding: 0 10px;">
        <span style="color: white; font-size: 0.78rem;">67.30%</span>
      </div>
    </div>
  </div>
  <!-- Add all baselines from key_data -->
</div>
```

### Two-Column Contrast
```html
<div style="display: flex; gap: 2rem; align-items: flex-start; margin-top: 0.8rem;">
  <div style="flex: 1; padding: 1.2rem; background: [highlight_background];
    border-radius: 8px; border-top: 3px solid [accent];">
    <div style="font-weight: 700; color: [primary]; margin-bottom: 0.7rem;
      font-size: 0.95rem;">SlideTailor</div>
    <!-- right side content -->
  </div>
  <div style="flex: 1; padding: 1.2rem; background: [background];
    border-radius: 8px; border-top: 3px solid [muted];">
    <div style="font-weight: 700; color: [muted]; margin-bottom: 0.7rem;
      font-size: 0.95rem;">Prior Systems</div>
    <!-- left side content -->
  </div>
</div>
```

### Highlighted Table Row (best method emphasis)
When rendering a table with `highlighted_table` transform, apply to best row:
```html
<!-- Headline number above table -->
<div style="text-align: right; margin-bottom: 0.6rem;">
  <span style="font-size: 1.5rem; font-weight: 700; color: [primary];">75.80%</span>
  <span style="font-size: 0.85rem; color: [muted]; margin-left: 0.5rem;">overall (best)</span>
</div>
<!-- In the table: -->
<tr style="background: [highlight_background];">
  <td style="color: [primary]; font-weight: 700;">SlideTailor (Ours)</td>
  <td style="color: [primary]; font-weight: 700;">75.80</td>
  <!-- remaining cells in text_primary -->
</tr>
```

---

## Image Asset Handling

### USE_AS_IS — Compositional Assessment
After resolving via copy_asset_to_slide, make ONE brief read of the image:

| Image character | Template | Annotation bullets |
|---|---|---|
| Complex architecture / flow | full_image or content_image_* | 0-2, point at key components |
| Dense chart with many labels | full_image or content_image_* | 1-2 max |
| Clean, simple figure | content_image_right or _left | 3-4 annotation bullets |
| Wide landscape | full_image | Title only or 1 caption |
| Tall portrait | content_image_left or _right | 3-4 in wider column |
| Small / icon-sized | content_image_* | 4-5, image supports text |

Annotation bullets are LABELS pointing at figure parts, not summaries.
Keep each ≤ 8 words. The figure carries the content; bullets are signposts.

### TRANSFORM — Build Visual Alternative
Use `asset_transform` target and data from `narrative_direction` / `key_data`:
- `metric_cards` → metric card grid with numbers from key_data
- `html_bar_chart` → horizontal bar chart from comparison data
- `highlighted_table` → reconstructed table with accent styling
- `simplified_table` → table with non-essential columns removed
- `two_column_comparison` → side-by-side contrast panels

### DESCRIBE — Text/Visual Only
No asset. Build from narrative_direction and key_data using custom_html forms.

### Missing Image (asset file not found)
1. Do NOT render a grey placeholder
2. Switch to content_text
3. Build metric cards or callout from key_data instead
4. The slide should look designed, not broken

---

## Table Transformation Guide

| Table content | Best form | Template |
|---|---|---|
| 2-4 headline metrics | Metric card grid | content_text |
| Method vs baselines (≤ 5 rows) | Highlighted table + headline callout | table_slide |
| Method vs baselines (> 5 rows) | Bar chart or top-3 metric cards | content_text |
| Ablation study | Highlighted table (removed component emphasis) | table_slide |
| Dataset statistics | Compact metric cards | content_text |
| Dense numbers grid | Colour-coded / heatmap table | table_slide |

When showing a full table:
- Bold + accent-colour the winning numbers
- Add a subtle highlight_background tint to the paper's method row
- Reduce font size for dense tables (0.85rem acceptable)
- Add a standalone headline number above the table as visual anchor

---

## Template-Specific Rules

### title_slide
- Paper title at h1_size. Authors + venue as subtitle.
- If key_data has a standout number, add it as a styled accent element below subtitle:
  inline-block, highlight_background fill, left accent border, metric_size number.
- No bullets. No body image.

### content_text
- Most flexible: metric cards, callout boxes, bar charts, or bullet list
- When custom_html present: limit bullets to 0-2 — visual form does the work
- Bullet fallback: max 5, ≤ 12 words each

### content_image_right / content_image_left
- Image MUST be resolved and verified to exist
- Bullets = annotation labels only: ≤ 8 words, max 4
- No valid image → switch to content_text + custom_html from key_data

### table_slide
- USE_AS_IS: resolve_asset → read .html → pass as table_html
- highlighted_table: reconstruct with accent styling, add headline callout above
- Max 2 context bullets

### equation_slide
- LaTeX string only. Template handles delimiters. Do NOT wrap in $.
- 2-3 bullets on terms or significance

### full_image
- Title ≤ 6 words (still a claim, just compressed)
- High quality images only — if unclear at slide scale, use content_image_* instead

### two_column
- col_left = our method / solution / after (accent border)
- col_right = prior work / problem / before (muted border)
- First array item in each column = column heading
- Max 4 items per column

### conclusion
- Title: central_message restated as impact claim (already set by research agent)
- 3 complete-sentence bullets from narrative_direction
- First bullet: central_message restated in impact terms
- key_data headline number as small styled callout if space permits
- No new information

---

## Consecutive Template Check

After every 3 slides generated, review the template sequence.
If 3 consecutive slides share the same template:
1. Look at the middle slide's visual_notes and key_data
2. Any numbers available → convert to metric cards (content_text + custom_html)
3. Any comparison → convert to two_column
4. Any figure available → convert to content_image_*
5. Apply override and continue

Template monotony is a generation failure. Fix it during generation, not editing.

---

## Speaker Notes

Use the `speaker_notes` from the outline as the base. Ensure every slide has:
- Main talking point (expanding the claim — not restating the slide)
- A supporting detail or number not visible on the slide
- Transition to next slide ("This brings us to...")
- Minimum 3 sentences, target 4-5

---

## Batch Generation Workflow

1. Read full slide_outline.json + design_tokens.json
2. For each slide: read brief → assess asset → select form → render key_data → generate HTML
3. quality_check every 5 slides
4. Fix all FAIL issues before next batch
5. After all slides: final quality gate on all paths

### quality_check FAIL responses
| Issue | Fix |
|---|---|
| Missing `<section>` wrapper | Regenerate — template failed |
| Missing speaker notes | Re-render with substantive notes from outline |
| Word count > 400 | Reduce content, move to notes, or split slide |
| Image not found | Switch to content_text, build visual from key_data |
| Empty table_html | Build metric cards or summary callout instead |

---

## Output Summary

Return to orchestrator (≤ 300 words):
1. Total slides generated and section breakdown
2. Visual forms used: metric cards, callouts, bar charts, two-column, annotated figures, tables
3. key_data rendering — how critical numbers were displayed on each data-heavy slide
4. Template overrides vs outline suggestion and why
5. Asset transformations applied
6. Any content splits performed
7. FAIL issues and resolution
8. Remaining WARN items
Do NOT return raw HTML.