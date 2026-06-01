import logging
from typing import Any, Dict, Optional

from .client import BinanceFuturesClient
from .validators import validate_order_params

logger = logging.getLogger("trading_bot.orders")


def _format_response(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "orderId": data.get("orderId"),
        "clientOrderId": data.get("clientOrderId"),
        "symbol": data.get("symbol"),
        "side": data.get("side"),
        "type": data.get("type"),
        "origQty": data.get("origQty"),
        "executedQty": data.get("executedQty"),
        "price": data.get("price"),
        "avgPrice": data.get("avgPrice"),
        "stopPrice": data.get("stopPrice"),
        "status": data.get("status"),
        "timeInForce": data.get("timeInForce"),
        "updateTime": data.get("updateTime"),
    }


def place_market_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: str,
) -> Dict[str, Any]:
    params = validate_order_params(
        symbol=symbol, side=side, order_type="MARKET", quantity=quantity
    )
    logger.info(
        "Placing MARKET order: symbol=%s side=%s qty=%s",
        params["symbol"],
        params["side"],
        params["quantity"],
    )
    raw = client.new_order(
        symbol=params["symbol"],
        side=params["side"],
        type="MARKET",
        quantity=params["quantity"],
    )
    result = _format_response(raw)
    logger.info("MARKET order placed successfully: orderId=%s status=%s", result["orderId"], result["status"])
    return result


def place_limit_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: str,
    price: str,
    time_in_force: str = "GTC",
) -> Dict[str, Any]:
    params = validate_order_params(
        symbol=symbol, side=side, order_type="LIMIT", quantity=quantity, price=price
    )
    logger.info(
        "Placing LIMIT order: symbol=%s side=%s qty=%s price=%s tif=%s",
        params["symbol"],
        params["side"],
        params["quantity"],
        params["price"],
        time_in_force,
    )
    raw = client.new_order(
        symbol=params["symbol"],
        side=params["side"],
        type="LIMIT",
        quantity=params["quantity"],
        price=params["price"],
        timeInForce=time_in_force,
    )
    result = _format_response(raw)
    logger.info("LIMIT order placed successfully: orderId=%s status=%s", result["orderId"], result["status"])
    return result


def place_stop_limit_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    quantity: str,
    price: str,
    stop_price: str,
    time_in_force: str = "GTC",
) -> Dict[str, Any]:
    params = validate_order_params(
        symbol=symbol,
        side=side,
        order_type="STOP_LIMIT",
        quantity=quantity,
        price=price,
        stop_price=stop_price,
    )
    logger.info(
        "Placing STOP_LIMIT order: symbol=%s side=%s qty=%s price=%s stopPrice=%s tif=%s",
        params["symbol"],
        params["side"],
        params["quantity"],
        params["price"],
        params["stop_price"],
        time_in_force,
    )
    raw = client.new_order(
        symbol=params["symbol"],
        side=params["side"],
        type="STOP",
        quantity=params["quantity"],
        price=params["price"],
        stopPrice=params["stop_price"],
        timeInForce=time_in_force,
    )
    result = _format_response(raw)
    logger.info(
        "STOP_LIMIT order placed successfully: orderId=%s status=%s",
        result["orderId"],
        result["status"],
    )
    return result
