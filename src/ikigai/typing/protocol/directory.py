# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from enum import Enum
from typing import Protocol, TypedDict


class DirectoryType(str, Enum):
    APP = "PROJECT"
    DATASET = "DATASET"
    FLOW = "PIPELINE"
    MODEL = "MODEL"


class DirectoryDict(TypedDict):
    directory_id: str
    type: DirectoryType


class NamedDirectoryDict(DirectoryDict, TypedDict):
    name: str


class Directory(Protocol):
    @property
    def directory_id(self) -> str: ...

    @property
    def type(self) -> DirectoryType: ...

    def to_dict(self) -> DirectoryDict: ...
