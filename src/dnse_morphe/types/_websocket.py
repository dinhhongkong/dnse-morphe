from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

__all__ = [
    "WSAccountUpdate",
    "WSExpectedPrice",
    "WSForeignInvestor",
    "WSMarketIndex",
    "WSOrder",
    "WSPosition",
    "WSTradeExtra",
]


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


class WSForeignInvestor(BaseModel):
    market_id: str = ""
    board_id: str = ""
    trading_session_id: str = ""
    symbol: str = ""
    transact_time: str = ""
    foreign_investor_type_code: str = ""

    sell_volume: int = 0
    sell_traded_amount: int = 0
    buy_volume: int = 0
    buy_traded_amount: int = 0

    total_sell_volume: int = 0
    total_sell_traded_amount: int = 0
    total_buy_volume: int = 0
    total_buy_traded_amount: int = 0

    foreigner_order_limit_quantity: int = 0
    foreigner_buy_possible_quantity: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> WSForeignInvestor:
        raw = {
            "market_id": str(data.get("marketId") or data.get("mi") or ""),
            "board_id": str(data.get("boardId") or data.get("bi") or ""),
            "trading_session_id": str(data.get("tradingSessionId") or data.get("tsid") or ""),
            "symbol": str(data.get("symbol") or data.get("s") or ""),
            "transact_time": str(data.get("transactTime") or data.get("tt") or ""),
            "foreign_investor_type_code": str(
                data.get("foreignInvestorTypeCode") or data.get("fitc") or ""
            ),
            "sell_volume": int(data.get("sellVolume") or data.get("sv") or 0),
            "sell_traded_amount": int(data.get("sellTradedAmount") or data.get("sta") or 0),
            "buy_volume": int(data.get("buyVolume") or data.get("bv") or 0),
            "buy_traded_amount": int(data.get("buyTradedAmount") or data.get("bta") or 0),
            "total_sell_volume": int(data.get("totalSellVolume") or data.get("tsv") or 0),
            "total_sell_traded_amount": int(
                data.get("totalSellTradedAmount") or data.get("tsta") or 0
            ),
            "total_buy_volume": int(data.get("totalBuyVolume") or data.get("tbv") or 0),
            "total_buy_traded_amount": int(
                data.get("totalBuyTradedAmount") or data.get("tbta") or 0
            ),
            "foreigner_order_limit_quantity": int(
                data.get("foreignerOrderLimitQuantity") or data.get("folq") or 0
            ),
            "foreigner_buy_possible_quantity": int(
                data.get("foreignerBuyPossibleQuantity") or data.get("fbpq") or 0
            ),
        }
        return cls.model_validate(raw)


class WSMarketIndex(BaseModel):
    index_name: str = ""
    changed_ratio: float = 0.0
    changed_value: float = 0.0

    fluctuation_steadiness_issue_count: int = 0
    fluctuation_down_issue_count: int = 0
    fluctuation_up_issue_count: int = 0
    fluctuation_lower_limit_issue_count: int = 0
    fluctuation_upper_limit_issue_count: int = 0

    fluctuation_down_issue_volume: int = 0
    fluctuation_up_issue_volume: int = 0
    fluctuation_steadiness_issue_volume: int = 0

    currency_code: str = ""
    index_type_code: str = ""

    lowest_value_indexes: float = 0.0
    highest_value_indexes: float = 0.0
    prior_value_indexes: float = 0.0
    value_indexes: float = 0.0

    contauct_acc_trd_val: float = 0.0
    contauct_acc_trd_vol: int = 0
    blk_trd_acc_trd_val: float = 0.0
    blk_trd_acc_trd_vol: int = 0

    gross_trade_amount: float = 0.0
    total_volume_traded: int = 0
    market_index_class: int = 0
    market_id: int = 0
    trading_session_id: int = 0
    transact_time: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> WSMarketIndex:
        def fl(key: str) -> float:
            val = data.get(key)
            return float(val) if val is not None else 0.0

        def integer(key: str) -> int:
            val = data.get(key)
            return int(val) if val is not None else 0

        raw = {
            "index_name": str(data.get("indexName") or data.get("in") or ""),
            "changed_ratio": fl("changedRatio"),
            "changed_value": fl("changedValue"),
            "fluctuation_steadiness_issue_count": integer("fluctuationSteadinessIssueCount"),
            "fluctuation_down_issue_count": integer("fluctuationDownIssueCount"),
            "fluctuation_up_issue_count": integer("fluctuationUpIssueCount"),
            "fluctuation_lower_limit_issue_count": integer("fluctuationLowerLimitIssueCount"),
            "fluctuation_upper_limit_issue_count": integer("fluctuationUpperLimitIssueCount"),
            "fluctuation_down_issue_volume": integer("fluctuationDownIssueVolume"),
            "fluctuation_up_issue_volume": integer("fluctuationUpIssueVolume"),
            "fluctuation_steadiness_issue_volume": integer("fluctuationSteadinessIssueVolume"),
            "currency_code": str(data.get("currencyCode") or data.get("cc") or ""),
            "index_type_code": str(data.get("indexTypeCode") or data.get("itc") or ""),
            "lowest_value_indexes": fl("lowestValueIndexes"),
            "highest_value_indexes": fl("highestValueIndexes"),
            "prior_value_indexes": fl("priorValueIndexes"),
            "value_indexes": fl("valueIndexes"),
            "contauct_acc_trd_val": fl("contauctAccTrdVal"),
            "contauct_acc_trd_vol": integer("contauctAccTrdVol"),
            "blk_trd_acc_trd_val": fl("blkTrdAccTrdVal"),
            "blk_trd_acc_trd_vol": integer("blkTrdAccTrdVol"),
            "gross_trade_amount": fl("grossTradeAmount"),
            "total_volume_traded": integer("totalVolumeTraded"),
            "market_index_class": integer("marketIndexClass"),
            "market_id": integer("marketId"),
            "trading_session_id": integer("tradingSessionId"),
            "transact_time": str(data.get("transactTime") or data.get("tt") or ""),
        }
        return cls.model_validate(raw)
