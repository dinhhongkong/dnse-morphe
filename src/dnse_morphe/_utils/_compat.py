from __future__ import annotations

import typing
from typing import Any, Union, get_args, get_origin

from typing_extensions import TypeIs

__all__ = ["get_args", "get_origin", "is_literal_type", "is_typeddict", "is_union"]


def is_union(typ: type[Any] | None) -> TypeIs[Any]:
    return get_origin(typ) is Union


def is_typeddict(tp: type[Any] | None) -> bool:
    if tp is None:
        return False
    return hasattr(tp, "__required_keys__") and hasattr(tp, "__optional_keys__")


def is_literal_type(tp: type[Any] | None) -> TypeIs[Any]:
    return get_origin(tp) is typing.Literal
