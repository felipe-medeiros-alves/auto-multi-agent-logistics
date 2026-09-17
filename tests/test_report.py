from logistics_crew.reporting.models import RunTrace, ToolEvent
from logistics_crew.reporting.render import render_markdown_report


def test_render_markdown_report_sections():
    trace = RunTrace(
        instruction="Quote shipping SP to RJ",
        plan="1. Fetch rates\n2. Summarize",
        tool_events=[
            ToolEvent(
                name="get_shipping_rates",
                args={"origin_cep": "01310-000", "destination_cep": "22041-080", "weight_kg": 2.5},
                result='{"ok": true, "rates": []}',
            )
        ],
        findings="Cheapest option is PAC at 45.90 BRL.",
        recommended_actions=["Would book PAC if executing."],
        gaps=["No live carrier API."],
    )
    md = render_markdown_report(trace)
    assert "## Instruction" in md
    assert "## Plan" in md
    assert "## Tool evidence" in md
    assert "get_shipping_rates" in md
    assert "## Findings" in md
    assert "## Recommended next actions" in md
    assert "## Gaps and risks" in md
    assert "Quote shipping SP to RJ" in md
