import pytest

from logistics_crew.shipping.repository import ShippingRepository
from logistics_crew.shipping.seed import init_database


@pytest.fixture
def repo(tmp_path):
    db_path = tmp_path / "shipping.db"
    init_database(db_path)
    return ShippingRepository(db_path)
