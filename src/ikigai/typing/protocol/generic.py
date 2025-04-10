# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Protocol


class Named(Protocol):
    @property
    def name(self) -> str: ...


class Empty(Protocol):
    pass
