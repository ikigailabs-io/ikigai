# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Protocol, TypedDict

from ikigai.typing.protocol.directory import DirectoryDict


class ModelType(Protocol):
    @property
    def model_type(self) -> str: ...

    @property
    def sub_model_type(self) -> str: ...


class ModelDict(TypedDict):
    project_id: str
    model_id: str
    name: str
    latest_version_id: str
    directory: DirectoryDict
    model_type: str
    sub_model_type: str
    description: str
    created_at: str
    modified_at: str
