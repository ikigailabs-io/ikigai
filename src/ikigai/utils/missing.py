# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from enum import Enum


class MissingType(Enum):
    _Missing = "Missing"


MISSING = MissingType._Missing
