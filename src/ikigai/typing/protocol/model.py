# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TypedDict

from ikigai.typing.protocol.directory import DirectoryDict


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
