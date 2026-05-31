from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

from dnse_morphe.types import Ohlc, Quote, SecurityDefinition, Trade

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

    def get_trades(
        self,
        symbol: str,
        board_id: str | None = None,
        from_date: int | None = None,
        to_date: int | None = None,
        limit: int | None = None,
        order: str | None = None,
        next_page_token: str | None = None,
        *,
        dry_run: bool = False,
    ) -> list[Trade]:
        query: dict[str, Any] = {}
        if board_id is not None:
            query["boardId"] = board_id
        if from_date is not None:
            query["from"] = from_date
        if to_date is not None:
            query["to"] = to_date
        if limit is not None:
            query["limit"] = limit
        if order is not None:
            query["order"] = order
        if next_page_token is not None:
            query["nextPageToken"] = next_page_token
        _, body = self._client._request(
            "GET",
            f"/price/{symbol}/trades",
            query=query if query else None,
            dry_run=dry_run,
        )
        if dry_run:
            return []
        data = json.loads(body)  # type: ignore[arg-type]
        return [Trade.from_dict(t) for t in data]

    def get_latest_trade(
        self,
        symbol: str,
        board_id: str | None = None,
        *,
        dry_run: bool = False,
    ) -> Trade:
        query: dict[str, Any] = {}
        if board_id is not None:
            query["boardId"] = board_id
        _, body = self._client._request(
            "GET",
            f"/price/{symbol}/trades/latest",
            query=query if query else None,
            dry_run=dry_run,
        )
        if dry_run:
            return Trade.model_construct()
        return Trade.from_dict(json.loads(body))  # type: ignore[arg-type]

    def get_quotes(
        self,
        symbol: str,
        board_id: str | None = None,
        from_date: int | None = None,
        to_date: int | None = None,
        limit: int | None = None,
        order: str | None = None,
        next_page_token: str | None = None,
        *,
        dry_run: bool = False,
    ) -> list[Quote]:
        query: dict[str, Any] = {}
        if board_id is not None:
            query["boardId"] = board_id
        if from_date is not None:
            query["from"] = from_date
        if to_date is not None:
            query["to"] = to_date
        if limit is not None:
            query["limit"] = limit
        if order is not None:
            query["order"] = order
        if next_page_token is not None:
            query["nextPageToken"] = next_page_token
        _, body = self._client._request(
            "GET",
            f"/price/{symbol}/quotes",
            query=query if query else None,
            dry_run=dry_run,
        )
        if dry_run:
            return []
        data = json.loads(body)  # type: ignore[arg-type]
        return [Quote.from_dict(q) for q in data]

    def get_latest_quote(
        self,
        symbol: str,
        board_id: str | None = None,
        *,
        dry_run: bool = False,
    ) -> Quote:
        query: dict[str, Any] = {}
        if board_id is not None:
            query["boardId"] = board_id
        _, body = self._client._request(
            "GET",
            f"/price/{symbol}/quotes/latest",
            query=query if query else None,
            dry_run=dry_run,
        )
        if dry_run:
            return Quote.model_construct()
        return Quote.from_dict(json.loads(body))  # type: ignore[arg-type]

    def get_instruments(
        self,
        symbol: str | None = None,
        market_id: str | None = None,
        security_group_id: str | None = None,
        index_name: str | None = None,
        limit: int | None = None,
        page: int | None = None,
        *,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        query: dict[str, Any] = {}
        if symbol is not None:
            query["symbol"] = symbol
        if market_id is not None:
            query["marketId"] = market_id
        if security_group_id is not None:
            query["securityGroupId"] = security_group_id
        if index_name is not None:
            query["indexName"] = index_name
        if limit is not None:
            query["limit"] = limit
        if page is not None:
            query["page"] = page
        _, body = self._client._request(
            "GET",
            "/instruments",
            query=query if query else None,
            dry_run=dry_run,
        )
        if dry_run:
            return {}
        return json.loads(body)  # type: ignore[arg-type, no-any-return]

    def get_close_price(
        self,
        symbol: str,
        board_id: str | None = None,
        *,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        query: dict[str, Any] = {}
        if board_id is not None:
            query["boardId"] = board_id
        _, body = self._client._request(
            "GET",
            f"/price/{symbol}/close",
            query=query if query else None,
            dry_run=dry_run,
        )
        if dry_run:
            return {}
        return json.loads(body)  # type: ignore[arg-type, no-any-return]

    def get_working_dates(
        self,
        *,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        _, body = self._client._request(
            "GET",
            "/market/working-dates",
            dry_run=dry_run,
        )
        if dry_run:
            return {}
        return json.loads(body)  # type: ignore[arg-type, no-any-return]
