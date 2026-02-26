"""Docling PDF -> Markdown + assets parser."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List

try:
    from langchain.tools import tool
except Exception:

    def tool(*_args, **_kwargs):
        def _wrap(fn):
            return fn
        return _wrap


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _serialize_bbox(bbox: Any) -> list[float] | None:
    """Convert a Docling BoundingBox into [l, t, r, b] floats."""
    if bbox is None:
        return None
    if isinstance(bbox, (list, tuple)):
        return [float(x) for x in bbox]
    for attrs in (("l", "t", "r", "b"), ("x0", "y0", "x1", "y1")):
        if all(hasattr(bbox, a) for a in attrs):
            return [float(getattr(bbox, a)) for a in attrs]
    if hasattr(bbox, "model_dump"):
        return [float(v) for v in bbox.model_dump().values()]
    return None


def _extract_prov(item: Any) -> tuple[int | None, list[float] | None]:
    """Return (page_number, bbox) from item.prov[0] provenance."""
    prov = getattr(item, "prov", None)
    page, bbox = None, None
    if prov and len(prov) > 0:
        p0 = prov[0]
        raw = getattr(p0, "page_no", None)
        if raw is not None:
            page = int(raw)
        bbox = _serialize_bbox(getattr(p0, "bbox", None))
    return page, bbox


def _extract_pictures(doc: Any, images_dir: Path) -> List[Dict[str, Any]]:
    pictures: list[dict[str, Any]] = []
    for idx, pic in enumerate(getattr(doc, "pictures", None) or [], start=1):
        try:
            image = pic.get_image(doc)
        except Exception:
            continue
        if image is None:
            continue

        fname = f"fig_{idx}.png"
        try:
            image.save(images_dir / fname)
        except Exception:
            continue

        caption = ""
        try:
            caption = pic.caption_text(doc)
        except Exception:
            pass

        page, bbox = _extract_prov(pic)
        pictures.append({
            "id": f"fig_{idx}",
            "path": f"images/{fname}",
            "caption": caption,
            "page": page,
            "bbox": bbox,
        })
    return pictures


def _extract_tables(doc: Any, tables_dir: Path) -> List[Dict[str, Any]]:
    tables: list[dict[str, Any]] = []
    for idx, table in enumerate(getattr(doc, "tables", None) or [], start=1):
        tid = f"table_{idx}"
        html_path = tables_dir / f"{tid}.html"
        try:
            html_path.write_text(table.export_to_html(doc), encoding="utf-8")
        except Exception:
            continue

        caption = ""
        try:
            caption = table.caption_text(doc)
        except Exception:
            pass

        page, bbox = _extract_prov(table)
        tables.append({
            "id": tid,
            "path": f"tables/{tid}.html",
            "caption": caption,
            "page": page,
            "bbox": bbox,
        })
    return tables


def parse_pdf_core(
    pdf_path: str,
    project_path: str,
    images_scale: float = 2.0,
    image_ref_mode: str = "referenced",
    verbose: bool = False,
) -> Dict[str, Any]:
    """Parse a PDF into markdown + structured assets using Docling.

    Returns a summary dict with output paths and counts.
    """
    start = time.time()

    def log(msg: str) -> None:
        if verbose:
            print(f"[parse_pdf] {msg}")

    project_dir = Path(project_path)
    docs_dir = project_dir / "docs"
    images_dir = project_dir / "images"
    tables_dir = project_dir / "tables"
    for d in (docs_dir, images_dir, tables_dir):
        _ensure_dir(d)

    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, InputFormat, PdfFormatOption

    opts = PdfPipelineOptions()
    opts.do_ocr = False
    opts.do_table_structure = True
    opts.generate_picture_images = True
    opts.images_scale = images_scale
    opts.do_formula_enrichment = True

    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)}
    )
    log(f"Converting {pdf_path}")
    result = converter.convert(pdf_path)
    if getattr(result, "document", None) is None:
        raise RuntimeError("Docling conversion failed: no document returned.")
    doc = result.document

    # Extract assets
    images = _extract_pictures(doc, images_dir)
    log(f"Extracted {len(images)} images")
    tables = _extract_tables(doc, tables_dir)
    log(f"Extracted {len(tables)} tables")

    # ── Export markdown ──────────────────────────────────────────────────
    md_path = docs_dir / "document.md"

    # Try to load Docling's ImageRefMode enum
    _placeholder_enum = None
    _selected_enum = None
    try:
        from docling_core.types.doc import ImageRefMode
        _placeholder_enum = ImageRefMode.PLACEHOLDER
        _mode_map = {"referenced": ImageRefMode.REFERENCED,
                     "embedded": ImageRefMode.EMBEDDED,
                     "placeholder": ImageRefMode.PLACEHOLDER}
        _selected_enum = _mode_map.get(image_ref_mode)
    except Exception:
        pass

    if image_ref_mode == "referenced":
        # Use placeholder mode then substitute our own clean relative paths
        # (avoids Docling writing deeply-nested absolute paths).
        try:
            md_text = doc.export_to_markdown(image_mode=_placeholder_enum) if _placeholder_enum else doc.export_to_markdown()
        except Exception:
            md_text = doc.export_to_markdown()

        _img_iter = iter(images)
        _ph_re = re.compile(r"<!--\s*image\s*-->", re.IGNORECASE)

        def _sub(m: re.Match) -> str:
            try:
                img = next(_img_iter)
                return f'![{img.get("caption") or img["id"]}]({img["path"]})'
            except StopIteration:
                return m.group(0)

        md_text = _ph_re.sub(_sub, md_text)
    elif _selected_enum is not None:
        # Honour the user's chosen mode (embedded / placeholder)
        try:
            md_text = doc.export_to_markdown(image_mode=_selected_enum)
        except Exception:
            md_text = doc.export_to_markdown()
    else:
        md_text = doc.export_to_markdown()

    md_path.write_text(md_text, encoding="utf-8")
    log(f"Wrote {md_path}")

    # ── Assets manifest ──────────────────────────────────────────────────
    manifest = {"images": images, "tables": tables}
    manifest_path = docs_dir / "assets_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    log("Wrote assets_manifest.json")

    duration = round(time.time() - start, 2)
    log(f"Done in {duration}s")

    return {
        "document": "/docs/document.md",
        "assets_manifest": "/docs/assets_manifest.json",
        "images": len(images),
        "tables": len(tables),
        "duration_seconds": duration,
    }


@tool
def parse_pdf(pdf_path: str) -> Dict[str, Any]:
    """Parse a PDF into markdown, images, and tables using Docling.

    Writes docs/document.md, docs/assets_manifest.json, images/*, and tables/*
    under the PDF's parent directory (the project root). Only provide the
    absolute path to the PDF file — the project directory is derived automatically.
    """
    # Derive project root from PDF location (PDF is always at {project}/input.pdf)
    project_path = str(Path(pdf_path).resolve().parent)
    try:
        from config import config as _cfg
        images_scale = _cfg.images_scale
        image_ref_mode = _cfg.image_ref_mode
    except Exception:
        images_scale = 2.0
        image_ref_mode = "referenced"
    return parse_pdf_core(
        pdf_path, project_path,
        images_scale=images_scale,
        image_ref_mode=image_ref_mode,
    )


__all__ = ["parse_pdf", "parse_pdf_core"]
