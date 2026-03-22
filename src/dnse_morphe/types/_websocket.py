from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

__all__ = ["WSAccountUpdate", "WSExpectedPrice", "WSOrder", "WSPosition", "WSTradeExtra"]


class WSOrder(BaseModel):
    order_id: str = ""
    symbol: str = ""
    side: str = ""
    order_type: str = ""
    status: str = ""
    quantity: int = 0
    filled_quantity: int = 0
    price: float = 0.0
    average_fill_price: float = 0.0
    timestamp: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict) -> WSOrder:
        def dec(key: str) -> float:
            val = data.get(key)
            if val is None:
                return 0.0
            return float(val)

        ts = data.get("t") or data.get("timestamp")
        if ts:
            ts = datetime.fromtimestamp(int(ts) / 1000)
        else:
            ts = datetime.now()

        raw = {
            "order_id": str(data.get("oid") or data.get("order_id") or ""),
            "symbol": str(data.get("S") or data.get("symbol") or ""),
            "side": str(data.get("sd") or data.get("side") or ""),
            "order_type": str(data.get("ot") or data.get("order_type") or ""),
            "status": str(data.get("st") or data.get("status") or ""),
            "quantity": int(data.get("q") or data.get("quantity") or 0),
            "filled_quantity": int(data.get("fq") or data.get("filled_quantity") or 0),
            "price": dec("p"),
            "average_fill_price": dec("ap"),
            "timestamp": ts,
        }
        return cls.model_validate(raw)


class WSPosition(BaseModel):
    symbol: str = ""
    quantity: int = 0
    average_price: float = 0.0
    market_value: float = 0.0
    cost_basis: float = 0.0
    unrealized_pl: float = 0.0
    unrealized_pl_percent: float = 0.0
    timestamp: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict) -> WSPosition:
        def dec(key: str) -> float:
            val = data.get(key)
            if val is None:
                return 0.0
            return float(val)

        ts = data.get("t") or data.get("timestamp")
        if ts:
            ts = datetime.fromtimestamp(int(ts) / 1000)
        else:
            ts = datetime.now()

        raw = {
            "symbol": str(data.get("S") or data.get("symbol") or ""),
            "quantity": int(data.get("q") or data.get("quantity") or 0),
            "average_price": dec("ap"),
            "market_value": dec("mv"),
            "cost_basis": dec("cb"),
            "unrealized_pl": dec("upl"),
            "unrealized_pl_percent": dec("uplp"),
            "timestamp": ts,
        }
        return cls.model_validate(raw)


class WSAccountUpdate(BaseModel):
    cash: float = 0.0
    buying_power: float = 0.0
    portfolio_value: float = 0.0
    equity: float = 0.0
    timestamp: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict) -> WSAccountUpdate:
        def dec(key: str) -> float:
            val = data.get(key)
            if val is None:
                return 0.0
            return float(val)

        ts = data.get("t") or data.get("timestamp")
        if ts:
            ts = datetime.fromtimestamp(int(ts) / 1000)
        else:
            ts = datetime.now()

        raw = {
            "cash": dec("c"),
            "buying_power": dec("bp"),
            "portfolio_value": dec("pv"),
            "equity": dec("eq"),
            "timestamp": ts,
        }
        return cls.model_validate(raw)


class WSTradeExtra(BaseModel):
    market_id: int = 0
    board_id: int = 0
    isin: str = ""
    symbol: str = ""
    price: float = 0.0
    quantity: int = 0
    side: int = 0
    avg_price: float = 0.0
    total_volume_traded: int = 0
    gross_trade_amount: float = 0.0
    highest_price: float = 0.0
    lowest_price: float = 0.0
    open_price: float = 0.0
    trading_session_id: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> WSTradeExtra:
        raw = {
            "market_id": int(data.get("market_id") or data.get("mi") or 0),
            "board_id": int(data.get("board_id") or data.get("bi") or 0),
            "isin": str(data.get("isin") or data.get("is") or ""),
            "symbol": str(data.get("symbol") or data.get("s") or ""),
            "price": float(data.get("price") or data.get("p") or 0.0),
            "quantity": int(data.get("quantity") or data.get("q") or 0),
            "side": int(data.get("side") or data.get("si") or 0),
            "avg_price": float(data.get("avg_price") or data.get("ap") or 0.0),
            "total_volume_traded": int(data.get("total_volume_traded") or data.get("tvt") or 0),
            "gross_trade_amount": float(data.get("gross_trade_amount") or data.get("gta") or 0.0),
            "highest_price": float(data.get("highest_price") or data.get("hp") or 0.0),
            "lowest_price": float(data.get("lowest_price") or data.get("lp") or 0.0),
            "open_price": float(data.get("open_price") or data.get("op") or 0.0),
            "trading_session_id": int(data.get("trading_session_id") or data.get("tsi") or 0),
        }
        return cls.model_validate(raw)


class WSExpectedPrice(BaseModel):
    market_id: int = 0
    board_id: int = 0
    isin: str = ""
    symbol: str = ""
    close_price: float = 0.0
    expected_trade_price: float = 0.0
    expected_trade_quantity: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> WSExpectedPrice:
        raw = {
            "market_id": int(data.get("market_id") or data.get("mi") or 0),
            "board_id": int(data.get("board_id") or data.get("bi") or 0),
            "isin": str(data.get("isin") or data.get("is") or ""),
            "symbol": str(data.get("symbol") or data.get("s") or ""),
            "close_price": float(data.get("close_price") or data.get("cp") or 0.0),
            "expected_trade_price": float(
                data.get("expected_trade_price") or data.get("etp") or 0.0
            ),
            "expected_trade_quantity": int(
                data.get("expected_trade_quantity") or data.get("etq") or 0
            ),
        }
        return cls.model_validate(raw)
