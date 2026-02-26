"""HTML slide generation via Jinja2 templates.

Renders slide content + design tokens into Reveal.js slide HTML.
Full implementation in Phase 2.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from langchain.tools import tool

from tools import resolve_vpath


TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


@tool
def generate_slide_html(
    slide_number: int,
    template_name: str,
    content: str,
    design_tokens: str,
    output_path: str,
) -> str:
    """Render a Jinja2 slide template with content and design tokens into HTML.

    Args:
        slide_number: Slide number (1-indexed).
        template_name: Template filename without .html extension
                       (title_slide, content_text, content_image_right, etc.)
        content: JSON string with keys: title, bullets, image_path, speaker_notes,
                 central_message, assets (list of paths).
        design_tokens: JSON string of CSS custom properties from design_tokens.json.
        output_path: Absolute path where the slide HTML file should be written.

    Returns:
        Confirmation string with file path and any warnings.
    """
    try:
        from jinja2 import Environment, FileSystemLoader, TemplateNotFound
    except ImportError:
        return "ERROR: jinja2 is not installed. Run: uv add jinja2"

    content_data: Dict[str, Any] = json.loads(content) if isinstance(content, str) else content
    tokens: Dict[str, Any] = json.loads(design_tokens) if isinstance(design_tokens, str) else design_tokens

    # ── Normalize tokens so templates always find the keys they expect ──
    # Templates use: tokens.fonts.heading, tokens.fonts.body
    # Design agent may write: tokens.typography.title_font, tokens.typography.body_font
    typo = tokens.get("typography") or {}
    fonts = tokens.get("fonts") or {}
    tokens["fonts"] = {
        "heading": fonts.get("heading") or typo.get("title_font") or typo.get("heading_font") or "Inter",
        "body": fonts.get("body") or typo.get("body_font") or "Inter",
    }
    # Ensure colors exists with safe defaults for templates
    if not tokens.get("colors"):
        tokens["colors"] = {}
    # Ensure spacing exists
    if not tokens.get("spacing"):
        tokens["spacing"] = {}
    # Ensure typography exists (some templates reference it)
    if not tokens.get("typography"):
        tokens["typography"] = {}

    template_file = f"{template_name}.html"
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    try:
        template = env.get_template(template_file)
    except TemplateNotFound:
        return f"ERROR: Template '{template_file}' not found in {TEMPLATES_DIR}"

    rendered = template.render(
        slide_number=slide_number,
        tokens=tokens,
        **content_data,
    )

    out_path = resolve_vpath(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered, encoding="utf-8")
    return f"OK: Slide {slide_number} written to {output_path} using template '{template_name}'"


@tool
def combine_presentation(
    slides_dir: str = "/slides",
    output_path: str = "/presentation.html",
    design_tokens_path: str = "/design/design_tokens.json",
) -> str:
    """Combine individual slide HTML files into a single Reveal.js presentation.

    Reads all slide{N:02d}.html files from slides_dir in order, wraps them in the
    Reveal.js scaffold with navigation controls, and writes the final presentation
    to output_path.

    Returns the output path and total slide count.
    """
    slides_path = resolve_vpath(slides_dir)
    if not slides_path.exists():
        return f"ERROR: slides directory not found: {slides_dir}"

    slide_files = sorted(slides_path.glob("slide*.html"))
    if not slide_files:
        return f"ERROR: No slide*.html files found in {slides_dir}"

    # Load design tokens for theme colours
    tokens: Dict[str, Any] = {}
    tokens_p = resolve_vpath(design_tokens_path)
    if tokens_p.exists():
        tokens = json.loads(tokens_p.read_text())

    colors = tokens.get("colors", {})
    fonts = tokens.get("fonts", {})
    primary = colors.get("primary", "#1e3a8a")
    bg = colors.get("background", "#ffffff")
    heading_font = fonts.get("heading", "Inter")
    body_font = fonts.get("body", "Inter")

    # Build CSS custom properties block
    css_vars = "\n".join(
        f"  --{k}: {v};" for k, v in colors.items()
    )

    sections: list[str] = []
    for sf in slide_files:
        sections.append(sf.read_text(encoding="utf-8"))

    all_sections = "\n\n".join(sections)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SlideSynth Presentation</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/theme/white.css">
  <style>
    :root {{
{css_vars}
      --heading-font: '{heading_font}', sans-serif;
      --body-font: '{body_font}', sans-serif;
    }}
    .reveal {{ font-family: var(--body-font); background: {bg}; }}
    .reveal h1, .reveal h2, .reveal h3 {{ font-family: var(--heading-font); color: {primary}; }}
  </style>
</head>
<body>
  <div class="reveal">
    <div class="slides">
{all_sections}
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.js"></script>
  <script>
    Reveal.initialize({{
      hash: true,
      slideNumber: true,
      plugins: []
    }});
  </script>
</body>
</html>"""

    out = resolve_vpath(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return f"OK: presentation.html written to {output_path} ({len(slide_files)} slides)"


@tool
def switch_template(
    slide_path: str,
    new_template: str,
    design_tokens_path: str = "/design/design_tokens.json",
) -> str:
    """Re-render an existing slide HTML with a different template.

    Extracts title, bullets, assets, and speaker notes from the current slide
    HTML, then renders the new template with the same content and design tokens.
    Overwrites the slide file in place.

    Args:
        slide_path: Absolute path to the slide HTML file to relayout.
        new_template: Target template name (content_text, content_image_right, etc.)
        design_tokens_path: Path to design_tokens.json

    Returns:
        Confirmation string with old and new template names.
    """
    import re

    path = resolve_vpath(slide_path)
    if not path.exists():
        return f"ERROR: Slide not found: {slide_path}"

    html = path.read_text(encoding="utf-8")

    # Heuristic content extraction from existing slide HTML
    title_match = re.search(r"<h[12][^>]*>(.*?)</h[12]>", html, re.S)
    title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip() if title_match else ""

    bullets = re.findall(r"<li[^>]*>(.*?)</li>", html, re.S)
    bullets_clean = [re.sub(r"<[^>]+>", "", b).strip() for b in bullets]

    notes_match = re.search(r'<aside[^>]*class=["\']notes["\'][^>]*>(.*?)</aside>', html, re.S)
    speaker_notes = re.sub(r"<[^>]+>", "", notes_match.group(1)).strip() if notes_match else ""

    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html)
    image_path = img_match.group(1) if img_match else ""

    # Extract slide number from filename
    num_match = re.search(r"slide(\d+)", path.stem)
    slide_number = int(num_match.group(1)) if num_match else 0

    content = json.dumps({
        "title": title,
        "bullets": bullets_clean,
        "image_path": image_path,
        "speaker_notes": speaker_notes,
    })

    tokens: Dict[str, Any] = {}
    tokens_p = resolve_vpath(design_tokens_path)
    if tokens_p.exists():
        tokens = json.loads(tokens_p.read_text())

    return generate_slide_html.invoke({
        "slide_number": slide_number,
        "template_name": new_template,
        "content": content,
        "design_tokens": json.dumps(tokens),
        "output_path": slide_path,
    })
