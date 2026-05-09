"""Local extraction configuration helpers.

Loads and applies the persisted local extraction settings so the runtime and
dashboard share one source of truth.
"""

from __future__ import annotations

import json
import os


EXTRACTION_CONFIG_PATH = os.path.expanduser("~/.octopoda/extraction.json")

PROVIDER_MAP = {
    "openai": "openai",
    "anthropic": "anthropic",
    "ollama": "ollama",
    "openrouter": "openai",
    "custom": "openai",
}


def default_extraction_settings() -> dict:
    return {
        "provider": "openrouter",
        "api_key": "",
        "model": "qwen/qwen-turbo",
        "base_url": "https://openrouter.ai/api/v1",
        "auto_extract": True,
        "extract_preferences": True,
        "extract_facts": True,
        "extract_decisions": True,
        "max_extractions_per_min": 10,
    }


def load_extraction_settings() -> dict:
    if not os.path.exists(EXTRACTION_CONFIG_PATH):
        return default_extraction_settings()
    try:
        with open(EXTRACTION_CONFIG_PATH) as handle:
            data = json.load(handle)
            return {**default_extraction_settings(), **data}
    except Exception:
        return default_extraction_settings()


def save_extraction_settings(settings: dict) -> dict:
    merged = {**default_extraction_settings(), **settings}
    os.makedirs(os.path.dirname(EXTRACTION_CONFIG_PATH), exist_ok=True)
    with open(EXTRACTION_CONFIG_PATH, "w") as handle:
        json.dump(merged, handle, indent=2)
    return merged


def apply_extraction_settings(settings: dict) -> None:
    provider = settings.get("provider", "none")
    api_key = settings.get("api_key", "")
    model = settings.get("model", "gpt-4o-mini")
    base_url = settings.get("base_url", "https://openrouter.ai/api/v1")

    if provider == "none" or not api_key:
        os.environ["OCTOPODA_LLM_PROVIDER"] = "none"
        return

    mapped = PROVIDER_MAP.get(provider, "openai")
    os.environ["OCTOPODA_LLM_PROVIDER"] = mapped
    os.environ["OCTOPODA_OPENAI_API_KEY"] = api_key
    os.environ["OCTOPODA_OPENAI_MODEL"] = model
    os.environ["OCTOPODA_OPENAI_BASE_URL"] = base_url


def load_local_extraction_config() -> bool:
    settings = load_extraction_settings()
    apply_extraction_settings(settings)
    return True
