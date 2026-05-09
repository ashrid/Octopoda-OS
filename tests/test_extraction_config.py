import importlib
import json
import sys


def test_load_local_extraction_config_reads_persisted_settings(tmp_dir, monkeypatch):
    home_dir = tmp_dir
    monkeypatch.setenv("HOME", home_dir)
    monkeypatch.delenv("OCTOPODA_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("OCTOPODA_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OCTOPODA_OPENAI_MODEL", raising=False)
    monkeypatch.delenv("OCTOPODA_OPENAI_BASE_URL", raising=False)

    from pathlib import Path

    config_dir = Path(home_dir) / ".octopoda"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "extraction.json").write_text(json.dumps({
        "provider": "openrouter",
        "api_key": "sk-test-1234",
        "model": "qwen/qwen-turbo",
        "base_url": "https://openrouter.ai/api/v1",
    }))

    sys.modules.pop("synrix_runtime.extraction_config", None)
    from synrix_runtime.extraction_config import load_local_extraction_config

    assert load_local_extraction_config() is True
    assert importlib.import_module("os").environ["OCTOPODA_LLM_PROVIDER"] == "openai"
    assert importlib.import_module("os").environ["OCTOPODA_OPENAI_MODEL"] == "qwen/qwen-turbo"


def test_startup_import_applies_local_extraction_config(tmp_dir, monkeypatch):
    home_dir = tmp_dir
    monkeypatch.setenv("HOME", home_dir)
    monkeypatch.delenv("OCTOPODA_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("OCTOPODA_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OCTOPODA_OPENAI_MODEL", raising=False)
    monkeypatch.delenv("OCTOPODA_OPENAI_BASE_URL", raising=False)

    from pathlib import Path

    config_dir = Path(home_dir) / ".octopoda"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "extraction.json").write_text(json.dumps({
        "provider": "openrouter",
        "api_key": "sk-test-5678",
        "model": "qwen/qwen-turbo",
        "base_url": "https://openrouter.ai/api/v1",
    }))

    sys.modules.pop("synrix_runtime.extraction_config", None)
    sys.modules.pop("synrix_runtime.start", None)
    import synrix_runtime.start  # noqa: F401

    assert importlib.import_module("os").environ["OCTOPODA_LLM_PROVIDER"] == "openai"
    assert importlib.import_module("os").environ["OCTOPODA_OPENAI_MODEL"] == "qwen/qwen-turbo"
