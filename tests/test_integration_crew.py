import os

import pytest

from logistics_crew.runner import run_instruction


@pytest.mark.integration
def test_crew_end_to_end(repo):
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")
    report = run_instruction(
        "Cheapest mock rate from 01310-000 to 22041-080 for 2.5 kg and status of BR123456789BR",
        repo,
        verbose=False,
    )
    assert "## Tool evidence" in report
    assert "01310-000" in report or "BR123456789BR" in report
