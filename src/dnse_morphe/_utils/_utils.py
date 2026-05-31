from __future__ import annotations

from typing import TypeGuard


def is_dict(obj: object) -> TypeGuard[dict[object, object]]:
    return isinstance(obj, dict)
