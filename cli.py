#!/usr/bin/env python3
"""
Binance Futures Testnet Trading Bot — CLI entry point.

Usage examples:
  python cli.py place-order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
  python cli.py place-order --symbol BTCUSDT --side SELL --type LIMIT  --quantity 0.001 --price 50000
  python cli.py place-order --symbol ETHUSDT --side BUY --type STOP_LIMIT --quantity 0.01 --price 2900 --stop-price 2950
"""

import json
import os
import sys

import click

from bot.client import BinanceAPIError, BinanceFuturesClient, BinanceNetworkError
from bot.logging_config import setup_logging
from bot.orders import place_limit_order, place_market_order, place_stop_limit_order
from bot.validators import ValidationError

BANNER = """
╔══════════════════════════════════════════════════╗
║   Binance Futures Testnet Trading Bot            ║
║   Base URL: https://testnet.binancefuture.com    ║
╚══════════════════════════════════════════════════╝
"""


def _get_client() -> BinanceFuturesClient:
    api_key = os.environ.get("BINANCE_API_KEY", "").strip()
    api_secret = os.environ.get("BINANCE_API_SECRET", "").strip()
    if not api_key or not api_secret:
        click.echo(
            click.style(
                "\n[ERROR] BINANCE_API_KEY and BINANCE_API_SECRET environment variables must be set.\n"
                "  Export them before running:\n"
                "    export BINANCE_API_KEY=your_key\n"
                "    export BINANCE_API_SECRET=your_secret\n",
                fg="red",
            ),
            err=True,
        )
        sys.exit(1)
    return BinanceFuturesClient(api_key=api_key, api_secret=api_secret)


def _print_summary(label: str, data: dict) -> None:
    click.echo(click.style(f"\n{'─' * 50}", fg="cyan"))
    click.echo(click.style(f"  {label}", fg="cyan", bold=True))
    click.echo(click.style(f"{'─' * 50}", fg="cyan"))
    for key, value in data.items():
        if value is not None and value != "" and value != "0":
            click.echo(f"  {key:<20} {value}")
    click.echo(click.style(f"{'─' * 50}\n", fg="cyan"))


def _print_order_request(params: dict) -> None:
    click.echo(click.style("\n  Order Request Summary", fg="yellow", bold=True))
    click.echo(click.style("  " + "─" * 40, fg="yellow"))
    for k, v in params.items():
        if v is not None:
            click.echo(f"  {k:<20} {v}")


def _print_order_response(result: dict) -> None:
    click.echo(click.style("\n  Order Response", fg="green", bold=True))
    click.echo(click.style("  " + "─" * 40, fg="green"))
    fields = [
        ("Order ID", result.get("orderId")),
        ("Client Order ID", result.get("clientOrderId")),
        ("Symbol", result.get("symbol")),
        ("Side", result.get("side")),
        ("Type", result.get("type")),
        ("Status", result.get("status")),
        ("Orig Qty", result.get("origQty")),
        ("Executed Qty", result.get("executedQty")),
        ("Avg Price", result.get("avgPrice")),
        ("Price", result.get("price")),
        ("Stop Price", result.get("stopPrice")),
        ("Time In Force", result.get("timeInForce")),
    ]
    for label, value in fields:
        if value is not None and str(value) not in ("", "0", "0.00000000"):
            click.echo(f"  {label:<20} {value}")


@click.group()
@click.option("--log-level", default="INFO", show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help="Log level written to logs/trading_bot.log")
@click.pass_context
def cli(ctx, log_level):
    ctx.ensure_object(dict)
    logger = setup_logging(log_level)
    ctx.obj["logger"] = logger
    click.echo(click.style(BANNER, fg="cyan"))


@cli.command("place-order")
@click.option("--symbol",     required=True, help="Trading pair, e.g. BTCUSDT")
@click.option("--side",       required=True, type=click.Choice(["BUY", "SELL"], case_sensitive=False), help="Order side")
@click.option("--type",  "order_type", required=True,
              type=click.Choice(["MARKET", "LIMIT", "STOP_LIMIT"], case_sensitive=False),
              help="Order type")
