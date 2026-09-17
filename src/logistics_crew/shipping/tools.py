import json
from typing import Literal

from crewai.tools import tool

from logistics_crew.reporting.models import ToolEvent
from logistics_crew.shipping.repository import ShippingRepository
from logistics_crew.shipping.validators import (
    normalize_cep,
    validate_tracking_id,
    validate_weight_kg,
)


class ToolTraceCollector:
    def __init__(self) -> None:
        self.events: list[ToolEvent] = []

    def record(self, name: str, args: dict[str, object], result: str) -> None:
        self.events.append(ToolEvent(name=name, args=args, result=result))


def _err(message: str) -> str:
    return json.dumps({"ok": False, "error": message})


def _wrap_with_trace(tool, collector: ToolTraceCollector | None):
    if collector is None:
        return tool
    original = tool.func

    def wrapped(**kwargs):
        result = original(**kwargs)
        collector.record(tool.name, dict(kwargs), result)
        return result

    tool.func = wrapped
    return tool


def build_shipping_tools(
    repo: ShippingRepository,
    trace: ToolTraceCollector | None = None,
) -> list:
    @tool("get_shipping_rates")
    def get_shipping_rates(
        origin_cep: str,
        destination_cep: str,
        weight_kg: float,
        service: str | None = None,
    ) -> str:
        """Return mock shipping rates for origin and destination CEPs and parcel weight."""
        try:
            validate_weight_kg(weight_kg)
            origin = normalize_cep(origin_cep)
            destination = normalize_cep(destination_cep)
            if service is not None and service not in ("PAC", "SEDEX"):
                raise ValueError("service must be PAC or SEDEX when provided")
        except ValueError as exc:
            return _err(str(exc))
        rates = repo.get_rates(origin, destination, weight_kg, service=service)
        return json.dumps({"ok": True, "rates": rates})

    @tool("get_shipment_tracking")
    def get_shipment_tracking(tracking_id: str) -> str:
        """Look up mock tracking status and events for a tracking ID."""
        try:
            validate_tracking_id(tracking_id)
        except ValueError as exc:
            return _err(str(exc))
        shipment = repo.get_tracking(tracking_id)
        if shipment is None:
            return json.dumps({"ok": True, "shipment": None})
        return json.dumps({"ok": True, "shipment": shipment})

    @tool("list_shipments")
    def list_shipments(
        status: Literal["in_transit", "delivered"] | None = None,
        origin_cep: str | None = None,
    ) -> str:
        """List mock shipments, optionally filtered by status and origin CEP."""
        origin: str | None = None
        if origin_cep is not None:
            try:
                origin = normalize_cep(origin_cep)
            except ValueError as exc:
                return _err(str(exc))
        if status is not None and status not in ("in_transit", "delivered"):
            return _err("status must be in_transit or delivered")
        rows = repo.list_shipments(status=status, origin=origin)
        return json.dumps({"ok": True, "shipments": rows})

    tools = [get_shipping_rates, get_shipment_tracking, list_shipments]
    return [_wrap_with_trace(t, trace) for t in tools]
