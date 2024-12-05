# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from typing import Generic, Mapping, TypeVar
from collections import abc

from ikigai.utils.protocols import Named


VT = TypeVar("VT", bound=Named)


class NamedMapping(Generic[VT], Mapping[str, VT]):
    def __init__(self, mapping: Mapping[str, VT]) -> None:
        self._mapping = dict(mapping)

    def __getitem__(self, key: str) -> VT:
        matches = [item for item in self._mapping.values() if item.name == key]
        if not matches:
            raise KeyError(f"{key}")
        if len(matches) > 1:
            raise KeyError(
                f'Multiple({len(matches)}) items with name: "{key}", use get_id(id="...") to disambiguiate between {matches}'
            )
        return matches[0]

    def __iter__(self) -> abc.Iterator[str]:
        return iter(set(item.name for item in self._mapping.values()))

    def __len__(self) -> int:
        return len(self._mapping)

    def get_id(self, id: str) -> VT:
        return self._mapping[id]
