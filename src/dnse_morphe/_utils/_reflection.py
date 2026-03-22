from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any, TypeVar

from typing_extensions import ParamSpec

from ._utils import lru_cache

__all__ = ["assert_signatures_in_sync", "function_has_argument"]

P = ParamSpec("P")
T = TypeVar("T")


@lru_cache(maxsize=256)
def function_has_argument(func: Callable[..., Any], name: str) -> bool:
    try:
        sig = inspect.signature(func)
        return name in sig.parameters
    except (ValueError, TypeError):
        return False


def assert_signatures_in_sync(
    async_func: Callable[P, Any], sync_func: Callable[P, Any], *, check_first_arg: bool = True
) -> None:
    """Assert that async and sync versions of a function have matching signatures."""
    try:
        async_sig = inspect.signature(async_func)
        sync_sig = inspect.signature(sync_func)
    except (ValueError, TypeError):
        return

    async_params = list(async_sig.parameters.values())
    sync_params = list(sync_sig.parameters.values())

    if check_first_arg:
        if async_params and sync_params and async_params[0].name == sync_params[0].name:
            async_params = async_params[1:]
            sync_params = sync_params[1:]

    for a_param, s_param in zip(async_params, sync_params):
        if a_param.name != s_param.name:
            raise TypeError(
                f"Parameter name mismatch: async has '{a_param.name}', sync has '{s_param.name}'"
            )
        if a_param.kind != s_param.kind:
            raise TypeError(
                f"Parameter kind mismatch for '{a_param.name}': "
                f"async is {a_param.kind}, sync is {s_param.kind}"
            )
