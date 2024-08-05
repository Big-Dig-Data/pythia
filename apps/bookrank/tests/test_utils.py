import pytest
from decimal import Decimal

from ..logic.work_copies import format_price


PRICE_SAMPLES = [
    '1001.00',
    "250,- KČ",
    '143.75 GBP',
    "43,50 Eur",
    '7687/3SV',
    '123.23 DM/3SV',
    None,
]
EXPECTED_PRICES = [
    (Decimal('1001.00'), 'CZK'),
    (Decimal("250"), 'CZK'),
    (Decimal('143.75'), 'GBP'),
    (Decimal("43.50"), 'EUR'),
    (Decimal('7687'), 'CZK'),
    (Decimal('123.23'), 'DM'),
    (None, None),
]


@pytest.mark.django_db()
class TestWorkCopiesUtils:
    def test_format_price(self):
        expected = [format_price(p) for p in PRICE_SAMPLES]
        assert expected == EXPECTED_PRICES
