import sqlite3
from pathlib import Path
from typing import Any


class ShippingRepository:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_rates(
        self,
        origin: str,
        destination: str,
        weight_kg: float,
        service: str | None = None,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT service, price_brl, eta_days, max_weight_kg
            FROM rates
            WHERE origin_cep = ? AND destination_cep = ? AND max_weight_kg >= ?
        """
        params: list[Any] = [origin, destination, weight_kg]
        if service is not None:
            query += " AND service = ?"
            params.append(service)
        query += " ORDER BY price_brl ASC"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def get_tracking(self, tracking_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            shipment = conn.execute(
                """
                SELECT tracking_id, origin_cep, destination_cep, service, status, weight_kg
                FROM shipments WHERE tracking_id = ?
                """,
                (tracking_id,),
            ).fetchone()
            if shipment is None:
                return None
            events = conn.execute(
                """
                SELECT event_at, location, description
                FROM tracking_events
                WHERE tracking_id = ?
                ORDER BY event_at ASC
                """,
                (tracking_id,),
            ).fetchall()
        result = dict(shipment)
        result["events"] = [dict(e) for e in events]
        return result

    def list_shipments(
        self,
        status: str | None = None,
        origin: str | None = None,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT tracking_id, origin_cep, destination_cep, service, status, weight_kg
            FROM shipments WHERE 1=1
        """
        params: list[Any] = []
        if status is not None:
            query += " AND status = ?"
            params.append(status)
        if origin is not None:
            query += " AND origin_cep = ?"
            params.append(origin)
        query += " ORDER BY created_at DESC"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
