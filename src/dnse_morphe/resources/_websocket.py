from __future__ import annotations

import asyncio
import json
import logging
import ssl
import time
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

import websockets

from dnse_morphe._constants import (
    DEFAULT_HEARTBEAT_INTERVAL,
    DEFAULT_WS_MAX_RETRIES,
    DEFAULT_WS_TIMEOUT,
    WS_BASE_URL_PROD,
)
from dnse_morphe._exception import (
    AuthenticationError,
    SubscriptionError,
)
from dnse_morphe.types import (
    Quote,
    SecurityDefinition,
    Trade,
    WSAccountUpdate,
    WSExpectedPrice,
    WSOrder,
    WSPosition,
    WSTradeExtra,
)

if TYPE_CHECKING:
    from websockets.client import ClientProtocol

    from dnse_morphe._base_client import BaseDNSEClient

    _WSC: type[ClientProtocol] = ClientProtocol
else:
    _WSC = None  # type: ignore[assignment, misc]

logger = logging.getLogger("dnse-morphe")


class MessageEncoder:
    def __init__(self, encoding: str = "json") -> None:
        self.encoding = encoding

    def encode(self, data: dict[str, Any]) -> bytes:
        if self.encoding == "json":
            return json.dumps(data).encode("utf-8")
        import msgpack

        return msgpack.packb(data)  # type: ignore[no-any-return]


class MessageDecoder:
    def __init__(self, encoding: str = "json") -> None:
        self.encoding = encoding

    def decode(self, data: bytes) -> dict[str, Any]:
        if self.encoding == "json":
            return json.loads(data.decode("utf-8"))  # type: ignore[no-any-return]
        import msgpack

        return msgpack.unpackb(data, raw=False)  # type: ignore[no-any-return]


