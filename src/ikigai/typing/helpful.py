# SPDX-FileCopyrightText: 2025-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

import abc
from collections.abc import Generator


class Helpful(abc.ABC):
    """
    Abstract base class for Classes that provide help methods.
    """

    @abc.abstractmethod
    def _help(self) -> Generator[str]: ...

    def help(self) -> str:
        """
        Get formatted string of the help documentation.

        Returns
        -------
        str
            Formatted help documentation.
        """
        return "\n".join(list(self._help()))
