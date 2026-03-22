# dnse-morphe

Python library for DNES LightSpeed API V2 trading API with full sync and async support.

## Features

- **REST API**: Account management, orders, market data
- **WebSocket**: Real-time market data streaming (trades, quotes, OHLC)
- **Sync & Async**: Both sync and async clients available
- **Pydantic Models**: Type-safe data models with validation
- **HMAC Authentication**: Secure API authentication

## Installation

```bash
pip install dnse-morphe
```

Or install from source:

```bash
pip install -e .
```

## Quick Start

### REST API Client

```python
from dnse_morphe import DNSEClient

# Initialize client
client = DNSEClient(
    api_key="your_api_key",
    api_secret="your_api_secret",
    base_url="https://openapi.dnse.com.vn",  # optional
)

# List accounts
accounts = client.accounts.list()
for account in accounts:
    print(f"Account: {account.account_no} - {account.account_name}")

# Get account balances
balances = client.accounts.list_balances(account_no="YOUR_ACCOUNT")
print(f"Cash Balance: {balances[0].cash_balance}")

# Get market data
sec_def = client.market_data.get_security_definition("VND")
print(f"Symbol: {sec_def.symbol}, Ceiling: {sec_def.ceiling_price}")

# Get OHLC data
ohlc_list = client.market_data.get_ohlc(
    bar_type="stock",
    symbol="VND",
    resolution="1m",
    from_date="2024-01-01",
    to_date="2024-01-02",
)
for ohlc in ohlc_list:
    print(f"{ohlc.time}: O={ohlc.open} H={ohlc.high} L={ohlc.low} C={ohlc.close}")
```

### Async Client

```python
import asyncio
from dnse_morphe import AsyncDNSEClient

async def main():
    client = AsyncDNSEClient(
        api_key="your_api_key",
        api_secret="your_api_secret",
    )

    # List accounts
    accounts = await client.accounts.list()
    print(f"Found {len(accounts)} accounts")

asyncio.run(main())
```

### WebSocket Streaming

```python
import asyncio
from dnse_morphe import AsyncDNSEClient

async def main():
    client = AsyncDNSEClient(
        api_key="your_api_key",
        api_secret="your_api_secret",
        base_url="wss://ws-openapi-uat.dnse.com.vn",  # UAT environment
    )

    async with client.websocket() as ws:
        # Subscribe to trades
        await ws.subscribe_trades(["VND", "HPG"], encoding="json")

        # Subscribe to quotes
        await ws.subscribe_quotes(["VND", "HPG"])

        # Register handlers
        def on_trade(trade):
            print(f"Trade: {trade.symbol} @ {trade.price}, Qty: {trade.quantity}")

        def on_quote(quote):
            print(f"Quote: {quote.symbol} | Bid: {quote.best_bid} | Ask: {quote.best_ask}")

        ws.on("trade", on_trade)
        ws.on("quote", on_quote)

        # Keep connection alive
        await asyncio.sleep(60)

asyncio.run(main())
```

### Placing Orders

```python
from dnse_morphe import DNSEClient
from dnse_morphe.types import OrderRequest

client = DNSEClient(
    api_key="your_api_key",
    api_secret="your_api_secret",
)

# Create trading token (first time only)
token_data = client.orders.create_trading_token(
    otp_type="EMAIL",
    passcode="your_passcode",
)

# Place order
order_request = OrderRequest(
    account_no="YOUR_ACCOUNT",
    symbol="VND",
    side="BUY",
    order_type="LO",
    price=50.0,
    quantity=100,
)

response = client.orders.create(
    market_type="stock",
    order_request=order_request,
    trading_token="your_trading_token",
)

print(f"Order ID: {response.order_id}, Status: {response.status}")

# Cancel order
cancel_response = client.orders.cancel(
    account_no="YOUR_ACCOUNT",
    order_id=response.order_id,
    market_type="stock",
    trading_token="your_trading_token",
)
```

## API Reference

### Client Initialization

```python
from dnse_morphe import DNSEClient, AsyncDNSEClient

# Sync client
client = DNSEClient(
    api_key="your_api_key",
    api_secret="your_api_secret",
    base_url="https://openapi.dnse.com.vn",  # optional, default: prod
    hmac_nonce_enabled=True,  # optional, default: True
    timeout=30.0,  # optional, HTTP timeout
)

# Async client
async_client = AsyncDNSEClient(
    api_key="your_api_key",
    api_secret="your_api_secret",
    base_url="https://openapi.dnse.com.vn",
)
```

### Available Endpoints

#### Accounts

