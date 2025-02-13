# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from collections import abc
from collections.abc import Mapping
from typing import Generic, TypeVar

from ikigai.typing.protocol import Named

VT = TypeVar("VT", bound=Named)


class NamedMapping(Generic[VT], Mapping[str, VT]):
    def __init__(self, mapping: Mapping[str, VT]) -> None:
        self._mapping = dict(mapping)

    def __getitem__(self, key: str) -> VT:
        matches = [item for item in self._mapping.values() if item.name == key]
        if not matches:
            raise KeyError(key)
        if len(matches) > 1:
            error_msg = (
                f'Multiple({len(matches)}) items with name: "{key}", '
                f'use get_id(id="...") to disambiguiate between {matches}'
            )
            raise KeyError(error_msg)
        return matches[0]

    def __iter__(self) -> abc.Iterator[str]:
        return iter({item.name for item in self._mapping.values()})

    def __len__(self) -> int:
        return len(self._mapping)

    def __repr__(self) -> str:
        return repr(self._mapping)

    def get_id(self, id: str) -> VT:
        return self._mapping[id]
