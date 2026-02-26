"""Enhanced semantic extraction using LangExtract.

Provides source-grounded structured extraction from parsed academic paper markdown.
Maps every extracted claim, result, figure, and equation to its exact location in
the source text — enabling traceability and verification of slide content.

This tool is:
- Optional (enabled via config: parsing.enhanced_extraction: true)
- Additive (complements Docling, does NOT replace it)
- Safe (falls back gracefully if langextract or API is unavailable)
- Configurable (model_id via config.langextract_model)

Output: {project_dir}/docs/enhanced_analysis.json

References:
  https://github.com/google/langextract
  pip install langextract
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any

from langchain.tools import tool


# ---------------------------------------------------------------------------
# Extraction schema definition
# ---------------------------------------------------------------------------

# Prompt describing what to extract from academic papers.
_EXTRACTION_PROMPT = textwrap.dedent("""\
    Extract the following entity types from this academic paper, in order of appearance.
    Use the exact text from the document for each extraction — do not paraphrase.
    Each entity should be a complete, meaningful phrase or sentence.

    Entity types to extract:
    - key_claim: A major scientific claim, contribution, or finding stated in the paper
    - core_result: A quantitative result with specific numbers (accuracy, improvement, metric values)
    - section_role: A section heading that establishes the narrative structure of the paper
    - figure_significance: A figure caption that describes an important visual (mark as "critical" or "illustrative")
    - equation_label: An equation label or inline formula that is central to the method (not supplementary)
    - core_term: A domain-specific term that must be defined for the audience to understand the paper

    Focus on entities that would be most useful for creating a conference presentation.
    Do not extract every instance — prioritize the most impactful ones.
