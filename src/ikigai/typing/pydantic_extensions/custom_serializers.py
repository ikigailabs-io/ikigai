# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from datetime import datetime


def datetime_to_timestamp(value: datetime) -> str:
    return str(int(value.timestamp()))


def optional_datetime_to_timestamp(value: datetime | None) -> str:
    if not value:
        return ""
    return str(int(value.timestamp()))
