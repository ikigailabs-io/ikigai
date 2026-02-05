# SPDX-FileCopyrightText: 2026-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Annotated

from pydantic import AwareDatetime, BeforeValidator, PlainSerializer, StringConstraints

from ikigai.typing.pydantic_extensions.custom_serializers import (
    datetime_to_timestamp,
    optional_datetime_to_timestamp,
)
from ikigai.typing.pydantic_extensions.custom_validators import (
    cron_str,
    optional_str,
)

TimestampSerializableDatetime = Annotated[
    AwareDatetime, PlainSerializer(datetime_to_timestamp)
]
TimestampSerializableOptionalDatetime = Annotated[
    AwareDatetime | None, PlainSerializer(optional_datetime_to_timestamp)
]

OptionalStr = Annotated[str | None, BeforeValidator(optional_str)]

LowercaseStr = Annotated[str, StringConstraints(to_lower=True)]

CronStr = Annotated[str, BeforeValidator(cron_str)]
