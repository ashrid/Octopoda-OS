"""
Load Octopoda extraction config from dashboard settings into environment.
Run this before any Octopoda operations to wire dashboard settings to runtime.

Usage:
    python3 load_extraction_config.py
    # Then in the same terminal: octopoda-mcp, or any Octopoda operation
"""

import os
import json
from pathlib import Path

CONFIG_PATH = os.path.expanduser("~/.octopoda/extraction.json")

PROVIDER_MAP = {
    "openai": "openai",
    "anthropic": "anthropic",
    "ollama": "ollama",
    "openrouter": "openai",  # OpenRouter uses OpenAI-compatible API
    "custom": "openai",      # Custom OpenAI-compatible
}

def load_config():
    """Load extraction config and set environment variables."""
    if not os.path.exists(CONFIG_PATH):
        print("No extraction config found at", CONFIG_PATH)
        return False

    with open(CONFIG_PATH) as f:
        config = json.load(f)

    provider = config.get("provider", "none")
    api_key = config.get("api_key", "")
    model = config.get("model", "gpt-4o-mini")
    base_url = config.get("base_url", "https://openrouter.ai/api/v1")

    if provider == "none" or not api_key:
        os.environ["OCTOPODA_LLM_PROVIDER"] = "none"
        print("Extraction: disabled (provider=none or no API key)")
        return True

    mapped = PROVIDER_MAP.get(provider, "openai")

    os.environ["OCTOPODA_LLM_PROVIDER"] = mapped
    os.environ["OCTOPODA_OPENAI_API_KEY"] = api_key
    os.environ["OCTOPODA_OPENAI_MODEL"] = model
    os.environ["OCTOPODA_OPENAI_BASE_URL"] = base_url

    print(f"Extraction: {provider} → {mapped}")
    print(f"  Model: {model}")
    print(f"  Endpoint: {base_url}")
    print(f"  API Key: {'***' + api_key[-4:] if len(api_key) > 4 else 'set'}")
    return True


def verify():
    """Verify the FactExtractor picks up the config."""
    from synrix.fact_extractor import FactExtractor
    ext = FactExtractor.get()
    if ext and ext._available:
        print(f"  FactExtractor: ✅ ACTIVE")
        print(f"  Provider: {ext._provider}")
        print(f"  Model: {ext._openai_model if hasattr(ext, '_openai_model') else 'N/A'}")
        # Test it
        result = ext.extract_facts("Rashid prefers concise responses with bullet points")
        if result.used_llm:
            print(f"  Test extraction: ✅ {len(result.facts)} facts extracted")
            for f in result.facts:
                print(f"    - {f}")
        else:
            print(f"  Test extraction: ⚠️  LLM not used (fallback)")
        return True
    else:
        print(f"  FactExtractor: ❌ NOT AVAILABLE")
        return False


if __name__ == "__main__":
    loaded = load_config()
    if loaded:
        verify()
