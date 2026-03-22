from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

from dnse_morphe.types import Account, Balance, Deal, LoanPackage

if TYPE_CHECKING:
    from dnse_morphe._base_client import BaseDNSEClient

logger = logging.getLogger("dnse-morphe")


class Accounts:
    def __init__(self, client: BaseDNSEClient) -> None:
        self._client = client

    def list(
        self,
        *,
        dry_run: bool = False,
    ) -> list[Account]:
        _, body = self._client._request("GET", "/accounts", dry_run=dry_run)
        if dry_run:
            return []
        data = json.loads(body)  # type: ignore[arg-type]
        return [Account.from_dict(a) for a in data]

    def list_balances(
        self,
        account_no: str,
        *,
        dry_run: bool = False,
    ) -> list[Balance]:  # type: ignore[valid-type]
        _, body = self._client._request("GET", f"/accounts/{account_no}/balances", dry_run=dry_run)
        if dry_run:
            return []
        data = json.loads(body)  # type: ignore[arg-type]
        return [Balance.from_dict(b) for b in data]

    def list_deals(
        self,
        account_no: str,
        market_type: str,
        *,
        dry_run: bool = False,
    ) -> list[Deal]:  # type: ignore[valid-type]
        _, body = self._client._request(
            "GET",
            f"/accounts/{account_no}/deals",
            query={"marketType": market_type},
            dry_run=dry_run,
        )
        if dry_run:
            return []
        data = json.loads(body)  # type: ignore[arg-type]
        return [Deal.from_dict(d) for d in data]

    def list_loan_packages(
        self,
        account_no: str,
        market_type: str,
        symbol: str | None = None,
        *,
        dry_run: bool = False,
    ) -> list[LoanPackage]:  # type: ignore[valid-type]
        query: dict[str, Any] = {"marketType": market_type}
        if symbol:
            query["symbol"] = symbol
        _, body = self._client._request(
            "GET",
            f"/accounts/{account_no}/loan-packages",
            query=query,
            dry_run=dry_run,
        )
        if dry_run:
            return []
        data = json.loads(body)  # type: ignore[arg-type]
        return [LoanPackage.from_dict(lp) for lp in data]

    def get_ppse(
        self,
        account_no: str,
        market_type: str,
        symbol: str,
        price: float,
        loan_package_id: int,
        *,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        _, body = self._client._request(
            "GET",
            f"/accounts/{account_no}/ppse",
            query={
                "marketType": market_type,
                "symbol": symbol,
                "price": str(price),
                "loanPackageId": str(loan_package_id),
            },
            dry_run=dry_run,
        )
        if dry_run:
            return {}
        return json.loads(body)  # type: ignore[arg-type, no-any-return]