@click.option("--quantity",   required=True, help="Order quantity (base asset)")
@click.option("--price",      default=None,  help="Limit price (required for LIMIT and STOP_LIMIT)")
@click.option("--stop-price", default=None,  help="Stop trigger price (required for STOP_LIMIT)")
@click.option("--tif",        default="GTC", show_default=True,
              type=click.Choice(["GTC", "IOC", "FOK"], case_sensitive=False),
              help="Time-in-force for LIMIT / STOP_LIMIT orders")
@click.option("--json-output", is_flag=True, default=False, help="Print raw JSON response instead of formatted output")
@click.pass_context
def place_order(ctx, symbol, side, order_type, quantity, price, stop_price, tif, json_output):
    """Place a MARKET, LIMIT, or STOP_LIMIT order on Binance Futures Testnet."""
    logger = ctx.obj["logger"]
    order_type = order_type.upper()
    side = side.upper()

    request_params = {
        "symbol":     symbol.upper(),
        "side":       side,
        "type":       order_type,
        "quantity":   quantity,
        "price":      price,
        "stop_price": stop_price,
        "tif":        tif if order_type != "MARKET" else None,
    }

    _print_order_request(request_params)

    client = _get_client()

    try:
        if order_type == "MARKET":
            result = place_market_order(client, symbol, side, quantity)
        elif order_type == "LIMIT":
            if not price:
                raise ValidationError("--price is required for LIMIT orders.")
            result = place_limit_order(client, symbol, side, quantity, price, tif)
        elif order_type == "STOP_LIMIT":
            if not price:
                raise ValidationError("--price is required for STOP_LIMIT orders.")
            if not stop_price:
                raise ValidationError("--stop-price is required for STOP_LIMIT orders.")
            result = place_stop_limit_order(client, symbol, side, quantity, price, stop_price, tif)
        else:
            raise ValidationError(f"Unsupported order type: {order_type}")

    except ValidationError as exc:
        click.echo(click.style(f"\n  [VALIDATION ERROR] {exc}\n", fg="red"), err=True)
        logger.error("Validation error: %s", exc)
        sys.exit(2)

    except BinanceAPIError as exc:
        click.echo(
            click.style(f"\n  [API ERROR] Code {exc.code}: {exc.message}\n", fg="red"), err=True
        )
        logger.error("API error: code=%s msg=%s", exc.code, exc.message)
        sys.exit(3)

    except BinanceNetworkError as exc:
        click.echo(click.style(f"\n  [NETWORK ERROR] {exc}\n", fg="red"), err=True)
        logger.error("Network error: %s", exc)
        sys.exit(4)

    except Exception as exc:
        click.echo(click.style(f"\n  [UNEXPECTED ERROR] {exc}\n", fg="red"), err=True)
        logger.exception("Unexpected error: %s", exc)
        sys.exit(5)

    if json_output:
        click.echo(json.dumps(result, indent=2))
    else:
        _print_order_response(result)
        status = result.get("status", "UNKNOWN")
        color = "green" if status in ("FILLED", "NEW", "PARTIALLY_FILLED") else "yellow"
        click.echo(
            click.style(f"  ✓ Order placed successfully — status: {status}\n", fg=color, bold=True)
        )


@cli.command("account")
@click.pass_context
def account(ctx):
    """Show Futures account balances."""
    logger = ctx.obj["logger"]
    client = _get_client()
    try:
        data = client.get_account()
    except BinanceAPIError as exc:
        click.echo(click.style(f"\n  [API ERROR] {exc.code}: {exc.message}\n", fg="red"), err=True)
        logger.error("Account fetch error: %s", exc)
        sys.exit(3)
    except BinanceNetworkError as exc:
        click.echo(click.style(f"\n  [NETWORK ERROR] {exc}\n", fg="red"), err=True)
        sys.exit(4)

    assets = [a for a in data.get("assets", []) if float(a.get("walletBalance", 0)) > 0]
    if not assets:
        click.echo("  No non-zero balances found.")
        return

    click.echo(click.style("\n  Account Balances\n  " + "─" * 40, fg="cyan"))
    for a in assets:
        click.echo(
            f"  {a['asset']:<10}  wallet: {a['walletBalance']:<20}  unrealized PnL: {a.get('unrealizedProfit', 'N/A')}"
        )
    click.echo()


if __name__ == "__main__":
    cli(obj={})
