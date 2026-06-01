# Binance Futures Testnet Trading Bot

A clean Python CLI application that places orders on [Binance Futures Testnet (USDT-M)](https://testnet.binancefuture.com).

---

## Features

| Capability | Detail |
|---|---|
| Order types | MARKET, LIMIT, STOP_LIMIT (bonus) |
| Sides | BUY / SELL |
| CLI | Click-powered with validation messages |
| Logging | Rotating file log at `logs/trading_bot.log` |
| Error handling | Validation errors, API errors, network failures |
| Account info | View non-zero Futures balances |

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST client (HMAC signing, request/response logging)
│   ├── orders.py          # Order placement logic (market, limit, stop-limit)
│   ├── validators.py      # Input validation with clear error messages
│   └── logging_config.py  # Rotating file + console log handler setup
├── cli.py                 # Click CLI entry point
├── logs/                  # Auto-created; trading_bot.log written here
├── README.md
└── requirements.txt
```

---

## Setup

### 1. Get Testnet API Credentials

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in with GitHub or create an account
3. Navigate to **API Key** → generate a new key pair
4. Copy your **API Key** and **Secret Key**

### 2. Install Dependencies

```bash
cd trading_bot
pip install -r requirements.txt
```

Python 3.8+ required. No external Binance SDK needed — uses `requests` directly.

### 3. Set Environment Variables

```bash
export BINANCE_API_KEY=your_api_key_here
export BINANCE_API_SECRET=your_api_secret_here
```

Or on Windows:
```cmd
set BINANCE_API_KEY=your_api_key_here
set BINANCE_API_SECRET=your_api_secret_here
```

---

## Usage

### Place a MARKET order

```bash
python cli.py place-order \
  --symbol BTCUSDT \
  --side BUY \
  --type MARKET \
  --quantity 0.001
```

### Place a LIMIT order

```bash
python cli.py place-order \
  --symbol BTCUSDT \
  --side SELL \
  --type LIMIT \
  --quantity 0.001 \
  --price 50000
```

### Place a STOP_LIMIT order (bonus)

```bash
python cli.py place-order \
  --symbol ETHUSDT \
  --side BUY \
  --type STOP_LIMIT \
  --quantity 0.01 \
  --price 2900 \
  --stop-price 2950
```

### View account balances

```bash
python cli.py account
```

### All options

```bash
python cli.py place-order --help
```

```
Options:
  --symbol TEXT                    Trading pair, e.g. BTCUSDT  [required]
  --side [BUY|SELL]                Order side  [required]
  --type [MARKET|LIMIT|STOP_LIMIT] Order type  [required]
  --quantity TEXT                  Order quantity (base asset)  [required]
  --price TEXT                     Limit price (required for LIMIT and STOP_LIMIT)
  --stop-price TEXT                Stop trigger price (required for STOP_LIMIT)
  --tif [GTC|IOC|FOK]             Time-in-force  [default: GTC]
  --json-output                    Print raw JSON response
  --log-level [DEBUG|INFO|WARNING|ERROR]  [default: INFO]
```

---

## Sample Output

```
╔══════════════════════════════════════════════════╗
║   Binance Futures Testnet Trading Bot            ║
║   Base URL: https://testnet.binancefuture.com    ║
╚══════════════════════════════════════════════════╝

  Order Request Summary
  ────────────────────────────────────────
  symbol               BTCUSDT
  side                 BUY
  type                 MARKET
  quantity             0.001

  Order Response
  ────────────────────────────────────────
  Order ID             123456789
  Symbol               BTCUSDT
  Side                 BUY
  Type                 MARKET
  Status               FILLED
  Orig Qty             0.001
  Executed Qty         0.001
  Avg Price            43215.60

  ✓ Order placed successfully — status: FILLED
```

---

## Logging

All API requests, responses, and errors are written to `logs/trading_bot.log`.

Log format:
```
YYYY-MM-DD HH:MM:SS | LEVEL    | logger.name | message
```

Example entries:
```
2024-01-15 10:23:01 | INFO     | trading_bot.client | REQUEST  POST /fapi/v1/order  params={'symbol': 'BTCUSDT', 'side': 'BUY', 'type': 'MARKET', 'quantity': '0.001', 'timestamp': 1705312981000}
2024-01-15 10:23:01 | INFO     | trading_bot.client | RESPONSE POST /fapi/v1/order  status=200  body={"orderId":123456789,...}
2024-01-15 10:23:01 | INFO     | trading_bot.orders | MARKET order placed successfully: orderId=123456789 status=FILLED
```

Log files rotate automatically at 5 MB, keeping the last 3 files.

---

## Error Handling

| Error type | Exit code | Example |
|---|---|---|
| Validation error | 2 | Missing --price for LIMIT order |
| Binance API error | 3 | Invalid symbol, insufficient balance |
| Network error | 4 | Timeout, connection refused |
| Unexpected error | 5 | Any other exception |

---

## Assumptions

- Testnet only — base URL is hardcoded to `https://testnet.binancefuture.com` (USDT-M Futures)
- Credentials are read from environment variables (never hard-coded)
- Quantity precision must match the symbol's `stepSize` filter; the testnet is more lenient than production
- `STOP_LIMIT` maps to Binance's `STOP` type (limit order triggered at stop price)
- Time-in-force defaults to `GTC` for LIMIT and STOP_LIMIT orders

---

## Requirements

```
requests>=2.31.0
click>=8.1.7
```