class WebSocket:
    def __init__(
        self,
        client: BaseDNSEClient,
        base_url: str = WS_BASE_URL_PROD,
        encoding: str = "json",
        auto_reconnect: bool = True,
        max_retries: int = DEFAULT_WS_MAX_RETRIES,
        heartbeat_interval: float = DEFAULT_HEARTBEAT_INTERVAL,
        timeout: float = DEFAULT_WS_TIMEOUT,
    ) -> None:
        self._client = client
        self.base_url = base_url
        self.encoding = encoding
        self.auto_reconnect = auto_reconnect
        self.max_retries = max_retries
        self.heartbeat_interval = heartbeat_interval
        self.timeout = timeout

        self._ws: ClientProtocol | None = None
        self._encoder = MessageEncoder(encoding)
        self._decoder = MessageDecoder(encoding)
        self._event_handlers: dict[str, list[Callable]] = {}
        self._subscriptions: dict[str, dict[str, Any]] = {}
        self._is_authenticated = False
        self._session_id: str | None = None
        self._is_running = False
        self._last_pong_time = 0.0
        self._heartbeat_task: asyncio.Task | None = None
        self._message_handler_task: asyncio.Task | None = None

    async def connect(self) -> None:
        url = f"{self.base_url}/v1/stream?encoding={self.encoding}"
        logger.info(f"Connecting to {url}")

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        self._ws = await asyncio.wait_for(
            websockets.connect(  # type: ignore[arg-type]
                url,
                ssl=ssl_context,
                ping_interval=30,
                ping_timeout=30,
                close_timeout=10,
                max_queue=None,
            ),
            timeout=self.timeout,
        )

        welcome = await asyncio.wait_for(self._ws.recv(), timeout=self.timeout)  # type: ignore[union-attr]
        welcome_data = self._decoder.decode(welcome)
        self._session_id = welcome_data.get("session_id") or welcome_data.get("sid")
        logger.info(f"Connected! Session ID: {self._session_id}")

        await self._authenticate()
        self._is_running = True
        self._last_pong_time = time.time()
        self._message_handler_task = asyncio.create_task(self._message_handler())
        if self.heartbeat_interval > 0:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def _authenticate(self) -> None:
        import hashlib
        import hmac

        timestamp = int(time.time())
        nonce = str(int(time.time() * 1000000))
        message = f"{self._client._api_key}:{timestamp}:{nonce}"
        signature = hmac.new(
            self._client._api_secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        auth_msg = {
            "action": "auth",
            "api_key": self._client._api_key,
            "signature": signature,
            "timestamp": timestamp,
            "nonce": nonce,
        }
        await self._ws.send(self._encoder.encode(auth_msg))  # type: ignore[union-attr]

        response = await asyncio.wait_for(self._ws.recv(), timeout=self.timeout)  # type: ignore[union-attr]
        data = self._decoder.decode(response)
        action = data.get("action") or data.get("a")

        if action == "auth_success":
            self._is_authenticated = True
            logger.info("Authentication successful")
        elif action in ("auth_error", "error"):
            msg = data.get("message") or data.get("msg", "Unknown error")
            raise AuthenticationError(f"Authentication failed: {msg}")
        else:
            raise AuthenticationError(f"Unexpected response: {action}")

    def on(self, event: str, handler: Callable) -> None:
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    def _emit(self, event: str, data: Any) -> None:
        if event in self._event_handlers:
            for handler in self._event_handlers[event]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        asyncio.create_task(handler(data))  # noqa: RUF006
                    else:
                        handler(data)
                except Exception as e:
                    logger.error(f"Handler error for {event}: {e}")

    async def _dispatch_message(self, data: dict[str, Any]) -> None:
        action = data.get("action") or data.get("a")
        msg_type = data.get("T")

        if action == "subscribed":
            logger.debug(f"Subscription confirmed: {data}")
        elif action == "ping":
            await self._ws.send(self._encoder.encode({"action": "pong"}))  # type: ignore[union-attr]
        elif action == "pong":
            self._last_pong_time = time.time()
        elif action == "error":
            msg = data.get("message") or data.get("msg")
            logger.error(f"Server error: {msg}")
            self._emit("error", Exception(msg))
        elif msg_type == "t":
            self._emit("trade", Trade.from_dict(data))
        elif msg_type == "te":
            self._emit("trade_extra", WSTradeExtra.from_dict(data))
        elif msg_type == "e":
            self._emit("expected_price", WSExpectedPrice.from_dict(data))
        elif msg_type == "sd":
            self._emit("security_definition", SecurityDefinition.from_dict(data))
        elif msg_type == "q":
            self._emit("quote", Quote.from_dict(data))
        elif msg_type == "b":
            from dnse_morphe.types import Ohlc

            self._emit("ohlc", Ohlc.from_dict(data))
        elif msg_type == "o":
            self._emit("order", WSOrder.from_dict(data))
        elif msg_type == "p":
            self._emit("position", WSPosition.from_dict(data))
        elif msg_type == "a":
            self._emit("account", WSAccountUpdate.from_dict(data))

    async def _message_handler(self) -> None:
        reconnect_attempt = 0
        max_reconnect_delay = 60

        while self._is_running:
            try:
                async for message in self._ws:  # type: ignore[union-attr]
                    data = self._decoder.decode(message)
                    await self._dispatch_message(data)
                    reconnect_attempt = 0
            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(f"Connection closed: {e}")
                if self.auto_reconnect and e.code in (1006, 1011, 1012):
                    reconnect_attempt += 1
                    if reconnect_attempt > self.max_retries:
                        self._emit("max_reconnect_exceeded", reconnect_attempt)
                        break
                    delay = min(2 ** (reconnect_attempt - 1), max_reconnect_delay)
                    logger.info(
                        f"Reconnecting in {delay}s (attempt {reconnect_attempt}/{self.max_retries})..."
                    )
                    self._emit(
                        "reconnecting",
                        {
                            "attempt": reconnect_attempt,
                            "max_retries": self.max_retries,
                            "delay": delay,
                        },
                    )
                    await asyncio.sleep(delay)
                    try:
                        await self._handle_reconnection()
                        reconnect_attempt = 0
                    except Exception:
                        continue
                else:
                    self._emit("error", e)
                    break
            except Exception as e:
                logger.error(f"Message handler error: {e}")
                self._emit("error", e)
                break

    async def _handle_reconnection(self) -> None:
        previous_subscriptions = self._subscriptions.copy()
        self._is_authenticated = False
        await self.connect()
        for channel, sub_data in previous_subscriptions.items():
            await self._subscribe_channel(
                channel, sub_data["symbols"], **sub_data.get("kwargs", {})
            )
        self._last_pong_time = time.time()
        self._emit("reconnected", {"session_id": self._session_id})

    async def _heartbeat_loop(self) -> None:
        while self._is_running and self._ws is not None:
            try:
                await self._ws.send(self._encoder.encode({"action": "ping"}))  # type: ignore[attr-defined]
                logger.debug("Sent heartbeat ping")
                await asyncio.sleep(self.heartbeat_interval)
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                break

    async def subscribe_trades(
        self,
        symbols: list[str],
        on_trade: Callable[[Trade], None] | None = None,
    ) -> None:
        channel = f"tick.G1.{self.encoding}"
        await self._subscribe_channel(channel, symbols)
        if on_trade:
            self.on("trade", on_trade)

    async def subscribe_quotes(
        self,
        symbols: list[str],
        on_quote: Callable[[Quote], None] | None = None,
    ) -> None:
        channel = f"top_price.G1.{self.encoding}"
        await self._subscribe_channel(channel, symbols)
        if on_quote:
            self.on("quote", on_quote)

    async def subscribe_ohlc(
        self,
        symbols: list[str],
        resolution: str = "1m",
        on_ohlc: Callable | None = None,
    ) -> None:
        channel = f"ohlc.{resolution}.{self.encoding}"
        await self._subscribe_channel(channel, symbols)
        if on_ohlc:
            self.on("ohlc", on_ohlc)

    async def subscribe_orders(
        self,
        on_order: Callable[[WSOrder], None] | None = None,
    ) -> None:
        await self._subscribe_channel("orders", [])
        if on_order:
            self.on("order", on_order)

    async def subscribe_positions(
        self,
        on_position: Callable[[WSPosition], None] | None = None,
    ) -> None:
        await self._subscribe_channel("positions", [])
        if on_position:
            self.on("position", on_position)

    async def subscribe_account(
        self,
        on_account: Callable[[WSAccountUpdate], None] | None = None,
    ) -> None:
        await self._subscribe_channel("account", [])
        if on_account:
            self.on("account", on_account)

    async def _subscribe_channel(self, channel: str, symbols: list[str], **kwargs: Any) -> None:
        if not self._is_authenticated:
            raise SubscriptionError("Must authenticate before subscribing")
        subscribe_msg = {
            "action": "subscribe",
            "channels": [{"name": channel, "symbols": symbols, **kwargs}],
        }
        await self._ws.send(self._encoder.encode(subscribe_msg))  # type: ignore[union-attr]
        self._subscriptions[channel] = {"symbols": symbols, "kwargs": kwargs}
        logger.info(f"Subscribed to {channel}: {symbols}")

    async def disconnect(self) -> None:
        logger.info("Disconnecting...")
        self._is_running = False
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        if self._message_handler_task and not self._message_handler_task.done():
            self._message_handler_task.cancel()
            try:
                await self._message_handler_task
            except asyncio.CancelledError:
                pass
        if self._ws:
            await self._ws.close()  # type: ignore[attr-defined]
        self._is_authenticated = False
        logger.info("Disconnected")

    async def __aenter__(self) -> WebSocket:
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.disconnect()

    @property
    def is_healthy(self) -> bool:
        if not self._ws or not self._is_authenticated:
            return False
        if self.heartbeat_interval > 0:
            time_since_pong = time.time() - self._last_pong_time
            max_pong_delay = self.heartbeat_interval * 2
            if time_since_pong > max_pong_delay:
                return False
        return True
