# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from enum import Enum
from typing import Protocol


class Named(Protocol):
    name: str


class DirectoryType(str, Enum):
    APP = "PROJECT"
    DATASET = "DATASET"
    FLOW = "PIPELINE"


class Directory(Protocol):
    directory_id: str
    type: str
