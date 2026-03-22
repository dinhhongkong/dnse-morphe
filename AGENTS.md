# AGENTS.md

## Project Overview

`dnse-morphe` is a Python library for DNSE (Dragon Securities) trading API, providing both REST and WebSocket interfaces for Vietnam Stock Exchange trading. The library should follow the **OpenAI Python SDK pattern** with full sync and async support.

- **Python**: `>=3.12`
- **Package Manager**: `uv`
- **Base URLs**: REST `https://openapi.dnse.com.vn`, WebSocket `wss://ws-openapi.dnse.com.vn` (prod), `wss://ws-openapi-uat.dnse.com.vn` (UAT)

## Project Structure

```
src/dnse-morphe/
├── __init__.py              # Top-level exports (dnse package root)
├── _base_client.py         # Base client class (shared sync/async)
├── _client.py               # Sync client (wraps async with to_thread)
├── _async_client.py         # Async client (primary implementation)
├── _constants.py            # API constants (URLs, timeouts, headers)
├── _exception.py            # Custom exception hierarchy
├── _model.py                # Base Pydantic model classes
├── _response.py             # Response/stream wrapper classes
├── _utils/                  # Internal utilities
│   ├── __init__.py          # Re-exports
│   ├── _logs.py             # Logging setup with sensitive header filtering
│   ├── _proxy.py            # LazyProxy for lazy module loading
│   ├── _resources_proxy.py  # Resources lazy-loading proxy
│   ├── _sync.py             # asyncify, to_thread utilities
│   ├── _typing.py           # Type introspection utilities
│   ├── _utils.py            # General helpers (lru_cache, deepcopy_minimal, etc.)
│   ├── _compat.py           # Typing compatibility shims
│   ├── _streams.py          # Sync/async iterator consumption
│   ├── _transform.py        # Data transformation helpers
│   ├── _reflection.py        # Function signature utilities
│   └── _datetime_parse.py   # Date/datetime parsing
├── resources/               # API resource modules (per-endpoint)
│   ├── __init__.py
│   ├── _accounts.py         # Accounts endpoints
│   ├── _orders.py           # Order management endpoints
│   ├── _market_data.py      # OHLC, security definition, etc.
│   └── _websocket.py        # WebSocket streaming
└── types/                   # Pydantic types/models
    ├── __init__.py
    ├── _account.py          # Account, Balance models
    ├── _order.py            # Order, Deal models
    ├── _market.py           # Trade, Quote, OHLC, PriceLevel models
    └── _websocket.py        # WebSocket message models
```

## Build / Test / Lint Commands

```bash
# Install dependencies
uv sync

# Install in dev mode
uv pip install -e ".[dev]"

# Run tests
pytest tests/                    # All tests
pytest tests/ -k test_name       # Single test by name
pytest tests/path/to/test.py    # Single test file
pytest tests/ --cov=src         # With coverage

# Type checking
mypy src/

# Linting (ruff)
ruff check src/
ruff check src/ --fix           # Auto-fix

# Formatting (ruff)
ruff format src/

# All checks (CI simulation)
ruff check src/ && ruff format --check src/ && mypy src/ && pytest tests/
```

## Code Style Guidelines

### Python Version & Imports

- Always use `from __future__ import annotations` at the top of every module.
- Import ordering: stdlib → third-party → local (use `ruff` to auto-sort).
- Use `typing_extensions` for features like `override`, `TypeGuard`, `ParamSpec`, `TypeIs`.
- Do NOT use relative imports beyond the package root (`from dnse_morphe._utils import ...`).
- Private modules start with `_` prefix. Never import private modules from public API.

### Type Annotations

- All public methods/functions MUST have type hints (both args and return).
- Use `Pydantic` models (`BaseModel`) for all API request/response types — see `sdk/websocket-marketdata/trading_websocket/models.py` for field naming conventions.
- Models support **both abbreviated** (MessagePack) and **full** (JSON) field names via `from_dict` pattern:

```python
@dataclass
class Trade:
    symbol: str
    price: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Trade":
        return cls(
            symbol=data.get("s") or data.get("symbol"),
            price=data.get("p", 0.0) or data.get("price", 0.0),
        )
```

- Use `Decimal` for monetary/price fields (see `sdk/websocket-marketdata/trading_websocket/models.py:Ohlc`, `Order`, `Position`).
- Use `Optional[T]` (not `T | None`) for compatibility.
- Use `@overload` for functions with multiple signatures.

### Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Classes | PascalCase | `DNSEClient`, `TradingClient` |
| Methods/functions | snake_case | `get_accounts`, `subscribe_trades` |
| Constants | SCREAMING_SNAKE | `SENSITIVE_HEADERS`, `DEFAULT_TIMEOUT` |
| Private modules | `_` prefix | `_logs.py`, `_model.py` |
| Private members | `_` prefix | `self._api_key`, `self._session_id` |
| Type aliases | PascalCase | `AccountList = list[Account]` |

### Models (Pydantic / dataclasses)

- Use `dataclasses` for lightweight models (matching SDK pattern in `sdk/websocket-marketdata/trading_websocket/models.py`).
- Use `Pydantic BaseModel` for request/response with validation.
- All models MUST have a `from_dict` classmethod that handles both abbreviated and full field names.
- Include docstrings on all model classes and public methods.

### Client Architecture (OpenAI Pattern)

Follow the **dual-client pattern** (sync + async):

```
_async_client.py  → Primary implementation using httpx.AsyncClient
_client.py        → Sync wrapper using to_thread (from _utils/_sync.py)
```

Key patterns from the existing SDK:
- Client `__init__` stores config; `connect()` / `disconnect()` for WebSocket.
- HTTP methods return `(status_code, response_body_text)` tuples or parsed objects.
- `dry_run` parameter on methods for debugging without API calls.
- Environment variable `DNSE_MORPHE_LOG=debug|info` for logging control.

### Error Handling

- Custom exception hierarchy in `_exception.py`:

```python
class DNSEError(Exception):
    """Base exception for all library errors."""
    pass

class APIError(DNSEError):
    def __init__(self, status: int, body: str | None):
        self.status = status
        self.body = body

class AuthenticationError(DNSEError):
    pass

class RateLimitError(DNSEError):
    pass

class WebSocketError(DNSEError):
    pass
```

- Catch `httpx.HTTPStatusError` and convert to `APIError`.
- Never expose raw `httpx` or `websockets` exceptions in public API.
- Log sensitive headers (api-key, authorization) with `<redacted>` — see `_logs.py` `SensitiveHeadersFilter`.
- WebSocket reconnection uses exponential backoff with `max(2^(attempt-1), 60)` delay.

### Logging

- Use `logging.getLogger("dnse-morphe")` for library logs.
- Use `DNSE_MORPHE_LOG=debug|info` env var to control verbosity.
- Filter sensitive headers in log output (`_logs.py:SensitiveHeadersFilter`).
- Log format: `[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s`.

### Async/Sync Utilities

- Use `asyncify()` from `_utils/_sync.py` to wrap blocking functions into async.
- Use `to_thread()` to run blocking I/O in a thread pool.
- Support both sync and async callback handlers (see `TradingClient._emit`).
- Use `asyncio.create_task()` for fire-and-forget async handlers.

### WebSocket Specific

- Support both **JSON** and **MessagePack** encoding.
- Channels use abbreviated names: `tick.G1.json`, `top_price.G1.msgpack`, etc.
- Message types: `t`=trade, `te`=trade_extra, `q`=quote, `b`=ohlc, `o`=order, `p`=position, `a`=account, `sd`=sec_def, `e`=expected_price.
- Auto-reconnect with re-authentication and re-subscription.
- Heartbeat with ping/pong monitoring (`is_healthy` property).
- Context manager (`async with`) and async iterator support.

### Security

- Never log or expose `api_key`, `api_secret`, `authorization` headers.
- HMAC-SHA256 signature construction matches `sdk/dnse/common.py` and `sdk/websocket-marketdata/trading_websocket/auth.py`.
- API credentials must be provided at initialization, never hardcoded.

## Conventions

- All files in `src/dnse-morphe/` are stub/scaffold — implement against the patterns in `sdk/`.
- Reference `sdk/dnse/client.py` for REST API patterns and `sdk/websocket-marketdata/trading_websocket/` for WebSocket patterns.
- The `_utils/` directory should be fully implemented first as other modules depend on it.
- Missing `_utils/` files to create: `_compat.py`, `_streams.py`, `_transform.py`, `_reflection.py`, `_datetime_parse.py`.
- Add `websockets` to dependencies in `pyproject.toml` when implementing WebSocket client.
- Add `msgpack` to dependencies when implementing MessagePack support.
- Add dev dependencies: `pytest`, `pytest-asyncio`, `mypy`, `ruff`, `pytest-cov`.
