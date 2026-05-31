from __future__ import annotations

import logging

from dnse_morphe._base_client import BaseDNSEClient
from dnse_morphe._constants import WS_BASE_URL_PROD
from dnse_morphe.resources import WebSocket

logger = logging.getLogger("dnse-morphe")


class AsyncDNSEClient(BaseDNSEClient):
    ws: WebSocket | None = None

    def websocket(
        self,
        base_url: str = WS_BASE_URL_PROD,
        encoding: str = "json",
        auto_reconnect: bool = True,
        max_retries: int = 10,
        heartbeat_interval: float = 25.0,
        timeout: float = 60.0,
    ) -> WebSocket:
        self.ws = WebSocket(
            client=self,
            base_url=base_url,
            encoding=encoding,
            auto_reconnect=auto_reconnect,
            max_retries=max_retries,
            heartbeat_interval=heartbeat_interval,
            timeout=timeout,
        )
        return self.ws
