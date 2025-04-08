# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TypedDict

from ikigai.typing.protocol.directory import DirectoryDict


class DatasetDict(TypedDict):
    project_id: str
    dataset_id: str
    name: str
    filename: str
    data_types: dict[str, DataTypeDict]
    directory: DirectoryDict
    is_optimized: bool
    file_extension: str
    size: int
    is_visible: bool
    created_at: str
    modified_at: str


class DataTypeDict(TypedDict):
    data_type: str
    data_formats: str


class DatasetLogDict(TypedDict):
    status: str
    timestamp: str
    job_type: str
