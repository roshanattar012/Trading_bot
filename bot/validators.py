import re
from decimal import Decimal, InvalidOperation
from typing import Optional


VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_LIMIT"}
SYMBOL_RE = re.compile(r"^[A-Z]{2,20}$")


class ValidationError(Exception):
    pass


def validate_symbol(symbol: str) -> str:
    s = symbol.strip().upper()
    if not SYMBOL_RE.match(s):
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Must be uppercase letters only (e.g. BTCUSDT)."
        )
    return s


def validate_side(side: str) -> str:
    s = side.strip().upper()
    if s not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side '{side}'. Must be one of: {', '.join(sorted(VALID_SIDES))}."
        )
    return s


def validate_order_type(order_type: str) -> str:
    t = order_type.strip().upper()
    if t not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    return t


def validate_quantity(quantity: str) -> str:
    try:
        q = Decimal(str(quantity))
    except InvalidOperation:
        raise ValidationError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if q <= 0:
        raise ValidationError(f"Quantity must be greater than zero, got {quantity}.")
    return str(q)


def validate_price(price: Optional[str]) -> Optional[str]:
    if price is None:
        return None
    try:
        p = Decimal(str(price))
    except InvalidOperation:
        raise ValidationError(f"Invalid price '{price}'. Must be a positive number.")
    if p <= 0:
        raise ValidationError(f"Price must be greater than zero, got {price}.")
    return str(p)


def validate_stop_price(stop_price: Optional[str]) -> Optional[str]:
    if stop_price is None:
        return None
    try:
        p = Decimal(str(stop_price))
    except InvalidOperation:
        raise ValidationError(f"Invalid stop price '{stop_price}'. Must be a positive number.")
    if p <= 0:
        raise ValidationError(f"Stop price must be greater than zero, got {stop_price}.")
    return str(p)


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
    stop_price: Optional[str] = None,
) -> dict:
    result = {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validate_order_type(order_type),
        "quantity": validate_quantity(quantity),
        "price": validate_price(price),
        "stop_price": validate_stop_price(stop_price),
    }

    if result["order_type"] == "LIMIT" and result["price"] is None:
        raise ValidationError("Price is required for LIMIT orders.")

    if result["order_type"] == "STOP_LIMIT":
        if result["price"] is None:
            raise ValidationError("Price (limit price) is required for STOP_LIMIT orders.")
        if result["stop_price"] is None:
            raise ValidationError("Stop price is required for STOP_LIMIT orders.")

    return result