```python
# List all accounts
accounts = client.accounts.list()

# Get account balances
balances = client.accounts.list_balances(account_no="ACCOUNT123")

# Get deals
deals = client.accounts.list_deals(account_no="ACCOUNT123", market_type="stock")

# Get loan packages
packages = client.accounts.list_loan_packages(
    account_no="ACCOUNT123",
    market_type="stock",
    symbol="VND",
)

# Calculate PPSE
ppse = client.accounts.get_ppse(
    account_no="ACCOUNT123",
    market_type="stock",
    symbol="VND",
    price=50.0,
    loan_package_id=123,
)
```

#### Orders

```python
# List active orders
orders = client.orders.list(account_no="ACCOUNT123", market_type="stock")

# Get order detail
order = client.orders.get(
    account_no="ACCOUNT123",
    order_id="ORDER123",
    market_type="stock",
)

# List order history
history = client.orders.list_history(
    account_no="ACCOUNT123",
    market_type="stock",
    from_date="2024-01-01",
    to_date="2024-12-31",
)

# Close deal
close_response = client.orders.close_deal(
    deal_id="DEAL123",
    account_no="ACCOUNT123",
    market_type="stock",
    payload={"close_quantity": 50},
    trading_token="TOKEN",
)
```

#### Market Data

```python
# Get security definition
sec_def = client.market_data.get_security_definition(
    symbol="VND",
    board_id="HOSE",  # optional
)

# Get OHLC data
ohlc = client.market_data.get_ohlc(
    bar_type="stock",
    symbol="VND",
    from_date="2024-01-01",
    to_date="2024-01-02",
    resolution="1m",  # 1m, 5m, 15m, 30m, 1h, 1d, 1w
    page_size=100,
    page_index=1,
)
```

### WebSocket Channels

```python
from dnse_morphe import AsyncDNSEClient

async def main():
    client = AsyncDNSEClient(
        api_key="your_api_key",
        api_secret="your_api_secret",
    )

    async with client.websocket(encoding="json") as ws:
        # Market data channels
        await ws.subscribe_trades(["VND", "HPG", "VHM"])
        await ws.subscribe_quotes(["VND", "HPG"])
        await ws.subscribe_ohlc(["VND"], resolution="1m")
        await ws.subscribe_expected_price(["VND"])
        await ws.subscribe_sec_def(["VND", "HPG"])

        # Private channels
        await ws.subscribe_orders()
        await ws.subscribe_positions()
        await ws.subscribe_account()

        # Register event handlers
        ws.on("trade", lambda t: print(f"Trade: {t}"))
        ws.on("quote", lambda q: print(f"Quote: {q}"))
        ws.on("order", lambda o: print(f"Order: {o}"))

        await asyncio.sleep(3600)  # Keep connected

asyncio.run(main())
```

### Data Models

All API responses are parsed into Pydantic models with full type hints:

```python
from dnse_morphe.types import Account, Balance, Order, Trade, Quote

# Access attributes directly
account: Account
print(account.account_no)
print(account.status)

trade: Trade
print(trade.symbol)
print(trade.price)
print(trade.quantity)

quote: Quote
print(quote.best_bid)    # (price, quantity) tuple
print(quote.best_ask)    # (price, quantity) tuple
print(quote.spread)      # bid-ask spread
```

## Configuration

### Environment Variables

```bash
# Logging level
DNSE_MORPHE_LOG=debug  # or info

# Example
DNSE_MORPHE_LOG=info python your_script.py
```

### Environments

```python
# Production
client = DNSEClient(
    api_key="...",
    api_secret="...",
    base_url="https://openapi.dnse.com.vn",
)

# UAT (WebSocket)
async_client = AsyncDNSEClient(
    api_key="...",
    api_secret="...",
    base_url="wss://ws-openapi-uat.dnse.com.vn",
)
```

## Error Handling

```python
from dnse_morphe import DNSEClient
from dnse_morphe._exception import APIError, AuthenticationError, RateLimitError

client = DNSEClient(
    api_key="your_api_key",
    api_secret="your_api_secret",
)

try:
    accounts = client.accounts.list()
except AuthenticationError:
    print("Invalid API credentials")
except RateLimitError:
    print("Rate limit exceeded, try again later")
except APIError as e:
    print(f"API Error: {e.status} - {e.body}")
```

## Development

```bash
# Install dependencies
uv sync

# Install in dev mode
uv pip install -e ".[dev]"

# Run tests
pytest tests/

# Type checking
mypy src/

# Linting
ruff check src/

# Formatting
ruff format src/

# All checks
ruff check src/ && ruff format --check src/ && mypy src/ && pytest tests/
```

## License

MIT License
