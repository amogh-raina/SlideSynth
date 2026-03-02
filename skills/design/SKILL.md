---
name: design
description: Visual design guidelines for academic presentations. Covers colour palettes, typography, composition principles, information hierarchy, accessibility, and professional-grade visual language. Explicitly supports metric cards, callout boxes, highlighted tables, and two-column contrasts as primary content forms. Supports both option presentation and final token generation.
---

# Visual Design Skill

## Purpose

Translate the paper's domain, tone, and audience into a `design_tokens.json`
that produces visually compelling, distinctive, and professional slides.

**Critical context:** Slides in this system are NOT primarily bullet lists.
They are built around metric cards, large callouts, highlighted tables,
annotated figures, and two-column contrasts. Your colour system must make
these content forms feel polished and intentional — they will appear on
the majority of slides and carry most of the visual identity.

Think like a premium design publication, not a conference template.

## Design Philosophy

**Form follows function, but form should also INSPIRE.**

The visual language should:
- Make metric cards and callouts feel like designed data visualisations, not HTML divs
- Create a recognisable identity that carries across all content forms
- Use colour semantically — accent means "important", not just "colourful"
- Stand out from the 5 generic decks shown before this one at the conference

Don't default to "navy + white + Inter" every time. Each paper has a unique
character — the design should reflect it.

---

## Understanding the Content Forms You Are Designing For

Before selecting any colour, understand what will actually appear on slides:

### Metric Cards
Large number (2-3rem, bold) + short label + context line, arranged in a 2-4
column grid. This is the primary way key results are shown.
- Background: `highlight_background` (very light tint)
- Border: left accent bar in `accent` colour, or full border in `accent`
- Number: `primary` colour at `metric_size`
- Label: `muted` colour at `metric_label` size
- Context: `success` or `error` for positive/negative comparisons

**Design test:** Do your `primary`, `accent`, and `highlight_background`
look intentional together on a card? Put them in your head: light tinted
card → accent border → large bold number in primary. Is this striking or muddy?

### Callout / Highlight Boxes
A key insight or finding set apart visually with a left border accent and
tinted background. Appears on results, method, and conclusion slides.
- Background: `highlight_background`
- Left border: 4px solid `accent`
- Text: `text_primary` with optional `primary` coloured label

### Highlighted Results Tables
Full comparison table with the paper's method row highlighted.
- Best method row: background in `highlight_background`, text bold
- Best result cells: `primary` or `accent` coloured text
- Table header: `primary` background with white text
- Runner-up rows: standard alternating `background` tint

### Two-Column Contrasts
Side-by-side panels separated by a divider. Used for before/after,
our method vs prior work, problem vs solution.
- Panel separation: `divider_color` vertical line or gap
- Column headers: `primary` for "our side", `muted` for "their side"
- Content: `text_primary` for both columns

### Large Standalone Statistics
A single number (e.g., "81.63%") displayed prominently, often above or
beside a table, acting as the visual anchor for a results slide.
- Number: `primary` at 3rem+ bold
- Context label: `muted` at body size below the number

### Annotated Figure Slides
Figure takes 50-60% of the slide. Short annotation bullets (2-3) point
at specific parts of the figure.
- Annotation bullets use square or dash markers in `accent`
- Figure sits on `background` with subtle `divider_color` border/shadow

---

## Colour System Architecture

### Primary Palette Selection

Go beyond basic domain mapping. Consider the paper's SPECIFIC character:

| Factor | Consideration |
|---|---|
| Paper's tone | Is it bold & provocative or measured & careful? |
| Key imagery | Do the paper's figures have their own colour palette? Match it. |
| Venue culture | NeurIPS is modern; Nature is conservative; CHI is creative |
| Audience mood | Energetic workshop vs. formal plenary vs. tutorial |
| Uniqueness | Would this palette be distinguishable from the 5 talks before it? |
| Data density | Many metric cards → accent colour will be very visible, choose carefully |

### Domain-Inspired Starting Points (NOT rigid rules)

