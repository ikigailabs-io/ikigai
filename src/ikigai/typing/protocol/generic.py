# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Protocol, TypedDict


class Named(Protocol):
    @property
    def name(self) -> str: ...


class Empty(Protocol):
    pass


class EmptyDict(TypedDict):
    pass
