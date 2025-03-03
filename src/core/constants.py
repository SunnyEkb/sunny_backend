from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class LimitsValues:
    MIN_VALUE_PRICE: Decimal = Decimal("0")
    DECIMAL_PLACES_PRICE: int = 2
    MAX_DIGITS_PRICE: int = 10
    MAX_LENGTH_SUBSERVICE_TITLE: int = 255
