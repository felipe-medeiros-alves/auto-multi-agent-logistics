import json

from logistics_crew.shipping.tools import ToolTraceCollector, build_shipping_tools


def test_tool_trace_collector_records_calls(repo):
    trace = ToolTraceCollector()
    tools = {t.name: t for t in build_shipping_tools(repo, trace=trace)}
    tools["get_shipping_rates"].run(
        origin_cep="01310-000",
        destination_cep="22041-080",
        weight_kg=1.0,
    )
    assert len(trace.events) == 1
    assert trace.events[0].name == "get_shipping_rates"
    data = json.loads(trace.events[0].result)
    assert data["ok"] is True
