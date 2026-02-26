"""Lightweight structural integrity checks for slide plans.

Only checks two deterministic, non-semantic rules that are provably correct
without LLM reasoning and prevent downstream tool crashes:

1. **Asset ID integrity** — every asset referenced in the outline exists in
   the manifest.  A missing ID means the generator will fail to copy the file.
2. **Figure/table separation** — no single slide references both a figure and
   a table, which violates the template layout constraint.

Semantic evaluation (coverage, narrative flow, redundancy, PMRC arc) is handled
by the **verifier subagent**, not this tool.

This tool is NOT wired into the main pipeline — it exists as an optional
utility that can be called manually or integrated in the future if needed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from langchain.tools import tool

from tools import resolve_vpath


@tool
def verify_plan(
    outline_path: str = "/docs/slide_outline.json",
    manifest_path: str = "/docs/assets_manifest.json",
) -> str:
    """Run fast structural integrity checks on a slide outline.

    Only two deterministic checks (no LLM calls):
    1. Asset ID integrity — every asset referenced in the outline exists in the manifest.
    2. Figure/table separation — no slide references both a figure and a table.

    Args:
        outline_path: Virtual path to slide_outline.json.
        manifest_path: Virtual path to assets_manifest.json.

    Returns JSON: {"status": "PASS"|"FAIL", "issues": [...]}
    """
    issues: List[Dict[str, str]] = []

    # ── Load outline ─────────────────────────────────────────────────────
    outline_p = resolve_vpath(outline_path)
    if not outline_p.exists():
        return json.dumps({
            "status": "FAIL",
            "issues": [{"severity": "fail", "message": f"Outline not found: {outline_path}"}],
        })

    raw = json.loads(outline_p.read_text())
    slides: List[Dict[str, Any]] = (
        raw if isinstance(raw, list)
        else raw.get("slides", []) if isinstance(raw, dict)
        else []
    )

    if not slides:
        return json.dumps({
            "status": "FAIL",
            "issues": [{"severity": "fail", "message": "Outline has no slides"}],
        })

    # ── Load manifest (build asset-type sets) ────────────────────────────
    manifest_ids: set[str] = set()
    figure_ids: set[str] = set()
    table_ids: set[str] = set()

    manifest_p = resolve_vpath(manifest_path)
    if manifest_p.exists():
        manifest = json.loads(manifest_p.read_text())
        for key in ("images", "figures"):
            for item in manifest.get(key, []):
                aid = item.get("id", "")
                if aid:
                    manifest_ids.add(aid)
                    figure_ids.add(aid)
        for item in manifest.get("tables", []):
            aid = item.get("id", "")
            if aid:
                manifest_ids.add(aid)
                table_ids.add(aid)
        for item in manifest.get("equations", []):
            aid = item.get("id", "")
            if aid:
                manifest_ids.add(aid)

    # ── Check 1: Asset ID integrity ──────────────────────────────────────
    for slide in slides:
        n = slide.get("slide_number", slide.get("number", "?"))
        for asset_id in slide.get("assets", []):
            if asset_id and asset_id not in manifest_ids:
                issues.append({
                    "severity": "fail",
                    "message": f"Slide {n}: asset '{asset_id}' not found in manifest",
                })

    # ── Check 2: Figure/table separation ─────────────────────────────────
    for slide in slides:
        n = slide.get("slide_number", slide.get("number", "?"))
        assets = slide.get("assets", [])
        has_figure = any(a in figure_ids for a in assets)
        has_table = any(a in table_ids for a in assets)
        if has_figure and has_table:
            issues.append({
                "severity": "fail",
                "message": (
                    f"Slide {n}: references both a figure and a table — "
                    "must be on separate slides (template layout constraint)"
                ),
            })

    # ── Result ───────────────────────────────────────────────────────────
    status = "FAIL" if issues else "PASS"
    return json.dumps({"status": status, "total_slides": len(slides), "issues": issues}, indent=2)