| Domain | Palette Direction | Rationale |
|---|---|---|
| CS / ML / AI | Deep charcoal + teal accent | Modern, avoids overused navy |
| Biology / Medicine | Forest green + warm cream + terracotta accent | Natural, organic, grounded |
| Physics / Math | Near-black + gold or burnt orange accent | Elegant, precise, classical |
| Social Science / HCI | Purple + dusty rose + muted teal | Creative, human-centered |
| NLP / Language | Dark teal + warm amber accent | Intellectual, communicative |
| Vision / Graphics | Deep slate + coral or magenta accent | Visual, bold, distinctive |
| Systems / Engineering | Charcoal + copper/rust accent | Industrial, confident |

These are exploration starting points, not templates to copy verbatim.

### Colour Roles

```
primary            — Headings, table headers, accent bars, large metric numbers
primary_dark       — 10-15% darker than primary — hover states, strong emphasis
primary_light      — 10-15% lighter than primary — subtle accents

secondary          — Different hue family from primary. Bullet markers, dividers,
                     callout labels, supporting elements.
secondary_light    — Lighter variant of secondary

accent             — The most important colour choice. Appears on:
                     metric card left borders, callout left borders,
                     highlighted table row backgrounds, bullet markers,
                     data emphasis. Must POP against highlight_background.
accent_light       — Lighter variant for hover/secondary accent use

highlight          — Warm accent for card backgrounds and emphasis fills
highlight_background — Very light tint (>= 85% lighter than accent) for:
                     metric card backgrounds, callout fills, key insight boxes.
                     The audience sees this colour on every data-heavy slide.

background         — Slide background (always near-white, never #ffffff)
text_primary       — Main body text (>= 7:1 contrast on background)
text_secondary     — Subheadings, column headers (>= 4.5:1)
muted              — Captions, metric labels, metadata (>= 3:1)
code_background    — For code blocks or equation backgrounds
divider_color      — Subtle lines, panel separators, figure borders

success            — Green: positive results, gains, our method wins
warning            — Amber: caution, marginal results
error              — Red: negative results, baseline comparisons
```

### Contrast Requirements (WCAG AA)

| Colour Role | Min Contrast vs Background |
|---|---|
| text_primary | >= 7:1 (AAA preferred) |
| text_secondary | >= 4.5:1 (AA required) |
| muted | >= 3:1 (acceptable for captions/labels) |
| primary headings | >= 4.5:1 |
| accent vs highlight_background | >= 3:1 (text on cards) |

### Background Philosophy

- NEVER use pure `#ffffff` — harsh under projector lighting
- Use a very slight warm or cool tint: `#fafbfc`, `#faf9f7`, `#f8fafc`
- Cool primary → cool-tinted background (`#f8fafc`)
- Warm primary → warm-tinted background (`#faf9f7`)
- The tint reinforces the palette temperature throughout

### highlight_background Is Critical

This colour appears as the fill of every metric card and callout box.
It will be visible on roughly 60-70% of slides. Rules:

- Must be >= 85% lighter than `accent` — cards need to feel airy, not heavy
- Must complement `primary` — number (in primary) sits on this background
- Must contrast enough with `accent` border for the border to read clearly
- Good test: does it look like intentional tinted paper, or like a faded mistake?

Example: accent = `#0891b2` (teal) → highlight_background = `#f0f9ff` (near-white blue tint)

### Colour Harmony Rules

- Primary and secondary must be from different hue families
- Accent should have high saturation — it needs to carry visual weight at small sizes
- Never use more than 3 saturated colours on one slide
- Use opacity variants (10-15%) for highlight backgrounds rather than flat light tints
  when possible — they stay in harmony as the palette shifts
- Ensure `success` (green) reads differently from `primary` — if primary IS green,
  use a warm teal success instead

---

## Typography System

### Font Selection Philosophy

Pick fonts with CHARACTER that match the paper's personality while maintaining
legibility at presentation distances. Every font choice should be justifiable.

### Heading Font Criteria
- Must be a Google Font available via CDN
- Sans-serif primary (geometric or humanist)
- Weight range 600-800 for visual hierarchy
- Must have distinctive character — avoid completely generic choices

