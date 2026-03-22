from __future__ import annotations

from pydantic import BaseModel

__all__ = ["Order", "OrderHistoryItem", "OrderRequest", "OrderResponse"]


class OrderRequest(BaseModel):
    account_no: str = ""
    symbol: str = ""
    side: str = ""
    order_type: str = ""
    price: float | None = None
    quantity: int = 0
    loan_package_id: int | None = None

    def to_dict(self) -> dict:
        data: dict = {
            "accountNo": self.account_no,
            "symbol": self.symbol,
            "side": self.side,
            "orderType": self.order_type,
            "quantity": self.quantity,
        }
        if self.price is not None:
            data["price"] = str(self.price)
        if self.loan_package_id is not None:
            data["loanPackageId"] = self.loan_package_id
        return data


class Order(BaseModel):
    order_id: str = ""
    account_no: str = ""
    symbol: str = ""
    side: str = ""
    order_type: str = ""
    status: str = ""
    quantity: int = 0
    filled_quantity: int = 0
    price: float | None = None
    average_fill_price: float | None = None
    created_at: str | None = None
    updated_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> Order:
        def dec(key: str) -> float | None:
            val = data.get(key)
            if val is None:
                return None
            return float(val)

        raw = {
            "order_id": str(data.get("orderId") or data.get("order_id") or ""),
            "account_no": str(data.get("accountNo") or data.get("account_no") or ""),
            "symbol": str(data.get("symbol") or ""),
            "side": str(data.get("side") or ""),
            "order_type": str(data.get("orderType") or data.get("order_type") or ""),
            "status": str(data.get("status") or ""),
            "quantity": int(data.get("quantity") or 0),
            "filled_quantity": int(data.get("filledQuantity") or data.get("filled_quantity") or 0),
            "price": dec("price"),
            "average_fill_price": dec("averageFillPrice"),
            "created_at": data.get("createdAt") or data.get("created_at"),
            "updated_at": data.get("updatedAt") or data.get("updated_at"),
        }
        return cls.model_validate(raw)


class OrderResponse(BaseModel):
    order_id: str = ""
    status: str = ""
    message: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> OrderResponse:
        raw = {
            "order_id": str(data.get("orderId") or data.get("order_id") or ""),
            "status": str(data.get("status") or ""),
            "message": data.get("message"),
        }
        return cls.model_validate(raw)


class OrderHistoryItem(Order):
    market_type: str = ""
    order_category: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> OrderHistoryItem:
        order = Order.from_dict(data)
        raw = {
            "order_id": order.order_id,
            "account_no": order.account_no,
            "symbol": order.symbol,
            "side": order.side,
            "order_type": order.order_type,
            "status": order.status,
            "quantity": order.quantity,
            "filled_quantity": order.filled_quantity,
            "price": order.price,
            "average_fill_price": order.average_fill_price,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "market_type": str(data.get("marketType") or data.get("market_type") or ""),
            "order_category": data.get("orderCategory") or data.get("order_category"),
        }
        return cls.model_validate(raw)
