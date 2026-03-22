from __future__ import annotations

from collections.abc import Iterator
from typing import Generic, TypeVar

T = TypeVar("T")


class Response(Generic[T]):
    """HTTP response wrapper."""

    def __init__(
        self,
        *,
        status_code: int,
        content: bytes,
        headers: dict[str, str],
        data: T | None = None,
    ):
        self.status_code = status_code
        self.content = content
        self.headers = headers
        self._data = data

    def json(self) -> T:
        import json

        if self._data is None:
            self._data = json.loads(self.content.decode("utf-8"))
        return self._data

    def __repr__(self) -> str:
        return f"<Response status_code={self.status_code}>"


class StreamResponse(Generic[T]):
    """Streaming response wrapper."""

    def __init__(
        self,
        *,
        status_code: int,
        headers: dict[str, str],
        iterator: Iterator[T],
    ):
        self.status_code = status_code
        self.headers = headers
        self._iterator = iterator

    def __iter__(self) -> Iterator[T]:
        return self._iterator

    def __repr__(self) -> str:
        return f"<StreamResponse status_code={self.status_code}>"
