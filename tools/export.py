"""Presentation export utilities.

Exports Reveal.js HTML to PDF via Playwright.
Full implementation in Phase 4.
"""

from __future__ import annotations

from pathlib import Path

from langchain.tools import tool

from tools import resolve_vpath


@tool
def export_to_pdf(
    presentation_path: str = "/presentation.html",
    output_path: str = "/exports/presentation.pdf",
) -> str:
    """Export a Reveal.js presentation HTML file to PDF using Playwright.

    Launches a headless Chromium browser, loads the local HTML file, appends
    Reveal.js print-pdf query param, and saves each slide as a PDF page.

    Args:
        presentation_path: Absolute path to the presentation.html file.
        output_path: Absolute path where the PDF should be written.

    Returns:
        Confirmation message with output path, or an error string.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return (
            "ERROR: playwright is not installed. "
            "Run: uv add playwright && playwright install chromium"
        )

    src = resolve_vpath(presentation_path)
    if not src.exists():
        return f"ERROR: presentation file not found: {presentation_path}"

    out = resolve_vpath(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    file_url = f"file://{src.resolve()}?print-pdf"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(file_url, wait_until="networkidle")
        # Give Reveal.js time to lay out
        page.wait_for_timeout(2000)
        page.pdf(
            path=str(out),
            format="A4",
            landscape=True,
            print_background=True,
        )
        browser.close()

    return f"OK: PDF exported to {output_path}"
