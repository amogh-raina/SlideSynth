"""HTML slide generation via Jinja2 templates.

Renders slide content + design tokens into Reveal.js slide HTML.
Full implementation in Phase 2.
"""

from __future__ import annotations

import json
import re
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
        content: JSON string with slide content. Common keys: title, bullets (list),
                 image_path, speaker_notes, custom_html (primary vehicle for visual
                 forms: metric cards, bar charts, callouts, two-column panels),
                 table_html, equation, subtitle, col_left, col_right.
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
    colors = tokens["colors"]
    # Normalise extended colour tokens — ensure all template-used keys exist
    if not colors.get("accent"):
        colors["accent"] = colors.get("highlight", "#f59e0b")
    if not colors.get("highlight_background"):
        # Derive a light tint from accent or use a sensible default
        colors["highlight_background"] = colors.get("highlight", "#f0f4ff") + "18" if len(colors.get("highlight", "")) == 7 else "#f0f4ff"
    if not colors.get("divider_color"):
        colors["divider_color"] = colors.get("muted", "#e5e7eb")
    if not colors.get("code_background"):
        colors["code_background"] = "#f8fafc"
    if not colors.get("success"):
        colors["success"] = "#10b981"
    if not colors.get("warning"):
        colors["warning"] = "#f59e0b"
    if not colors.get("error"):
        colors["error"] = "#ef4444"
    # Ensure spacing exists
    if not tokens.get("spacing"):
        tokens["spacing"] = {}
    # Ensure typography exists (some templates reference it)
    if not tokens.get("typography"):
        tokens["typography"] = {}
    # Ensure layout exists
    if not tokens.get("layout"):
        tokens["layout"] = {}

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

    # ── Persist speaker notes to a separate JSON file ──────────────────
    notes_text = content_data.get("speaker_notes", "")
    if notes_text:
        notes_file = out_path.parent / "speaker_notes.json"
        existing: list[dict] = []
        if notes_file.exists():
            try:
                existing = json.loads(notes_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, ValueError):
                existing = []
        # Update or append entry for this slide number
        entry = {"slide": slide_number, "notes": notes_text}
        found = False
        for i, e in enumerate(existing):
            if e.get("slide") == slide_number:
                existing[i] = entry
                found = True
                break
        if not found:
            existing.append(entry)
        existing.sort(key=lambda e: e.get("slide", 0))
        notes_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")

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
    secondary = colors.get("secondary", "#3b82f6")
    accent = colors.get("accent", colors.get("highlight", "#f59e0b"))
    bg = colors.get("background", "#ffffff")
    text_color = colors.get("text", "#1f2937")
    heading_font = fonts.get("heading", "Inter")
    body_font = fonts.get("body", "Inter")

    # Build CSS custom properties block (all colours available as CSS vars)
    css_vars = "\n".join(
        f"  --{k}: {v};" for k, v in colors.items()
    )

    sections: list[str] = []
    for sf in slide_files:
        raw = sf.read_text(encoding="utf-8")
        # Rewrite relative asset paths so they resolve from the project root
        # (presentation.html lives one level above slides/)
        raw = re.sub(
            r'''(src\s*=\s*["'])(?!https?://|//|data:|slides/)''',
            r'\1slides/',
            raw
        )
        sections.append(raw)

    all_sections = "\n\n".join(sections)

    # ── Build speaker notes map (JSON + HTML fallback) ─────────────────
    notes_list: list[dict] = []
    notes_path = slides_path / "speaker_notes.json"
    if notes_path.exists():
        try:
            notes_list = json.loads(notes_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            notes_list = []

    notes_map: dict[int, str] = {e["slide"]: e["notes"] for e in notes_list if e.get("notes")}

    # Fallback: extract notes from <aside class="notes"> in each slide HTML
    for sf in slide_files:
        num_match = re.search(r"slide(\d+)", sf.stem)
        if not num_match:
            continue
        snum = int(num_match.group(1))
        if snum in notes_map:
            continue  # JSON already has notes for this slide
        html_text = sf.read_text(encoding="utf-8")
        aside_match = re.search(
            r'<aside[^>]*class=["\']notes["\'][^>]*>(.*?)</aside>',
            html_text, re.S
        )
        if aside_match:
            text = re.sub(r"<[^>]+>", "", aside_match.group(1)).strip()
            if text:
                notes_map[snum] = text

    # Rebuild the notes list sorted by slide number
    combined_notes = [{"slide": k, "notes": v} for k, v in sorted(notes_map.items())]
    notes_json_str = json.dumps(combined_notes, indent=2, ensure_ascii=False)

    # Also update the speaker_notes.json on disk with the merged data
    notes_path.write_text(notes_json_str, encoding="utf-8")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SlideSynth Presentation</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family={heading_font.replace(' ', '+')}:wght@400;600;700;800&family={body_font.replace(' ', '+')}:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/theme/white.css">
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" async></script>
  <style>
    :root {{
{css_vars}
      --heading-font: '{heading_font}', sans-serif;
      --body-font: '{body_font}', sans-serif;
    }}
    .reveal {{ font-family: var(--body-font); background: {bg}; }}
    .reveal h1, .reveal h2, .reveal h3 {{ font-family: var(--heading-font); color: {primary}; }}
    .reveal section {{ text-align: left; }}
    .reveal .slides section {{ padding: 0; }}
    .reveal .slide-number {{ color: {colors.get('muted', '#6b7280')}; font-size: 0.7rem; }}

    /* ── Speaker Notes Panel ─────────────────────────── */
    body {{ margin: 0; display: flex; height: 100vh; overflow: hidden; }}
    .ss-main {{ flex: 1; min-width: 0; position: relative; }}
    .ss-notes-panel {{
      width: 320px; flex-shrink: 0; background: #f8f9fa; border-left: 1px solid #e5e7eb;
      display: flex; flex-direction: column; font-family: var(--body-font);
      transition: width 0.2s ease;
    }}
    .ss-notes-panel.hidden {{ width: 0; overflow: hidden; border: none; }}
    .ss-notes-header {{
      padding: 12px 16px; font-size: 13px; font-weight: 600; color: #374151;
      border-bottom: 1px solid #e5e7eb; display: flex; align-items: center;
      justify-content: space-between; flex-shrink: 0;
    }}
    .ss-notes-body {{
      flex: 1; overflow-y: auto; padding: 16px; font-size: 14px;
      line-height: 1.65; color: #4b5563;
    }}
    .ss-notes-body .ss-no-notes {{ color: #9ca3af; font-style: italic; }}
    .ss-notes-toggle {{
      position: fixed; bottom: 16px; right: 16px; z-index: 100;
      width: 40px; height: 40px; border-radius: 50%; border: none;
      background: {primary}; color: #fff; font-size: 18px;
      cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.15);
      display: flex; align-items: center; justify-content: center;
      transition: background 0.15s;
    }}
    .ss-notes-toggle:hover {{ background: {secondary}; }}
    .ss-notes-toggle.panel-open {{ right: 336px; }}
  </style>
</head>
<body>
  <div class="ss-main">
    <div class="reveal">
      <div class="slides">
{all_sections}
      </div>
    </div>
  </div>

  <!-- Speaker Notes Side Panel -->
  <aside class="ss-notes-panel" id="ss-notes-panel">
    <div class="ss-notes-header">
      <span>Speaker Notes</span>
      <span id="ss-notes-slide" style="font-weight:400; color:#6b7280;"></span>
    </div>
    <div class="ss-notes-body" id="ss-notes-body">
      <span class="ss-no-notes">Navigate to a slide to see notes.</span>
    </div>
  </aside>

  <!-- Toggle button -->
  <button class="ss-notes-toggle panel-open" id="ss-notes-btn" title="Toggle speaker notes"
    onclick="toggleNotesPanel()">📝</button>

  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.js"></script>
  <script>
    // Speaker notes data (embedded at build time)
    const speakerNotes = {notes_json_str};

    const notesMap = {{}};
    speakerNotes.forEach(n => {{ notesMap[n.slide] = n.notes; }});

    Reveal.initialize({{
      hash: true,
      slideNumber: true,
      width: 960,
      height: 700,
      margin: 0,
      plugins: []
    }}).then(() => {{
      updateNotesPanel();
      Reveal.on('slidechanged', updateNotesPanel);
    }});

    function updateNotesPanel() {{
      const idx = Reveal.getState().indexh + 1;
      const body = document.getElementById('ss-notes-body');
      const label = document.getElementById('ss-notes-slide');
      label.textContent = 'Slide ' + idx;
      const notes = notesMap[idx];
      if (notes) {{
        body.innerHTML = '<p>' + notes.replace(/\\n\\n/g, '</p><p>').replace(/\\n/g, '<br>') + '</p>';
      }} else {{
        body.innerHTML = '<span class="ss-no-notes">No notes for this slide.</span>';
      }}
    }}

    function toggleNotesPanel() {{
      const panel = document.getElementById('ss-notes-panel');
      const btn = document.getElementById('ss-notes-btn');
      panel.classList.toggle('hidden');
      btn.classList.toggle('panel-open');
    }}
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

    # Extract custom_html if present
    custom_html_match = re.search(r'<div[^>]*class=["\']slide-custom-html["\'][^>]*>(.*?)</div>\s*(?=<aside|$)', html, re.S)
    custom_html = custom_html_match.group(1).strip() if custom_html_match else ""

    # Extract table_html if present
    table_html_match = re.search(r'<div[^>]*class=["\']slide-table-wrapper["\'][^>]*>.*?(<table.*?</table>)', html, re.S)
    table_html = table_html_match.group(1).strip() if table_html_match else ""

    # Extract slide number from filename
    num_match = re.search(r"slide(\d+)", path.stem)
    slide_number = int(num_match.group(1)) if num_match else 0

    content_dict = {
        "title": title,
        "bullets": bullets_clean,
        "image_path": image_path,
        "speaker_notes": speaker_notes,
    }
    if custom_html:
        content_dict["custom_html"] = custom_html
    if table_html:
        content_dict["table_html"] = table_html

    content = json.dumps(content_dict)

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
