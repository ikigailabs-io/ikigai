# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import PlainSerializer


def __datetime_to_str(value: datetime) -> str:
    return str(int(value.timestamp()))


def __optional_datetime_to_str(value: datetime | None) -> str:
    if not value:
        return ""
    return str(int(value.timestamp()))


StrSerializableDatetime = Annotated[datetime, PlainSerializer(__datetime_to_str)]
StrSerializableOptionalDatetime = Annotated[
    datetime | None, PlainSerializer(__optional_datetime_to_str)
]
