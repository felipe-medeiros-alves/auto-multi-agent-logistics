def test_get_rates_returns_cheapest_first(repo):
    rates = repo.get_rates("01310-000", "22041-080", 2.5)
    assert len(rates) >= 1
    assert rates[0]["service"] in ("PAC", "SEDEX")
    prices = [r["price_brl"] for r in rates]
    assert prices == sorted(prices)


def test_get_rates_filters_by_service(repo):
    rates = repo.get_rates("01310-000", "22041-080", 1.0, service="PAC")
    assert all(r["service"] == "PAC" for r in rates)


def test_get_tracking_found(repo):
    t = repo.get_tracking("BR123456789BR")
    assert t is not None
    assert t["tracking_id"] == "BR123456789BR"
    assert "status" in t


def test_get_tracking_not_found(repo):
    assert repo.get_tracking("BR000000000BR") is None


def test_list_shipments_by_status(repo):
    rows = repo.list_shipments(status="in_transit")
    assert len(rows) >= 1
    assert all(r["status"] == "in_transit" for r in rows)


def test_sql_injection_in_cep_treated_as_literal(repo):
    malicious = "01310-000'; DROP TABLE shipments; --"
    rates = repo.get_rates(malicious, "22041-080", 1.0)
    assert rates == []
    still = repo.list_shipments()
    assert isinstance(still, list)
