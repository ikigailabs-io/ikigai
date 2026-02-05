# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import abc
from typing import Generic, TypeVar

from ikigai.typing.named_mapping import Named, NamedMapping

T = TypeVar("T", bound=Named)


class ComponentBrowser(Generic[T], abc.ABC):
    @abc.abstractmethod
    def __call__(self) -> NamedMapping[T]:
        """
        Get as many components as possible

        Note
        ----
            Usage of this method is discouraged as the platform may truncate
            the list of components returned if it exceeds a certain limit.

        Returns
        -------
        NamedMapping[T]
            A mapping of component names to components
        """

    @abc.abstractmethod
    def __getitem__(self, name: str) -> T:
        """
        Get a component by name

        Parameters
        ----------
        name : str
            Name of the component to get

        Returns
        -------
        T
            The component with the given name

        Raises
        ------
        KeyError
            If the component with the given name does not exist
        """

    @abc.abstractmethod
    def search(self, query: str) -> NamedMapping[T]:
        """
        Search for a component by name

        Parameters
        ----------
        query : str
            Query string to search for

        Returns
        -------
        NamedMapping[T]
            A mapping of component names to components that match the query
        """
