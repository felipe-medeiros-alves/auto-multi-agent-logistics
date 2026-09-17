import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS rates (
    id INTEGER PRIMARY KEY,
    origin_cep TEXT NOT NULL,
    destination_cep TEXT NOT NULL,
    service TEXT NOT NULL,
    max_weight_kg REAL NOT NULL,
    price_brl REAL NOT NULL,
    eta_days INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS shipments (
    id INTEGER PRIMARY KEY,
    tracking_id TEXT NOT NULL UNIQUE,
    origin_cep TEXT NOT NULL,
    destination_cep TEXT NOT NULL,
    service TEXT NOT NULL,
    status TEXT NOT NULL,
    weight_kg REAL NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tracking_events (
    id INTEGER PRIMARY KEY,
    tracking_id TEXT NOT NULL,
    event_at TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT NOT NULL,
    FOREIGN KEY (tracking_id) REFERENCES shipments(tracking_id)
);
"""

SEED_RATES = [
    ("01310-000", "22041-080", "PAC", 30.0, 45.90, 8),
    ("01310-000", "22041-080", "SEDEX", 30.0, 89.50, 3),
    ("01310-000", "30130-000", "PAC", 30.0, 52.00, 10),
    ("01310-000", "30130-000", "SEDEX", 30.0, 95.00, 4),
]

SEED_SHIPMENTS = [
    (
        "BR123456789BR",
        "01310-000",
        "22041-080",
        "SEDEX",
        "in_transit",
        2.5,
        "2026-09-10T10:00:00Z",
    ),
    (
        "BR987654321BR",
        "01310-000",
        "30130-000",
        "PAC",
        "delivered",
        1.2,
        "2026-09-01T08:00:00Z",
    ),
]

SEED_EVENTS = [
    (
        "BR123456789BR",
        "2026-09-10T12:00:00Z",
        "São Paulo, SP",
        "Objeto postado",
    ),
    (
        "BR123456789BR",
        "2026-09-12T09:00:00Z",
        "Campinas, SP",
        "Objeto em trânsito",
    ),
    (
        "BR987654321BR",
        "2026-09-01T10:00:00Z",
        "São Paulo, SP",
        "Objeto postado",
    ),
    (
        "BR987654321BR",
        "2026-09-05T14:00:00Z",
        "Belo Horizonte, MG",
        "Objeto entregue",
    ),
]


def init_database(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
        conn.execute("DELETE FROM tracking_events")
        conn.execute("DELETE FROM shipments")
        conn.execute("DELETE FROM rates")
        conn.executemany(
            """
            INSERT INTO rates (
                origin_cep, destination_cep, service, max_weight_kg, price_brl, eta_days
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            SEED_RATES,
        )
        conn.executemany(
            """
            INSERT INTO shipments (
                tracking_id, origin_cep, destination_cep, service, status, weight_kg, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            SEED_SHIPMENTS,
        )
        conn.executemany(
            """
            INSERT INTO tracking_events (tracking_id, event_at, location, description)
            VALUES (?, ?, ?, ?)
            """,
            SEED_EVENTS,
        )
        conn.commit()
    finally:
        conn.close()
