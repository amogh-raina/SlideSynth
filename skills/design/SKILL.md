---
name: design
description: Visual design guidelines for academic presentations. Covers colour theory, typography selection, spacing systems, domain-specific branding, and WCAG accessibility. Supports both option presentation and final token generation.
---

# Visual Design Skill

## Purpose

Translate the paper's domain, tone, and venue into a design_tokens.json that
the generator can use to produce visually consistent, professional slides.

## Domain Colour Palettes

| Domain | Recommended Primary | Feel |
|---|---|---|
| Computer Science / ML | #1e3a8a (navy) | Authoritative, technical |
| Biology / Medicine | #065f46 (deep green) | Natural, precise |
| Physics | #1c1917 (near-black) + #f59e0b accent | Elegant, rigorous |
| Social Science / HCI | #4c1d95 (purple) | Creative, humanistic |
| Engineering | #1e40af (blue) or #92400e (rust) | Industrial, confident |
| General / Mixed | #1e3a8a (navy) — safest default | — |

### Venue-Specific Recommendations
- **NeurIPS / ICML**: Clean, minimal, modern — navy or teal
- **CVPR / ICCV**: Slightly bolder — deeper blues, allow image-heavy layouts
- **ACL / EMNLP**: Classic academic — navy or dark green
- **CHI / UIST**: Allow more vibrant accents — purple, teal
- **Nature / Science**: Conservative — dark greys with one accent colour
- **Workshop / informal**: Can push towards bolder, friendlier palettes

## Colour System Rules

- **Background**: Always #ffffff or a very light tint (#f8fafc). Dark backgrounds hurt readability in lit rooms.
- **Text**: Must achieve WCAG AA contrast >= 4.5:1 against the background (use #111827 or #1f2937).
- **Primary**: Used for H1/H2 headings and key accents.
- **Secondary**: A complementary colour for bullets, icons, and dividers — should be harmonious but distinct.
- **Highlight**: A warm accent (#f59e0b, #ef4444) for call-outs and key terms. Use sparingly.
- **Muted**: A grey tone for speaker notes, captions, and secondary text (#6b7280).

Never use more than 3 colours prominently per slide.

## Contrast Check Formula

To verify contrast (you cannot see the screen, so estimate):
- Light background #ffffff + dark text #111827 -> contrast ~ 18:1 (PASS)
- #1e3a8a headings on #ffffff -> contrast ~ 8.5:1 (PASS)
- Light grey text #9ca3af on #ffffff -> contrast ~ 2.9:1 (FAIL — too low for body)

When in doubt, err darker for text and lighter for backgrounds.

## Typography Selection

### Heading Font Rules
- Must be a Google Font available via CDN
- Sans-serif only (serif fonts reduce legibility on projectors)
- Strong weight at 600-800 for visual hierarchy
- Recommended: Inter, Plus Jakarta Sans, DM Sans, Outfit, Sora

### Body Font Rules
- High x-height for legibility at small sizes
- Regular weight (400) for body, medium (500) for bullets
- Recommended: Inter, Lato, Source Sans 3, Nunito, Open Sans

### Font Pairing Guide
- **Same family**: Inter heading (700) + Inter body (400) — clean, unified
- **Complementary**: DM Sans heading + Source Sans body — geometric + humanist
- **High contrast**: Sora heading + Lato body — modern geometric + classic humanist

Heading and body may be the same font family — just use different weights.

## Font Size System

Design for a 1920x1080 slide rendered at 100% scale in Reveal.js:

| Element | Recommended Size |
|---|---|
| H1 (title slides) | 2.8rem - 3.2rem |
| H2 (slide headings) | 1.8rem - 2.2rem |
| Bullet text | 1.1rem - 1.3rem |
| Body text | 1.0rem - 1.15rem |
| Speaker notes | 0.85rem (greyed out) |

## Spacing System

- slide_padding: The inner padding of the <section> element. Default: 40px 60px.
- bullet_gap: Vertical gap between list items. Default: 0.6em.
- image_max_width: Maximum width of an embedded image. Default: 55%.

For text-heavy slides without images, image_max_width can be ignored.

## Design Option Differentiation

When presenting 3 options, ensure genuine variety:
- Vary HUE FAMILIES — not just shades of the same colour
- Example: Navy (cool) vs Forest Green (natural) vs Charcoal+Gold (warm)
- Each option should evoke a different emotional response
- All three must pass WCAG contrast requirements

### Option Naming
Name options descriptively — not just "Option A":
- "Academic Professional" (navy + serif-like sans)
- "Modern Minimal" (monochrome + geometric sans)
- "Swiss Design" (high contrast + Helvetica-style)

## Design Rationale

After writing the tokens JSON, write a short paragraph explaining:
1. Why you chose this primary colour for this domain
2. Why this font pair works for academic content
3. Any special choices made for this specific paper's venue or tone

This helps the editor agent understand the design intent when making adjustments.

## Layout Awareness

Reveal.js uses a fixed **960×700 logical viewport**. With `slide_padding` of
`40px 60px`, the usable content area is ~840×620px. The token values you set
directly affect whether content fits.

### Token Value Guardrails

- `slide_padding`: >= `40px 60px` (never let content touch edges)
- `image_max_width`: <= 55% for image+text layouts, <= 90% for full_image
- Font size ceilings: h1 ≤ 3.2rem, h2 ≤ 2.2rem, body/bullet ≤ 1.3rem

### Include a `layout` key in design_tokens.json

```json
"layout": {
  "image_max_height": "400px",
  "table_max_width": "90%",
  "table_overflow": "auto",
  "content_max_height": "520px"
}
```

The generator and Jinja2 templates consume these as CSS variables
(`--image-max-height`, `--table-max-width`, `--content-max-height`) for
overflow protection. The design agent only needs to set sensible values;
enforcement happens downstream.
```