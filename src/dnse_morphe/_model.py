from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound="BaseModel")


class DNSEBaseModel(BaseModel):
    """Base model for all API request/response types."""

    model_config = {"populate_by_name": True, "extra": "allow"}

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        return cls.model_validate(data)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json", by_alias=True)
