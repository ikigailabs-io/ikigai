# SPDX-FileCopyrightText: 2025-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

import abc
from collections.abc import Generator


class Helpful(abc.ABC):
    """Base class for Classes that provide help methods"""

    @abc.abstractmethod
    def _help(self) -> Generator[str]: ...

    def help(self) -> str:
        """Returns a formatted string of the help documentation."""
        return "\n".join(list(self._help()))
