from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TypeVar

T = TypeVar("T")


def consume_sync_iterator(iterator: Iterator[T]) -> list[T]:
    return list(iterator)


async def consume_async_iterator(iterator: AsyncIterator[T]) -> list[T]:
    return [item async for item in iterator]