**Recommended heading fonts by feel:**
| Feel | Fonts |
|---|---|
| Modern & clean | Inter, Plus Jakarta Sans, Outfit |
| Geometric & precise | DM Sans, Sora, Manrope |
| Friendly & accessible | Nunito, Rubik, Quicksand |
| Editorial & refined | Playfair Display (serif, use selectively) |
| Technical & structured | Space Grotesk, JetBrains Mono (CS/code papers) |

### Body Font Criteria
- High x-height for legibility at presentation distances
- Regular (400) weight for body, Medium (500) for emphasis
- Must pair well with selected heading font

Recommended: Inter, Lato, Source Sans 3, Nunito, Open Sans, IBM Plex Sans

### Font Pairing Guide

| Heading | Body | Feel |
|---|---|---|
| Plus Jakarta Sans | Inter | Modern professional |
| Sora | Lato | Geometric meets humanist |
| Space Grotesk | Source Sans 3 | Technical precision |
| DM Sans | Nunito | Warm academic |
| Outfit | IBM Plex Sans | Clean authority |
| Playfair Display | Inter | Editorial elegance |

### Font Size System

Design for Reveal.js 960×700 viewport:

| Element | Size Range | Notes |
|---|---|---|
| Title slide H1 | 2.6rem - 3.2rem | Larger — it's alone on the slide |
| Slide headings H2 | 1.6rem - 2.0rem | Must leave room for content below |
| Bullet / body text | 1.0rem - 1.2rem | Legibility from back of room |
| Metric numbers | 2.0rem - 3.0rem | Large callout numbers |
| Metric labels | 0.8rem - 0.9rem | Below the large number |
| Caption / metadata | 0.8rem - 0.9rem | Muted colour compensates |
| Speaker notes | 0.8rem | Not visible to audience |

---

## Title Slide Design

The title slide is the audience's first impression and should be visually
distinctive — not just "title + authors in plain text."

Each design option must describe a title slide treatment. Options include:

**Accent bar approach:** A short coloured horizontal bar (3-5px, `accent` or
`primary`) above the title — creates a subtle brand marker.

**Background tint approach:** A very faint full-slide tint using
`highlight_background` instead of pure white — warms the stage.

**Metric callout approach:** If `key_numbers` contains a standout number,
display it as a styled element below the authors: large number in `primary`,
label in `muted`. Creates an immediate hook.

**Geometric accent approach:** A decorative element in `accent` or `primary`
(e.g., a coloured rectangle or gradient bar) that frames the title area.

**Rule:** The title slide should use at most ONE of these. Restraint is key.
The rest of the deck should feel like a natural extension of the title slide's
visual language.

---

## Design Option Differentiation

When presenting 3 options, ensure GENUINE variety across all axes:

### Differentiation Axes
1. **Hue family** — Not shade variations; the entire colour story must differ
2. **Personality** — Each option should evoke a different emotional response
3. **Typography character** — Pair different font personalities
4. **Energy level** — One option should feel calm/measured, one confident,
   one bold/energetic

### Option Naming (evocative, not labels)
Name options to capture the mood:
- "Scholarly Precision" — charcoal + sage + measured serif accents
- "Innovation Forward" — teal + coral + geometric sans
- "Clean Authority" — deep navy + gold + classic sans
- "Digital Nature" — forest green + warm amber + rounded sans
- "Critical Edge" — near-black + electric indigo + modern geometric

### Anti-Patterns
- Three shades of blue → not different enough; lazy differentiation
- Same font pair with different colours → typography dimension wasted
- All three options "safe" → at least one must be genuinely bold
- All three look like academic conference templates → wrong reference frame
- Accent colour that reads as "just another shade of primary" → accent must contrast

---

## Composition & Layout Principles

### Information Hierarchy

Every slide must have a clear visual hierarchy:
1. **Primary** — The ONE element the audience notices first (heading or hero number)
2. **Secondary** — Supporting content (metric grid, figure, table)
3. **Tertiary** — Context and metadata (captions, sources, slide number)

Use size, weight, colour, AND position to establish hierarchy — not font size alone.

### Spatial Composition Rules

- **Intentional whitespace** — breathing room is a design choice, not waste
- **Alignment on consistent margins** — all content snaps to the same left margin
- **Breathing room around visuals** — images and cards need margin, not zero gap

