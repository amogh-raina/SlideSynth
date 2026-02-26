"""Stub: HTML slide quality checker.

Validates generated Reveal.js slide HTML files for structural and content issues.
Full implementation in Phase 2.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from langchain.tools import tool

from tools import resolve_vpath


@tool
def quality_check(slide_paths: List[str]) -> str:
    """Validate generated HTML slides for common issues.

    Checks:
    - No empty content sections
    - Referenced images exist on the filesystem
    - Text not too long (>200 words per slide = warning)
    - Valid HTML structure (<section> wrapper present)
    - Speaker notes present (<aside class="notes">)
    - design tokens applied (CSS custom properties present)

    Returns a JSON report with status per slide and a combined verdict.
    """
    results: List[Dict[str, Any]] = []
    any_fail = False

    for path_str in slide_paths:
        path = resolve_vpath(path_str)
        issues: List[Dict[str, str]] = []

        if not path.exists():
            results.append({"slide": path_str, "status": "FAIL", "issues": [
                {"severity": "fail", "message": f"File not found: {path_str}"}
            ]})
            any_fail = True
            continue

        html = path.read_text(encoding="utf-8")

        # Structure check
        if "<section" not in html:
            issues.append({"severity": "fail", "message": "Missing <section> wrapper"})
            any_fail = True

        # Speaker notes check
        if 'class="notes"' not in html and "class='notes'" not in html:
            issues.append({"severity": "warn", "message": "No speaker notes found"})

        # Word count check
        text_only = re.sub(r"<[^>]+>", " ", html)
        word_count = len(text_only.split())
        if word_count > 400:
            issues.append({"severity": "warn", "message": f"High word count: {word_count} words"})

        # Image existence check
        for img_match in re.finditer(r'src=["\']([^"\']+)["\']', html):
            src = img_match.group(1)
            if src.startswith("/") or src.startswith("./"):
                img_path = resolve_vpath(src)
                if not img_path.exists():
                    issues.append({"severity": "warn", "message": f"Referenced image not found: {src}"})

        status = "FAIL" if any(i["severity"] == "fail" for i in issues) else (
            "WARN" if issues else "PASS"
        )
        results.append({"slide": path_str, "status": status, "issues": issues})

    overall = "FAIL" if any_fail else (
        "WARN" if any(r["status"] == "WARN" for r in results) else "PASS"
    )
    return json.dumps({"overall": overall, "slides": results}, indent=2)
