# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TypedDict

from ikigai.typing.protocol.directory import DirectoryDict


class AppDict(TypedDict):
    project_id: str
    name: str
    owner: str
    description: str
    icon: str
    images: list[str]
    directory: DirectoryDict
    created_at: str
    modified_at: str
    last_used_at: str
