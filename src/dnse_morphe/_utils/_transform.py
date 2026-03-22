from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, TypeVar

from ._utils import is_mapping, is_sequence

__all__ = [
    "PropertyInfo",
    "async_maybe_transform",
    "async_transform",
    "maybe_transform",
    "transform",
]

T = TypeVar("T")
T2 = TypeVar("T2")


@dataclass
class PropertyInfo:
    """Metadata about a property/field for transformation."""

    name: str
    default: Any = None


def transform(value: Any, expected_type: type[T], transform_fn: Callable[[Any], T2]) -> T2 | T:
    """Transform a value if it matches the expected type, otherwise return as-is."""
    if isinstance(value, expected_type):
        return transform_fn(value)
    return value  # type: ignore[no-any-return]


async def async_transform(
    value: Any, expected_type: type[T], transform_fn: Callable[[Any], T2 | Awaitable[T2]]
) -> T2 | T:
    """Async version of transform."""
    if isinstance(value, expected_type):
        result = transform_fn(value)
        if isinstance(result, Awaitable):
            return await result
        return result
    return value  # type: ignore[no-any-return]


def maybe_transform(value: dict[str, Any]) -> dict[str, Any]:
    """Transform nested structures in a dict for serialization."""
    if not is_mapping(value):
        return value
    result: dict[str, Any] = {}
    for k, v in value.items():
        if is_mapping(v):
            result[k] = maybe_transform(dict(v))
        elif is_sequence(v) and not isinstance(v, (str, bytes)):
            result[k] = [maybe_transform(dict(i)) if is_mapping(i) else i for i in v]
        else:
            result[k] = v
    return result


async def async_maybe_transform(value: dict[str, Any]) -> dict[str, Any]:
    """Async version of maybe_transform."""
    return maybe_transform(value)
