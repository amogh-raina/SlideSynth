"""SlideSynth configuration.

Loads from config.yaml if present, falls back to environment variables.
All model strings use LangChain's init_chat_model format: "provider:model-name".
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

# Load .env file before anything else so all os.environ lookups below see the keys.
# python-dotenv is a core dependency; this is a no-op if .env doesn't exist.
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=False)
except ImportError:
    pass  # dotenv not installed yet — run: uv sync


_DEFAULT_MODELS: Dict[str, str] = {
    "orchestrator": "anthropic:claude-sonnet-4-5-20250929",
    "research": "anthropic:claude-haiku-4-5-20251001",
    "planner": "anthropic:claude-haiku-4-5-20251001",
    "verifier": "anthropic:claude-haiku-4-5-20251001",
    "design": "anthropic:claude-haiku-4-5-20251001",
    "generator": "anthropic:claude-sonnet-4-5-20250929",
    "editor": "anthropic:claude-haiku-4-5-20251001",
}


class SlideSynthConfig:
    """Holds runtime configuration for model selection and optional features."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data
        self.models: Dict[str, str] = {
            **_DEFAULT_MODELS,
            **data.get("models", {}),
        }
        parsing = data.get("parsing", {})
        self.enhanced_extraction: bool = parsing.get("enhanced_extraction", False)
        self.langextract_model: str = parsing.get(
            "langextract_model", "gemini-2.5-flash"
        )
        # Docling images_scale: 1.0 ≈ 72 DPI, 2.0 ≈ 144 DPI (default), 3.0 ≈ 216 DPI
        self.images_scale: float = float(parsing.get("images_scale", 2.0))
        # How images are referenced in the exported markdown.
        # "referenced" → ![caption](images/fig_1.png)  (LLM can see the path)
        # "embedded"   → base64 data URI inline
        self.image_ref_mode: str = parsing.get("image_ref_mode", "referenced")

    def model(self, role: str) -> str:
        """Return the model string for the given agent role."""
        return self.models.get(role, _DEFAULT_MODELS.get(role, "anthropic:claude-sonnet-4-5-20250929"))

    @property
    def custom_endpoints(self) -> Dict[str, Any]:
        return self._data.get("custom_endpoints", {})


def load_config(config_path: Optional[str | Path] = None) -> SlideSynthConfig:
    """Load config from YAML file.  Falls back gracefully if file is absent.

    The config file path is resolved in this order:
      1. Explicit ``config_path`` argument
      2. ``SLIDESYNTH_CONFIG`` environment variable
      3. ``config.yaml`` next to this file
    """
    if config_path:
        path = Path(config_path)
    else:
        env_path = os.environ.get("SLIDESYNTH_CONFIG")
        path = Path(env_path) if env_path else Path(__file__).parent / "config.yaml"
    if path.exists():
        with open(path) as f:
            data = yaml.safe_load(f) or {}
    else:
        data = {}

    # Allow per-role model overrides from env vars, e.g. SLIDESYNTH_MODEL_ORCHESTRATOR
    for role in _DEFAULT_MODELS:
        env_key = f"SLIDESYNTH_MODEL_{role.upper()}"
        env_val = os.environ.get(env_key)
        if env_val:
            data.setdefault("models", {})[role] = env_val

    return SlideSynthConfig(data)


# Module-level default instance (override by calling load_config explicitly)
config = load_config()
