# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Annotated, Any

from pydantic import BeforeValidator, StringConstraints


def __optional_str(value: Any) -> str | None:
    if not value:
        return None
    return str(value)


OptionalStr = Annotated[str | None, BeforeValidator(__optional_str)]

LowercaseStr = Annotated[str, StringConstraints(to_lower=True)]
