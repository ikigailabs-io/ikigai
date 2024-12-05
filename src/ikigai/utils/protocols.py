# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from typing import Protocol


class Named(Protocol):
    name: str


class Directory(Protocol):
    directory_id: str
    type: str
