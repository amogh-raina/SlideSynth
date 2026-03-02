"""Asset management utilities.

Resolves, copies, and validates media assets (images, tables) for slides.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from langchain.tools import tool

from tools import resolve_vpath, get_project_root


@tool
def resolve_asset(
    asset_id: str,
    manifest_path: str = "/docs/assets_manifest.json",
) -> str:
    """Resolve an asset ID to its absolute file path.

    Looks up the asset_id in the project's assets_manifest.json and returns
    the resolved absolute path.

    Args:
        asset_id: The unique asset identifier (e.g., "figure_1", "table_3").
        manifest_path: Virtual path to assets_manifest.json produced by parse_pdf.

    Returns:
        JSON with {"asset_id", "type", "path", "caption"} or an error string.
    """
    manifest_p = resolve_vpath(manifest_path)
    if not manifest_p.exists():
        return f"ERROR: manifest not found at {manifest_path}"

    manifest = json.loads(manifest_p.read_text())
    project_root = get_project_root() or str(manifest_p.parent.parent)

    # parse_pdf writes top-level "images" and "tables" keys
    all_assets: list = []
    for key in ("images", "tables", "figures", "equations", "assets"):
        all_assets.extend(manifest.get(key, []))

    for asset in all_assets:
        if asset.get("id") == asset_id or asset.get("filename") == asset_id:
            src_path = asset.get("path", "")
            abs_path = (Path(project_root) / src_path).resolve()
            asset_type = "image" if asset.get("id", "").startswith("fig") else "table"
            return json.dumps({
                "asset_id": asset_id,
                "type": asset.get("type", asset_type),
                "path": str(abs_path),
                "caption": asset.get("caption", ""),
                "exists": abs_path.exists(),
            }, indent=2)

    return f"ERROR: asset '{asset_id}' not found in manifest"


@tool
def copy_asset_to_slide(
    asset_id: str,
    slide_number: int,
    manifest_path: str = "/docs/assets_manifest.json",
) -> str:
    """Copy an asset file into the slide's local assets directory.

    Creates slides/assets/slide{N:02d}/{filename} and returns the
    relative path to use in slide HTML src attributes.

    Args:
        asset_id: The asset identifier.
        slide_number: The target slide number (1-indexed).
        manifest_path: Virtual path to assets_manifest.json.

    Returns:
        The relative path from the presentation root (e.g., "assets/slide01/figure_1.png"),
        or an error string.
    """
    result = resolve_asset.invoke({
        "asset_id": asset_id,
        "manifest_path": manifest_path,
    })

    try:
        data = json.loads(result)
    except json.JSONDecodeError:
        return result  # forwarded error string

    if not data.get("exists"):
        return f"ERROR: asset file not found on disk: {data.get('path')}"

    src = Path(data["path"])
    project_root = get_project_root() or str(resolve_vpath("/").parent)
    dest_dir = Path(project_root) / "slides" / "assets" / f"slide{slide_number:02d}"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    shutil.copy2(src, dest)

    rel_path = f"assets/slide{slide_number:02d}/{src.name}"
    return rel_path


@tool
def batch_resolve_assets(
    asset_ids: list[str],
    slide_assignments: str,  # JSON mapping {"fig_1": 3, "table_1": 5}
    manifest_path: str = "/docs/assets_manifest.json",
) -> str:
    """Copy multiple assets to their target slides in one call.
    
    Args:
        asset_ids: List of asset IDs to resolve.
        slide_assignments: JSON mapping asset_id -> slide_number.
        manifest_path: Path to assets manifest.
    
    Returns:
        JSON mapping asset_id -> relative_path for use in HTML src attributes.
    """
    assignments = json.loads(slide_assignments)
    results = {}
    for asset_id in asset_ids:
        slide_num = assignments.get(asset_id, 1)
        # We manually call the inner logic of copy_asset_to_slide to avoid
        # tool wrapping complications
        path = copy_asset_to_slide.invoke({
            "asset_id": asset_id,
            "slide_number": slide_num,
            "manifest_path": manifest_path,
        })
        results[asset_id] = path
    return json.dumps(results)


@tool
def list_assets(
    manifest_path: str = "/docs/assets_manifest.json",
    asset_type: str = "all",
) -> str:
    """List all assets in the project manifest, optionally filtered by type.

    Args:
        manifest_path: Virtual path to assets_manifest.json.
        asset_type: Filter by type: 'all', 'figure', 'table', or 'equation'.

    Returns:
        JSON list of asset summaries with id, type, caption, and path.
    """
    manifest_p = resolve_vpath(manifest_path)
    if not manifest_p.exists():
        return f"ERROR: manifest not found at {manifest_path}"

    manifest = json.loads(manifest_p.read_text())

    # parse_pdf writes top-level "images" and "tables" keys
    all_assets: list = []
    for key in ("images", "tables", "figures", "equations", "assets"):
        for item in manifest.get(key, []):
            # Infer type from key / id if not already present
            if "type" not in item:
                item = {**item, "type": key.rstrip("s")}  # images->image, tables->table
            all_assets.append(item)

    if asset_type != "all":
        all_assets = [a for a in all_assets if a.get("type", "") == asset_type]

    summary = [
        {
            "id": a.get("id", a.get("filename", "?")),
            "type": a.get("type", "unknown"),
            "caption": a.get("caption", "")[:80],
            "path": a.get("path", ""),
        }
        for a in all_assets
    ]
    return json.dumps(summary, indent=2)
