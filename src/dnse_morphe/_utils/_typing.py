from __future__ import annotations

import typing
from collections import abc as _c_abc
from collections.abc import Iterable
from typing import Annotated, Any, Required, TypeVar, cast, get_args, get_origin

import typing_extensions
from typing_extensions import (
    TypeIs,
)

from ._utils import lru_cache


def is_annotated_type(typ: type) -> bool:
    return get_origin(typ) == Annotated


def is_list_type(typ: type) -> bool:
    return (get_origin(typ) or typ) is list


def is_sequence_type(typ: type) -> bool:
    origin = get_origin(typ) or typ
    return (
        origin == typing_extensions.Sequence
        or origin == typing.Sequence
        or origin == _c_abc.Sequence
    )


def is_iterable_type(typ: type) -> bool:
    """If the given type is `typing.Iterable[T]`"""
    origin = get_origin(typ) or typ
    return origin == Iterable or origin == _c_abc.Iterable


def is_required_type(typ: type) -> bool:
    return get_origin(typ) == Required


def is_typevar(typ: type) -> bool:
    # type ignore is required because type checkers
    # think this expression will always return False
    return type(typ) is TypeVar  # type: ignore


_TYPE_ALIAS_TYPES: tuple[type, ...] = (
    typing.TypeAliasType,
    typing_extensions.TypeAliasType,
)


def is_type_alias_type(tp: Any, /) -> TypeIs[typing_extensions.TypeAliasType]:
    """Return whether the provided argument is an instance of `TypeAliasType`.

    ```python
    type Int = int
    is_type_alias_type(Int)
    # > True
    Str = TypeAliasType("Str", str)
    is_type_alias_type(Str)
    # > True
    ```
    """
    return isinstance(tp, _TYPE_ALIAS_TYPES)


# Extracts T from Annotated[T, ...] or from Required[Annotated[T, ...]]
@lru_cache(maxsize=8096)
def strip_annotated_type(typ: type) -> type:
    if is_required_type(typ) or is_annotated_type(typ):
        return strip_annotated_type(cast("type", get_args(typ)[0]))

    return typ


def extract_type_arg(typ: type, index: int) -> type:
    args = get_args(typ)
    try:
        return cast("type", args[index])
    except IndexError as err:
        raise RuntimeError(
            f"Expected type {typ} to have a type argument at index {index} but it did not"
        ) from err
