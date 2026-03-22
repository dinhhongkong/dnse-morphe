from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

from dnse_morphe.types import Ohlc, SecurityDefinition

if TYPE_CHECKING:
    from dnse_morphe._base_client import BaseDNSEClient

logger = logging.getLogger("dnse-morphe")


class MarketData:
    def __init__(self, client: BaseDNSEClient) -> None:
        self._client = client

    def get_security_definition(
        self,
        symbol: str,
        board_id: str | None = None,
        *,
        dry_run: bool = False,
    ) -> SecurityDefinition:
        query: dict[str, Any] = {}
        if board_id:
            query["boardId"] = board_id
        _, body = self._client._request(
            "GET",
            f"/price/secdef/{symbol}",
            query=query if query else None,
            dry_run=dry_run,
        )
        if dry_run:
            return SecurityDefinition.model_construct()
        return SecurityDefinition.from_dict(json.loads(body))  # type: ignore[arg-type]

    def get_ohlc(
        self,
        bar_type: str,
        symbol: str | None = None,
        board_id: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        resolution: str | None = None,
        page_size: int | None = None,
        page_index: int | None = None,
        *,
        dry_run: bool = False,
    ) -> list[Ohlc]:
        query: dict[str, Any] = {"type": bar_type}
        if symbol:
            query["symbol"] = symbol
        if board_id:
            query["boardId"] = board_id
        if from_date:
            query["from"] = from_date
        if to_date:
            query["to"] = to_date
        if resolution:
            query["resolution"] = resolution
        if page_size is not None:
            query["pageSize"] = page_size
        if page_index is not None:
            query["pageIndex"] = page_index
        _, body = self._client._request(
            "GET",
            "/price/ohlc",
            query=query,
            dry_run=dry_run,
        )
        if dry_run:
            return []
        data = json.loads(body)  # type: ignore[arg-type]
        return [Ohlc.from_dict(o) for o in data]
