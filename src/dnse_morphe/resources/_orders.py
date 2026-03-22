from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

from dnse_morphe._exception import APIError
from dnse_morphe.types import Order, OrderHistoryItem, OrderRequest, OrderResponse

if TYPE_CHECKING:
    from dnse_morphe._base_client import BaseDNSEClient

logger = logging.getLogger("dnse-morphe")


class Orders:
    def __init__(self, client: BaseDNSEClient) -> None:
        self._client = client

    def list(
        self,
        account_no: str,
        market_type: str,
        order_category: str | None = None,
        *,
        dry_run: bool = False,
    ) -> list[Order]:
        query: dict[str, Any] = {"marketType": market_type}
        if order_category:
            query["orderCategory"] = order_category
        _, body = self._client._request(
            "GET",
            f"/accounts/{account_no}/orders",
            query=query,
            dry_run=dry_run,
        )
        if dry_run:
            return []
        data = json.loads(body)  # type: ignore[arg-type]
        return [Order.from_dict(o) for o in data]

    def get(
        self,
        account_no: str,
        order_id: str,
        market_type: str,
        order_category: str | None = None,
        *,
        dry_run: bool = False,
    ) -> Order:
        query: dict[str, Any] = {"marketType": market_type}
        if order_category:
            query["orderCategory"] = order_category
        _, body = self._client._request(
            "GET",
            f"/accounts/{account_no}/orders/{order_id}",
            query=query,
            dry_run=dry_run,
        )
        if dry_run:
            return Order.model_construct(
                order_id="",
                account_no="",
                symbol="",
                side="",
                order_type="",
                status="",
                quantity=0,
                filled_quantity=0,
                price=None,
                average_fill_price=None,
            )
        return Order.from_dict(json.loads(body))  # type: ignore[arg-type]

    def list_history(
        self,
        account_no: str,
        market_type: str,
        from_date: str | None = None,
        to_date: str | None = None,
        page_size: int | None = None,
        page_index: int | None = None,
        *,
        dry_run: bool = False,
    ) -> list[OrderHistoryItem]:  # type: ignore[valid-type]
        query: dict[str, Any] = {"marketType": market_type}
        if from_date:
            query["from"] = from_date
        if to_date:
            query["to"] = to_date
        if page_size is not None:
            query["pageSize"] = page_size
        if page_index is not None:
            query["pageIndex"] = page_index
        _, body = self._client._request(
            "GET",
            f"/accounts/{account_no}/orders/history",
            query=query,
            dry_run=dry_run,
        )
        if dry_run:
            return []
        data = json.loads(body)  # type: ignore[arg-type]
        return [OrderHistoryItem.from_dict(o) for o in data]

    def create(
        self,
        market_type: str,
        order_request: OrderRequest,
        trading_token: str,
        order_category: str = "NORMAL",
        *,
        dry_run: bool = False,
    ) -> OrderResponse:
        headers = {"trading-token": trading_token}
        query = {"marketType": market_type, "orderCategory": order_category}
        status, body = self._client._request(
            "POST",
            "/accounts/orders",
            query=query,
            body=order_request.to_dict(),
            headers=headers,
            dry_run=dry_run,
        )
        if dry_run:
            return OrderResponse.model_construct(order_id="", status="")
        if status >= 400:
            raise APIError(status, body)
        return OrderResponse.from_dict(json.loads(body))  # type: ignore[arg-type]

    def modify(
        self,
        account_no: str,
        order_id: str,
        market_type: str,
        order_request: OrderRequest,
        trading_token: str,
        order_category: str | None = None,
        *,
        dry_run: bool = False,
    ) -> OrderResponse:
        headers = {"trading-token": trading_token}
        query: dict[str, Any] = {"marketType": market_type}
        if order_category:
            query["orderCategory"] = order_category
        status, body = self._client._request(
            "PUT",
            f"/accounts/{account_no}/orders/{order_id}",
            query=query,
            body=order_request.to_dict(),
            headers=headers,
            dry_run=dry_run,
        )
        if dry_run:
            return OrderResponse.model_construct(order_id="", status="")
        if status >= 400:
            raise APIError(status, body)
        return OrderResponse.from_dict(json.loads(body))  # type: ignore[arg-type]

    def cancel(
        self,
        account_no: str,
        order_id: str,
        market_type: str,
        trading_token: str,
        order_category: str | None = None,
        *,
        dry_run: bool = False,
    ) -> OrderResponse:
        headers = {"trading-token": trading_token}
        query: dict[str, Any] = {"marketType": market_type}
        if order_category:
            query["orderCategory"] = order_category
        status, body = self._client._request(
            "DELETE",
            f"/accounts/{account_no}/orders/{order_id}",
            query=query,
            headers=headers,
            dry_run=dry_run,
        )
        if dry_run:
            return OrderResponse.model_construct(order_id="", status="")
        if status >= 400:
            raise APIError(status, body)
        return OrderResponse.from_dict(json.loads(body))  # type: ignore[arg-type]

    def close_deal(
        self,
        deal_id: str,
        account_no: str,
        market_type: str,
        payload: dict[str, Any],
        trading_token: str,
        *,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        headers = {"trading-token": trading_token}
        query = {"marketType": market_type}
        status, body = self._client._request(
            "POST",
            f"/accounts/{account_no}/deals/{deal_id}/close",
            query=query,
            body=payload,
            headers=headers,
            dry_run=dry_run,
        )
        if status >= 400:
            raise APIError(status, body)
        return json.loads(body)  # type: ignore[arg-type, no-any-return]

    def create_trading_token(
        self,
        otp_type: str,
        passcode: str,
        *,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        status, body = self._client._request(
            "POST",
            "/registration/trading-token",
            body={"otpType": otp_type, "passcode": passcode},
            dry_run=dry_run,
        )
        if status >= 400:
            raise APIError(status, body)
        return json.loads(body)  # type: ignore[arg-type, no-any-return]

    def send_email_otp(
        self,
        *,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        status, body = self._client._request(
            "POST",
            "/registration/send-email-otp",
            dry_run=dry_run,
        )
        if status >= 400:
            raise APIError(status, body)
        return json.loads(body)  # type: ignore[arg-type, no-any-return]
