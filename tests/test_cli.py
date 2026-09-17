import pytest

from logistics_crew.cli import execute
from logistics_crew.runner import ConfigurationError


def test_execute_prints_report(repo, monkeypatch, tmp_path):
    db = tmp_path / "shipping.db"
    from logistics_crew.shipping.seed import init_database

    init_database(db)

    def fake_run(instruction, repository, *, verbose=False, llm=None):
        assert "cheapest" in instruction.lower()
        return "# Execution report\n\n## Instruction\n\ndemo"

    monkeypatch.setattr("logistics_crew.cli.run_instruction", fake_run)
    report = execute("Quote cheapest rate", db_path=db)
    assert "Execution report" in report


def test_execute_missing_key_raises(repo, monkeypatch, tmp_path):
    db = tmp_path / "shipping.db"
    from logistics_crew.shipping.seed import init_database

    init_database(db)

    def raise_config(*_a, **_k):
        raise ConfigurationError("OPENAI_API_KEY is not set.")

    monkeypatch.setattr("logistics_crew.cli.run_instruction", raise_config)
    with pytest.raises(ConfigurationError):
        execute("hello", db_path=db)
