# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Protocol, TypedDict

from ikigai.utils.enums import DirectoryType


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
