from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel

__all__ = ["Account", "Balance", "Deal", "LoanPackage"]


class Account(BaseModel):
    account_no: str = ""
    account_name: str = ""
    account_type: str = ""
    status: str = ""
    open_date: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> Account:
        raw = {
            "account_no": str(data.get("accountNo") or data.get("account_no") or ""),
            "account_name": str(data.get("accountName") or data.get("account_name") or ""),
            "account_type": str(data.get("accountType") or data.get("account_type") or ""),
            "status": str(data.get("status") or ""),
            "open_date": data.get("openDate") or data.get("open_date"),
        }
        return cls.model_validate(raw)


class Balance(BaseModel):
    account_no: str = ""
    cash_balance: Decimal = Decimal("0")
    buying_power: Decimal = Decimal("0")
    total_assets: Decimal = Decimal("0")
    liability: Decimal = Decimal("0")
    market_value: Decimal = Decimal("0")
    available_cash: Decimal = Decimal("0")
    withheld: Decimal = Decimal("0")
    currency: str = "VND"

    @classmethod
    def from_dict(cls, data: dict) -> Balance:
        def dec(key: str) -> Decimal:
            val = data.get(key, 0)
            return Decimal(str(val)) if val is not None else Decimal("0")

        raw = {
            "account_no": str(data.get("accountNo") or data.get("account_no") or ""),
            "cash_balance": dec("cashBalance"),
            "buying_power": dec("buyingPower"),
            "total_assets": dec("totalAssets"),
            "liability": dec("liability"),
            "market_value": dec("marketValue"),
            "available_cash": dec("availableCash"),
            "withheld": dec("withheld"),
            "currency": data.get("currency", "VND"),
        }
        return cls.model_validate(raw)


class Deal(BaseModel):
    deal_id: str = ""
    account_no: str = ""
    symbol: str = ""
    side: str = ""
    quantity: int = 0
    price: Decimal = Decimal("0")
    deal_status: str = ""
    matched_quantity: int = 0
    matched_price: Decimal = Decimal("0")
    matched_at: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> Deal:
        def dec(key: str) -> Decimal:
            val = data.get(key, 0)
            return Decimal(str(val)) if val is not None else Decimal("0")

        raw = {
            "deal_id": str(data.get("dealId") or data.get("deal_id") or ""),
            "account_no": str(data.get("accountNo") or data.get("account_no") or ""),
            "symbol": str(data.get("symbol") or ""),
            "side": str(data.get("side") or ""),
            "quantity": int(data.get("quantity") or 0),
            "price": dec("price"),
            "deal_status": str(data.get("dealStatus") or data.get("deal_status") or ""),
            "matched_quantity": int(
                data.get("matchedQuantity") or data.get("matched_quantity") or 0
            ),
            "matched_price": dec("matchedPrice"),
            "matched_at": data.get("matchedAt") or data.get("matched_at"),
        }
        return cls.model_validate(raw)


class LoanPackage(BaseModel):
    loan_package_id: int = 0
    account_no: str = ""
    symbol: str = ""
    market_type: str = ""
    loan_quantity: int = 0
    loan_price: Decimal = Decimal("0")
    interest_rate: Decimal = Decimal("0")
    loan_date: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> LoanPackage:
        def dec(key: str) -> Decimal:
            val = data.get(key, 0)
            return Decimal(str(val)) if val is not None else Decimal("0")

        raw = {
            "loan_package_id": int(data.get("loanPackageId") or data.get("loan_package_id") or 0),
            "account_no": str(data.get("accountNo") or data.get("account_no") or ""),
            "symbol": str(data.get("symbol") or ""),
            "market_type": str(data.get("marketType") or data.get("market_type") or ""),
            "loan_quantity": int(data.get("loanQuantity") or data.get("loan_quantity") or 0),
            "loan_price": dec("loanPrice"),
            "interest_rate": dec("interestRate"),
            "loan_date": str(data.get("loanDate") or data.get("loan_date") or ""),
        }
        return cls.model_validate(raw)