### Spacing Tokens for Visual Forms

```
card_gap:          1.5rem   — gap between metric cards in a grid
card_padding:      1.5rem 1rem  — internal padding of metric cards
card_border_radius: 10px    — rounded corners for cards
callout_padding:   1.2rem 1.5rem  — highlight box internal padding
image_margin:      16px     — breathing room around figures
```

These are the spacings that appear most in generated slides. Set them
deliberately — they define the feel of the data visualisation.

### Visual Accent Elements Enabled by Your Tokens

Well-set tokens enable these without custom styling:
- **Accent bars** — 3-5px `primary` or `accent` lines above section headings
- **Metric card grids** — `highlight_background` fill + `accent` left border
- **Callout boxes** — `highlight_background` fill + `accent` 4px left border
- **Table highlights** — `highlight_background` row + `primary` bold text
- **Success/error indicators** — `success`/`error` in comparison tables

---

## Design Token Full Schema

```json
{
  "colors": {
    "primary":              "#hex",
    "primary_dark":         "#hex (10-15% darker)",
    "primary_light":        "#hex (10-15% lighter)",
    "secondary":            "#hex (different hue family)",
    "secondary_light":      "#hex",
    "accent":               "#hex (high saturation, POPs against highlight_background)",
    "accent_light":         "#hex",
    "highlight":            "#hex (warm, for emphasis fills)",
    "highlight_background": "#hex (very light, >= 85% lighter than accent)",
    "background":           "#hex (near-white, NOT #ffffff)",
    "text_primary":         "#hex (>= 7:1 on background)",
    "text_secondary":       "#hex (>= 4.5:1 on background)",
    "muted":                "#hex (>= 3:1, for captions and labels)",
    "code_background":      "#hex",
    "divider_color":        "#hex",
    "success":              "#hex",
    "warning":              "#hex",
    "error":                "#hex"
  },
  "fonts": {
    "heading": "Google Font Name",
    "body":    "Google Font Name"
  },
  "spacing": {
    "slide_padding":     "40px 60px",
    "bullet_gap":        "0.7em",
    "image_max_width":   "55%",
    "content_max_width": "85%",
    "card_gap":          "1.5rem",
    "card_padding":      "1.5rem 1rem",
    "card_border_radius":"10px",
    "callout_padding":   "1.2rem 1.5rem",
    "image_margin":      "16px"
  },
  "typography": {
    "h1_size":      "2.8rem",
    "h2_size":      "1.8rem",
    "body_size":    "1.05rem",
    "bullet_size":  "1.05rem",
    "metric_size":  "2.4rem",
    "metric_label": "0.85rem",
    "caption_size": "0.85rem",
    "notes_size":   "0.8rem",
    "h1_weight":    "700",
    "h2_weight":    "700",
    "metric_weight":"700"
  },
  "layout": {
    "image_max_height":      "400px",
    "table_max_width":       "90%",
    "table_overflow":        "auto",
    "content_max_height":    "520px",
    "metric_card_min_width": "140px"
  }
}
```

---

## Design Rationale (required after Mode B)

Write 3-4 sentences covering:
1. Why this primary colour suits the paper's specific character (not just its domain)
2. Why this font pair matches the content tone
3. How `accent` + `highlight_background` work together for metric cards and callouts
4. How the title slide will make a distinctive first impression with this system

---

## Reveal.js Layout Awareness

Reveal.js uses a fixed **960×700 logical viewport**. With `slide_padding` of
`40px 60px`, the usable content area is ~840×620px.

### Token Value Guardrails
- `slide_padding`: >= `40px 60px` — content must never touch slide edges
- `image_max_width`: <= 55% for image+text, <= 90% for full_image slides
- Font ceilings: h1 ≤ 3.2rem, h2 ≤ 2.2rem, body/bullet ≤ 1.3rem, metric ≤ 3rem
- `highlight_background` must be >= 85% lighter than `accent`
- `accent` must pass 3:1 contrast vs `highlight_background`

Templates enforce overflow protection using these tokens as CSS variables.
The design agent sets the values; the generator and templates enforce the bounds.