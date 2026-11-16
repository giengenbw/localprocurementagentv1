from decimal import Decimal
import pytest
from agents.quotation_agent import Quote,compare_quotes
def test_deterministic_price_deviation():
 rows=compare_quotes([Quote(supplier="A",material_number="M",quantity=10,unit_price=10,currency="EUR"),Quote(supplier="B",material_number="M",quantity=10,unit_price=12,currency="EUR")])
 assert rows[1]["deviation_from_low_pct"]==Decimal("20")
def test_mixed_currency_rejected():
 with pytest.raises(ValueError): compare_quotes([Quote(supplier="A",material_number="M",quantity=1,unit_price=1,currency="EUR"),Quote(supplier="B",material_number="M",quantity=1,unit_price=1,currency="USD")])
