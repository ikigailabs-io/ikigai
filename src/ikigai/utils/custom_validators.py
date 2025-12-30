# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Annotated, Any

from pydantic import BeforeValidator, StringConstraints

__ONE_HOUR_AS_MINUTES = 60
__CRON_PARTS = ["minute", "hour", "day", "month", "day_of_week"]


def __optional_str(value: Any) -> str | None:
    if not value:
        return None
    return str(value)


def __cron_str(value: Any) -> str:
    if not isinstance(value, str):
        error_msg = "Cron must be a string"
        raise TypeError(error_msg)

    cron_components = value.strip().split(" ")

    # Validate the number of components
    if len(cron_components) != len(__CRON_PARTS):
        error_msg = (
            "Incorrect cron format, expected format: minute hour day month day_of_week"
            f"but got {value}"
        )
        raise ValueError(error_msg)

    # On Ikigai, the minute field must be an integer between 0 and 59
    minute = cron_components[0]
    if not minute.isdigit():
        error_msg = "Minute field must be an integer"
        raise TypeError(error_msg)

    if not (0 <= int(minute) < __ONE_HOUR_AS_MINUTES):
        error_msg = "Minute field must be an integer between 0 and 59"
        raise ValueError(error_msg)

    return value.strip()


OptionalStr = Annotated[str | None, BeforeValidator(__optional_str)]

LowercaseStr = Annotated[str, StringConstraints(to_lower=True)]

CronStr = Annotated[str, BeforeValidator(__cron_str)]
