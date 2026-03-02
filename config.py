"""SlideSynth configuration.

Loads from config.yaml if present, falls back to environment variables.
All model strings use LangChain's init_chat_model format: "provider:model-name".

Supported providers:
  - anthropic:model-name   → Anthropic API (requires ANTHROPIC_API_KEY)
  - openai:model-name      → OpenAI API (requires OPENAI_API_KEY)
  - ollama:model-name      → Local Ollama instance
  - openrouter:model-name  → OpenRouter API (requires OPENROUTER_API_KEY)

The openrouter provider uses the native ``langchain-openrouter`` package
(``ChatOpenRouter``) which provides first-class OpenRouter support including
reasoning tokens.  You can use any model available on OpenRouter
(e.g. openrouter:moonshotai/kimi-k2.5).

Thinking / Extended Reasoning:
  Per-role thinking can be enabled in config.yaml under the ``thinking`` key.
  Each provider uses different kwargs — the config layer auto-translates:

  - anthropic  → thinking={"type":"enabled","budget_tokens":N}, max_tokens raised
  - openai     → reasoning_effort="low"|"medium"|"high" (o-series models)
  - google_genai / google_vertexai → thinking={"type":"enabled","budget_tokens":N}
  - deepseek   → thinking={"type":"enabled","budget_tokens":N}
  - openrouter → reasoning={"effort":"high"} via ChatOpenRouter
  - ollama     → think=True (for models that support it, e.g. qwen3)
  - others     → generic kwargs passthrough via model_kwargs

  When thinking is enabled for a role, ``model()`` returns a pre-built
  BaseChatModel instance instead of a plain string.
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
        # Per-role thinking / extended reasoning configuration
        self.thinking: Dict[str, Dict[str, Any]] = data.get("thinking", {})
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

    # ── Model construction ────────────────────────────────────────────

    def model(self, role: str):
        """Return a model instance or init_chat_model-compatible string for *role*.

        When thinking is enabled for this role, returns a pre-built
        BaseChatModel with provider-specific thinking kwargs.
        Otherwise returns the ``"provider:model-name"`` string.
        """
        model_str: str = self.models.get(
            role, _DEFAULT_MODELS.get(role, "anthropic:claude-sonnet-4-5-20250929")
        )
        thinking_cfg = self.thinking.get(role, {})
        has_thinking = thinking_cfg.get("enabled", False)

        if model_str.startswith("openrouter:"):
            return self._make_openrouter_model(model_str, thinking_cfg)

        if has_thinking:
            return self._make_model_with_thinking(model_str, thinking_cfg)

        return model_str

    # ── Provider-specific builders ────────────────────────────────────

    def _make_model_with_thinking(self, model_str: str, thinking_cfg: Dict[str, Any]):
        """Build a chat model with extended thinking / reasoning enabled.

        Detects the provider from the model string and applies the correct
        kwargs.  Falls back to a generic ``thinking`` kwarg for unknown
        providers.
        """
        from langchain.chat_models import init_chat_model  # lazy

        provider, _ = (model_str.split(":", 1) + [""])[:2]
        budget: int = int(thinking_cfg.get("budget_tokens", 10_000))
        effort: str = thinking_cfg.get("effort", "medium")  # low | medium | high

        kwargs: Dict[str, Any] = {}

        if provider == "anthropic":
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": budget}
            # Anthropic requires max_tokens >= budget_tokens when thinking is on
            kwargs["max_tokens"] = max(16_000, budget + 8_000)

        elif provider == "openai":
            # For o-series (o1, o3, o4-mini) reasoning is built-in.
            # reasoning_effort tunes how long the model thinks.
            kwargs["reasoning_effort"] = effort

        elif provider in ("google_genai", "google_vertexai"):
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": budget}

        elif provider == "deepseek":
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": budget}

        elif provider == "ollama":
            # Ollama models that support thinking (e.g. qwen3) use think=True
            kwargs["think"] = True

        else:
            # Generic fallback — try the most common param name
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": budget}

        return init_chat_model(model_str, **kwargs)

    def _make_openrouter_model(
        self, model_str: str, thinking_cfg: Dict[str, Any] | None = None
    ):
        """Create a ``ChatOpenRouter`` instance from ``langchain-openrouter``.

        If thinking/reasoning is enabled, sets the native ``reasoning``
        parameter that ``ChatOpenRouter`` supports directly.

        See https://openrouter.ai/docs/guides/best-practices/reasoning-tokens
        """
        from langchain_openrouter import ChatOpenRouter  # lazy import

        model_name = model_str.split(":", 1)[1]

        kwargs: Dict[str, Any] = {"model": model_name}

        thinking_cfg = thinking_cfg or {}
        if thinking_cfg.get("enabled"):
            effort = thinking_cfg.get("effort", "medium")
            reasoning: Dict[str, Any] = {"effort": effort}
            summary = thinking_cfg.get("summary")
            if summary:
                reasoning["summary"] = summary
            budget = thinking_cfg.get("budget_tokens")
            if budget:
                reasoning["max_tokens"] = int(budget)
            kwargs["reasoning"] = reasoning

        return ChatOpenRouter(**kwargs)

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
