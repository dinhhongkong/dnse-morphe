from __future__ import annotations

BASE_URL = "https://openapi.dnse.com.vn"
WS_BASE_URL_PROD = "wss://ws-openapi.dnse.com.vn"
WS_BASE_URL_UAT = "wss://ws-openapi-uat.dnse.com.vn"

DEFAULT_TIMEOUT = 60.0
DEFAULT_WS_TIMEOUT = 60.0
DEFAULT_HEARTBEAT_INTERVAL = 25.0
DEFAULT_WS_MAX_RETRIES = 10

CONTENT_TYPE_JSON = "application/json"

SENSITIVE_HEADERS = {"api-key", "x-api-key", "authorization", "trading-token", "x-signature"}

__all__ = [
    "BASE_URL",
    "CONTENT_TYPE_JSON",
    "DEFAULT_HEARTBEAT_INTERVAL",
    "DEFAULT_TIMEOUT",
    "DEFAULT_WS_MAX_RETRIES",
    "DEFAULT_WS_TIMEOUT",
    "SENSITIVE_HEADERS",
    "WS_BASE_URL_PROD",
    "WS_BASE_URL_UAT",
]