""")

_EXTRACTION_EXAMPLES = None  # Populated lazily to avoid import at module level


def _get_examples() -> list[Any]:
    """Build LangExtract examples for academic paper extraction."""
    try:
        import langextract as lx  # type: ignore[import]  # noqa: PLC0415
    except ImportError:
        return []

    return [
        lx.data.ExampleData(
            text=(
                "1 Introduction\n"
                "Training large language models requires substantial compute. "
                "We propose AdaptLR, a method that reduces training cost by 32% "
                "while maintaining accuracy within 0.3% of baseline on GLUE. "
                "Figure 1 shows the overall architecture of our approach."
            ),
            extractions=[
                lx.data.Extraction(
                    extraction_class="section_role",
                    extraction_text="1 Introduction",
                    attributes={"narrative_role": "introduction", "position": "opening"},
                ),
                lx.data.Extraction(
                    extraction_class="key_claim",
                    extraction_text="We propose AdaptLR, a method that reduces training cost by 32%",
                    attributes={"claim_type": "contribution", "specificity": "quantified"},
                ),
                lx.data.Extraction(
                    extraction_class="core_result",
                    extraction_text="reduces training cost by 32% while maintaining accuracy within 0.3% of baseline on GLUE",
                    attributes={"metric": "training cost + GLUE accuracy", "improvement": "32%"},
                ),
                lx.data.Extraction(
                    extraction_class="figure_significance",
                    extraction_text="Figure 1 shows the overall architecture of our approach",
                    attributes={"significance": "critical", "type": "architecture_diagram"},
                ),
            ],
        ),
        lx.data.ExampleData(
            text=(
                "3 Method\n"
                "We define the adaptive learning rate as:\n"
                "\\alpha_t = \\alpha_0 / \\sqrt{\\sum_{i=1}^{t} g_i^2}\n"
                "where g_i is the gradient at step i. "
                "This formulation, which we call AdaptLR, builds on AdaGrad (Duchi et al., 2011). "
                "Unlike AdaGrad, our method introduces a momentum term to prevent learning rate decay.\n"
                "AdaptLR is a form of adaptive gradient descent."
            ),
            extractions=[
                lx.data.Extraction(
                    extraction_class="section_role",
                    extraction_text="3 Method",
                    attributes={"narrative_role": "methodology", "position": "core"},
                ),
                lx.data.Extraction(
                    extraction_class="equation_label",
                    extraction_text="\\alpha_t = \\alpha_0 / \\sqrt{\\sum_{i=1}^{t} g_i^2}",
                    attributes={"significance": "central", "label": "AdaptLR update rule"},
                ),
                lx.data.Extraction(
                    extraction_class="key_claim",
                    extraction_text="our method introduces a momentum term to prevent learning rate decay",
                    attributes={"claim_type": "novelty", "specificity": "comparative"},
                ),
                lx.data.Extraction(
                    extraction_class="core_term",
                    extraction_text="AdaptLR",
                    attributes={"definition": "adaptive learning rate method with momentum", "introduced_here": True},
                ),
            ],
        ),
    ]


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------


@tool
def enhanced_extract(
    document_path: str,
    output_path: str = "",
    model_id: str = "",
) -> str:
    """Use LangExtract to produce source-grounded structured extraction from parsed paper markdown.

    Maps every extracted claim, result, figure reference, and equation to its exact
    location in the source text. This enables verification that slide content accurately
    reflects what the paper says.

    Extracts:
    - key_claim: Major claims and contributions (with claim type + specificity)
    - core_result: Quantitative results with specific numbers (with metric + improvement)
    - section_role: Section headings with their narrative role (intro/method/results/conclusion)
    - figure_significance: Figure captions rated "critical" or "illustrative"
    - equation_label: Central equations with labels (not supplementary derivations)
    - core_term: Domain-specific terms requiring audience definition

    Args:
        document_path: Path to the parsed paper markdown (e.g. /docs/document.md).
        output_path: Where to write enhanced_analysis.json. Defaults to same dir as document.
        model_id: LangExtract model to use. Defaults to config.langextract_model
                  (gemini-2.5-flash by default). Supports any Gemini model or Ollama local model.

    Returns:
        Summary of extracted entities counts and output file path.
        Returns an informative error message if langextract is unavailable or disabled.
    """
    # ------------------------------------------------------------------
    # 0. Config guard
    # ------------------------------------------------------------------
    try:
        from config import config as _cfg  # noqa: PLC0415
        if not _cfg.enhanced_extraction:
            return (
                "SKIPPED: enhanced_extract is disabled. "
                "Set 'parsing.enhanced_extraction: true' in config.yaml to enable it."
            )
        effective_model = model_id or _cfg.langextract_model
    except ImportError:
        effective_model = model_id or "gemini-2.5-flash"

    # ------------------------------------------------------------------
    # 1. Check langextract availability
    # ------------------------------------------------------------------
    try:
        import langextract as lx  # type: ignore[import]  # noqa: PLC0415
    except ImportError:
        return (
            "ERROR: langextract is not installed. "
            "Run: uv add langextract  (or: pip install langextract)\n"
            "Also set LANGEXTRACT_API_KEY (Google AI Studio key) in your environment."
        )

    # ------------------------------------------------------------------
    # 2. Read the document
    # ------------------------------------------------------------------
    doc_path = Path(document_path)
    if not doc_path.exists():
        return f"ERROR: Document not found: {document_path}"

    text = doc_path.read_text(encoding="utf-8")
    if len(text.strip()) < 100:
        return f"ERROR: Document at {document_path} appears empty or too short."

    # ------------------------------------------------------------------
    # 3. Determine output path
    # ------------------------------------------------------------------
    if output_path:
        out_path = Path(output_path)
    else:
        out_path = doc_path.parent / "enhanced_analysis.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 4. Run extraction
    # ------------------------------------------------------------------
    examples = _get_examples()
    try:
        result = lx.extract(
            text_or_documents=text,
            prompt_description=_EXTRACTION_PROMPT,
            examples=examples,
            model_id=effective_model,
            # For longer papers: parallel processing + multiple passes
            extraction_passes=2,   # Two passes for higher recall
            max_workers=4,         # Parallel chunk processing
            max_char_buffer=2000,  # Context per chunk (tune for long papers)
        )
    except Exception as exc:  # noqa: BLE001
        return (
            f"ERROR: LangExtract extraction failed: {exc}\n"
            "Check your LANGEXTRACT_API_KEY and model_id. "
            "The rest of the pipeline is unaffected — this tool is optional."
        )

    # ------------------------------------------------------------------
    # 5. Organise extractions by class
    # ------------------------------------------------------------------
    organised: dict[str, list[dict[str, Any]]] = {
        "key_claims": [],
        "core_results": [],
        "section_roles": [],
        "figure_significance": [],
        "equation_labels": [],
        "core_terms": [],
    }

    class_map = {
        "key_claim": "key_claims",
        "core_result": "core_results",
        "section_role": "section_roles",
        "figure_significance": "figure_significance",
        "equation_label": "equation_labels",
        "core_term": "core_terms",
    }

    for extraction in getattr(result, "extractions", []):
        cls = getattr(extraction, "extraction_class", "")
        bucket = class_map.get(cls)
        if bucket is None:
            continue
        organised[bucket].append(
            {
                "text": getattr(extraction, "extraction_text", ""),
                "attributes": getattr(extraction, "attributes", {}),
                # Source span — LangExtract provides char offsets when available
                "source_span": {
                    "start": getattr(extraction, "start_char", None),
                    "end": getattr(extraction, "end_char", None),
                },
            }
        )

    # ------------------------------------------------------------------
    # 6. Build output document
    # ------------------------------------------------------------------
    output_doc: dict[str, Any] = {
        "model_id": effective_model,
        "document_path": str(doc_path.resolve()),
        "summary": {
            "total_extractions": sum(len(v) for v in organised.values()),
            "key_claims": len(organised["key_claims"]),
            "core_results": len(organised["core_results"]),
            "section_roles": len(organised["section_roles"]),
            "critical_figures": sum(
                1 for f in organised["figure_significance"]
                if f.get("attributes", {}).get("significance") == "critical"
            ),
            "central_equations": len(organised["equation_labels"]),
            "core_terms": len(organised["core_terms"]),
        },
        **organised,
    }

    # ------------------------------------------------------------------
    # 7. Save JSONL-compatible output + JSON summary
    # ------------------------------------------------------------------
    out_path.write_text(json.dumps(output_doc, indent=2, ensure_ascii=False), encoding="utf-8")

    # Optional: save LangExtract's native JSONL for visualization
    jsonl_path = out_path.parent / "enhanced_analysis_raw.jsonl"
    try:
        lx.io.save_annotated_documents([result], output_name="enhanced_analysis_raw.jsonl", output_dir=str(out_path.parent))
    except Exception:  # noqa: BLE001
        pass  # JSONL save is optional; structured JSON is the primary output

    summary = output_doc["summary"]
    return (
        f"OK: Enhanced extraction complete using {effective_model}.\n"
        f"  Key claims: {summary['key_claims']}\n"
        f"  Core results: {summary['core_results']}\n"
        f"  Section roles: {summary['section_roles']}\n"
        f"  Critical figures: {summary['critical_figures']}\n"
        f"  Central equations: {summary['central_equations']}\n"
        f"  Core terms: {summary['core_terms']}\n"
        f"  Total extractions: {summary['total_extractions']}\n"
        f"  Written to: {out_path}\n"
        f"  JSONL for visualization: {jsonl_path}"
    )
