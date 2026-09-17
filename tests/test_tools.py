import json

import pytest

from logistics_crew.shipping.tools import build_shipping_tools


@pytest.fixture
def tools(repo):
    return {t.name: t for t in build_shipping_tools(repo)}


def test_get_shipping_rates_valid(tools):
    out = tools["get_shipping_rates"].run(
        origin_cep="01310-000",
        destination_cep="22041-080",
        weight_kg=2.5,
    )
    data = json.loads(out)
    assert data["ok"] is True
    assert len(data["rates"]) >= 1


def test_get_shipping_rates_invalid_weight(tools):
    out = tools["get_shipping_rates"].run(
        origin_cep="01310-000",
        destination_cep="22041-080",
        weight_kg=0,
    )
    data = json.loads(out)
    assert data["ok"] is False
    assert "weight_kg" in data["error"]


def test_get_shipping_rates_invalid_cep(tools):
    out = tools["get_shipping_rates"].run(
        origin_cep="invalid",
        destination_cep="22041-080",
        weight_kg=1.0,
    )
    data = json.loads(out)
    assert data["ok"] is False


def test_get_shipment_tracking_valid(tools):
    out = tools["get_shipment_tracking"].run(tracking_id="BR123456789BR")
    data = json.loads(out)
    assert data["ok"] is True
    assert data["shipment"]["tracking_id"] == "BR123456789BR"


def test_get_shipment_tracking_invalid_id(tools):
    out = tools["get_shipment_tracking"].run(tracking_id="not-a-tracking-id")
    data = json.loads(out)
    assert data["ok"] is False


def test_list_shipments_filter(tools):
    out = tools["list_shipments"].run(status="in_transit")
    data = json.loads(out)
    assert data["ok"] is True
    assert all(s["status"] == "in_transit" for s in data["shipments"])
