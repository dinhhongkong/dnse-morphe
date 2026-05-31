# AGENTS.md

## Project Overview

`dnse-morphe` is a Python library for DNSE LightSpeed API V2, providing REST and WebSocket interfaces for Vietnam Stock Exchange trading.

- **Python**: `>=3.12`
- **Package Manager**: `uv`
- **REST**: `https://openapi.dnse.com.vn`
- **WebSocket**: `wss://ws-openapi.dnse.com.vn` (prod), `wss://ws-openapi-uat.dnse.com.vn` (UAT)

## Project Structure

```
src/dnse_morphe/
├── __init__.py              # Public exports
├── _base_client.py          # HTTP client with HMAC auth
├── _client.py               # Sync client
├── _async_client.py         # Async client
├── _constants.py            # URLs, timeouts, headers
├── _exception.py            # Exception hierarchy
├── _utils/                  # Utilities
│   ├── __init__.py
│   ├── _logs.py             # Logging setup
│   └── _utils.py            # is_dict helper
├── resources/               # API endpoints
│   ├── _accounts.py
│   ├── _orders.py
│   ├── _market_data.py
│   └── _websocket.py
└── types/                   # Pydantic models
    ├── _account.py
    ├── _order.py
    ├── _market.py
    └── _websocket.py
```

## Commands

```bash
# Install dependencies
uv sync

# Lint & format
uv run ruff check src/
uv run ruff check src/ --fix
uv run ruff format src/

# Type check
uv run mypy src/

# All checks (CI)
uv run ruff check src/ && uv run ruff format --check src/ && uv run mypy src/
```

## Code Style

- Use `from __future__ import annotations` at top of every module.
- Import ordering: stdlib → third-party → local (use `ruff` to auto-sort).
- All public methods MUST have type hints.
- Private modules start with `_` prefix.
- Use `Decimal` for monetary/price fields.
- Models MUST have `from_dict` classmethod handling both abbreviated (`s`, `p`) and full (`symbol`, `price`) field names.
- Never expose raw `httpx` or `websockets` exceptions.

## Client Architecture

```
_base_client.py   → Shared HTTP logic with HMAC signature
_client.py        → Sync client (websocket() returns WebSocket)
_async_client.py  → Async client (websocket() returns WebSocket)
```

Both clients provide `websocket()` method returning a `WebSocket` instance. Users handle async context:

```python
async with client.websocket() as ws:
    await ws.subscribe_trades(["VND"])
    await asyncio.sleep(60)
```

## WebSocket

- JSON and MessagePack encoding supported.
- Channel names: `tick.G1.json`, `top_price.G1.msgpack`, etc.
- Message types: `t`=trade, `q`=quote, `b`=ohlc, `o`=order, `p`=position, `a`=account.
- Auto-reconnect with exponential backoff.
- Use `DNSE_MORPHE_LOG=debug|info` for logging.

## Reference SDK

- `sdk/dnse/client.py` — REST API patterns
- `sdk/websocket-marketdata/trading_websocket/` — WebSocket patterns
- `sdk/websocket-marketdata/trading_websocket/models.py` — model field naming
