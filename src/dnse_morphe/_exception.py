from __future__ import annotations

__version__ = "0.1.0"


class DNSEError(Exception):
    """Base exception for all library errors."""


class APIError(DNSEError):
    """HTTP API error."""

    def __init__(self, status: int, body: str | None):
        self.status = status
        self.body = body
        super().__init__(f"HTTP {status}: {body}")


class AuthenticationError(DNSEError):
    """Authentication failed."""


class RateLimitError(DNSEError):
    """Rate limit exceeded."""


class WebSocketError(DNSEError):
    """WebSocket-related error."""


class ConnectionError(WebSocketError):
    """Failed to establish WebSocket connection."""


class ConnectionClosed(WebSocketError):
    """WebSocket connection was closed."""

    def __init__(self, message: str, recoverable: bool = False):
        self.recoverable = recoverable
        super().__init__(message)


class SubscriptionError(WebSocketError):
    """Subscription failed."""


class EncodingError(WebSocketError):
    """Message encoding/decoding failed."""


__all__ = [
    "APIError",
    "AuthenticationError",
    "ConnectionClosed",
    "ConnectionError",
    "DNSEError",
    "EncodingError",
    "RateLimitError",
    "SubscriptionError",
    "WebSocketError",
]
