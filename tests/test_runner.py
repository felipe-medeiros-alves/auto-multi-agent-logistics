import pytest

from logistics_crew.runner import ConfigurationError, run_instruction


def test_run_instruction_requires_api_key(repo, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ConfigurationError, match="OPENAI_API_KEY"):
        run_instruction("track BR123456789BR", repo)
