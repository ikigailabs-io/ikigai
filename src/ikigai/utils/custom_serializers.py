# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import AwareDatetime, PlainSerializer


def __datetime_to_timestamp(value: datetime) -> str:
    return str(int(value.timestamp()))


def __optional_datetime_to_timestamp(value: datetime | None) -> str:
    if not value:
        return ""
    return str(int(value.timestamp()))


TimestampSerializableDatetime = Annotated[
    AwareDatetime, PlainSerializer(__datetime_to_timestamp)
]
TimestampSerializableOptionalDatetime = Annotated[
    AwareDatetime | None, PlainSerializer(__optional_datetime_to_timestamp)
]
