"""SlideSynth tools package.

Provides a ContextVar-based virtual-path resolver so custom tools can
transparently map virtual paths (e.g. ``/docs/foo.json``) to real on-disk
paths under the current project root.

Usage in server/app.py (or cli.py)::

    from tools import set_project_root
    set_project_root("/abs/path/to/data/projects/<thread_id>")
"""

from __future__ import annotations

import contextvars
from pathlib import Path

# ---------------------------------------------------------------------------
# Project-root context (async-safe via ContextVar)
# ---------------------------------------------------------------------------

_project_root_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "slidesynth_project_root", default=""
)


def set_project_root(path: str) -> contextvars.Token[str]:
    """Set the current project root for virtual-path resolution.

    Call this once per request/stream before invoking the agent.
    Returns a token that can be used with ``_project_root_var.reset(token)``
    if you need to restore the previous value.
    """
    return _project_root_var.set(str(Path(path).resolve()))


def get_project_root() -> str:
    """Return the current project root, or empty string if unset."""
    return _project_root_var.get()


def resolve_vpath(virtual_path: str) -> Path:
    """Resolve a virtual path against the current project root.

    Resolution strategy:
      1. If project_root is set and the virtual path starts with ``/``,
         strip the leading ``/`` and join with project_root.
      2. If the resolved real path exists, return it.
      3. Otherwise fall back to ``Path(virtual_path)`` (raw OS path).

    This allows tools to accept paths like ``/docs/slide_outline.json``
    from agents operating in the virtual filesystem and transparently
    resolve them to ``<project_root>/docs/slide_outline.json`` on disk.
    """
    root = _project_root_var.get()
    if root and virtual_path.startswith("/"):
        candidate = Path(root) / virtual_path.lstrip("/")
        # Always prefer the resolved path when root is set
        return candidate
    # Fallback: treat as literal OS path (works for real absolute paths)
    return Path(virtual_path)


# ---------------------------------------------------------------------------
# Tool imports
# ---------------------------------------------------------------------------

from .parse_pdf import parse_pdf
from .quality_check import quality_check
from .html_generator import generate_slide_html, combine_presentation, switch_template
from .export import export_to_pdf
from .asset_manager import resolve_asset, copy_asset_to_slide, list_assets
from .enhanced_extract import enhanced_extract

__all__ = [
    # Context management
    "set_project_root",
    "get_project_root",
    "resolve_vpath",
    # Tools
    "parse_pdf",
    "quality_check",
    "generate_slide_html",
    "combine_presentation",
    "switch_template",
    "export_to_pdf",
    "resolve_asset",
    "copy_asset_to_slide",
    "list_assets",
    "enhanced_extract",
]
