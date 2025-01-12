# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Annotated, Any, Optional

from pydantic import BeforeValidator


def __optional_int(value: Any) -> int | None:
    if isinstance(value, str) and value == "":
        return None
    return int(value)


OptionalInt = Annotated[Optional[int], BeforeValidator(__optional_int)]
