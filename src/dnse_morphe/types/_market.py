from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, field_validator

__all__ = ["Ohlc", "PriceLevel", "Quote", "SecurityDefinition", "Trade"]


class PriceLevel(BaseModel):
    price: float
    quantity: int

    @field_validator("price", mode="before")
    @classmethod
    def price_from_dict(cls, v: Any) -> float:
        if isinstance(v, dict):
            return float(v.get("p") or v.get("Price") or 0.0)
        return float(v) if v is not None else 0.0

    @field_validator("quantity", mode="before")
    @classmethod
    def quantity_from_dict(cls, v: Any) -> int:
        if isinstance(v, dict):
            return int(v.get("q") or v.get("Qtty") or 0)
        return int(v) if v is not None else 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PriceLevel:
        return cls.model_validate(data)


class Trade(BaseModel):
    market_id: int = Field(validation_alias="market_id", default=0)
    board_id: int = 0
    isin: str = ""
    symbol: str = ""
    price: float = 0.0
    quantity: int = 0
    total_volume_traded: int = 0
    gross_trade_amount: float = 0.0
    highest_price: float = 0.0
    lowest_price: float = 0.0
    open_price: float = 0.0
    trading_session_id: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Trade:
        raw = {
            "market_id": int(data.get("market_id") or data.get("mi") or 0),
            "board_id": int(data.get("board_id") or data.get("bi") or 0),
            "isin": str(data.get("isin") or data.get("is") or ""),
            "symbol": str(data.get("symbol") or data.get("s") or ""),
            "price": float(data.get("price") or data.get("p") or 0.0),
            "quantity": int(data.get("quantity") or data.get("q") or 0),
            "total_volume_traded": int(data.get("total_volume_traded") or data.get("tvt") or 0),
            "gross_trade_amount": float(data.get("gross_trade_amount") or data.get("gta") or 0.0),
            "highest_price": float(data.get("highest_price") or data.get("hp") or 0.0),
            "lowest_price": float(data.get("lowest_price") or data.get("lp") or 0.0),
            "open_price": float(data.get("open_price") or data.get("op") or 0.0),
            "trading_session_id": int(data.get("trading_session_id") or data.get("tsi") or 0),
        }
        return cls.model_validate(raw)


class Quote(BaseModel):
    market_id: int = 0
    board_id: int = 0
    symbol: str = ""
    isin: str = ""
    bid: list[PriceLevel] = []
    offer: list[PriceLevel] = []
    total_offer_qtty: float | None = None
    total_bid_qtty: float | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Quote:
        bids_data = data.get("bid") or data.get("b") or []
        offers_data = data.get("offer") or data.get("of") or []

        raw = {
            "market_id": int(data.get("market_id") or data.get("mi") or 0),
            "board_id": int(data.get("board_id") or data.get("bi") or 0),
            "symbol": str(data.get("symbol") or data.get("s") or ""),
            "isin": str(data.get("isin") or data.get("is") or ""),
            "bid": [PriceLevel.from_dict(lvl) for lvl in bids_data],
            "offer": [PriceLevel.from_dict(lvl) for lvl in offers_data],
            "total_offer_qtty": data.get("total_offer_qtty") or data.get("toq"),
            "total_bid_qtty": data.get("total_bid_qtty") or data.get("tbq"),
        }
        return cls.model_validate(raw)

    @property
    def best_bid(self) -> tuple[float, int] | None:
        if not self.bid:
            return None
        return (self.bid[0].price, self.bid[0].quantity)

    @property
    def best_ask(self) -> tuple[float, int] | None:
        if not self.offer:
            return None
        return (self.offer[0].price, self.offer[0].quantity)


class Ohlc(BaseModel):
    symbol: str = ""
    resolution: int = 0
    open: Decimal = Decimal("0")
    high: Decimal = Decimal("0")
    low: Decimal = Decimal("0")
    close: Decimal = Decimal("0")
    volume: int = 0
    time: int = 0
    last_updated: int = 0
    type: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Ohlc:
        def dec(key: str) -> Decimal:
            val = data.get(key)
            if val is None:
                return Decimal("0")
            return Decimal(str(val))

        raw = {
            "symbol": str(data.get("symbol") or data.get("s") or ""),
            "resolution": int(data.get("resolution") or data.get("r") or 0),
            "open": dec("open"),
            "high": dec("high"),
            "low": dec("low"),
            "close": dec("close"),
            "volume": int(data.get("volume") or data.get("v") or 0),
            "time": int(data.get("time") or data.get("t") or 0),
            "last_updated": int(data.get("lastUpdated") or data.get("lu") or 0),
            "type": str(data.get("type") or data.get("ty") or ""),
        }
        return cls.model_validate(raw)


class SecurityDefinition(BaseModel):
    market_id: int = 0
    board_id: int = 0
    symbol: str = ""
    isin: str = ""
    product_grp_id: int = 0
    security_group_id: int = 0
    basic_price: float = 0.0
    ceiling_price: float = 0.0
    floor_price: float = 0.0
    open_interest_quantity: int = 0
    security_status: int = 0
    symbol_admin_status_code: int = 0
    symbol_trading_method_status_code: int = 0
    symbol_trading_sanction_status_code: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SecurityDefinition:
        def fl(key: str) -> float:
            val = data.get(key)
            return float(val) if val is not None else 0.0

        def integer(key: str) -> int:
            val = data.get(key)
            return int(val) if val is not None else 0

        raw = {
            "symbol": str(data.get("symbol") or data.get("s") or ""),
            "market_id": integer("market_id"),
            "board_id": integer("board_id"),
            "isin": str(data.get("isin") or data.get("is") or ""),
            "product_grp_id": integer("product_grp_id"),
            "security_group_id": integer("security_group_id"),
            "basic_price": fl("basic_price"),
            "ceiling_price": fl("ceiling_price"),
            "floor_price": fl("floor_price"),
            "open_interest_quantity": integer("open_interest_quantity"),
            "security_status": integer("security_status"),
            "symbol_admin_status_code": integer("symbol_admin_status_code"),
            "symbol_trading_method_status_code": integer("symbol_trading_method_status_code"),
            "symbol_trading_sanction_status_code": integer("symbol_trading_sanction_status_code"),
        }
        return cls.model_validate(raw)
