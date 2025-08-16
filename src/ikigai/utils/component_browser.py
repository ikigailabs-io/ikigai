# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Generic, Protocol, TypeVar

from ikigai.typing.protocol.generic import Named
from ikigai.utils.named_mapping import NamedMapping

T = TypeVar("T", bound=Named)


class ComponentBrowser(Generic[T], Protocol):
    def __call__(self) -> NamedMapping[T]:
        """
        Get as many components as possible
        """
        ...

    def __getitem__(self, name: str) -> T:
        """
        Get a component by name
        """
        ...

    def search(self, query: str) -> NamedMapping[T]:
        """
        Search for a component by name
        """
        ...
