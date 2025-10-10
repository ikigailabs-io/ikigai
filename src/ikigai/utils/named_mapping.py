# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from collections import Counter, abc
from collections.abc import Mapping
from typing import Any, Generic, TypeVar

from ikigai.typing.protocol import Named

VT = TypeVar("VT", bound=Named)


class NamedMapping(Generic[VT], Mapping[str, VT]):
    def __init__(self, mapping: Mapping[str, VT]) -> None:
        self._names = Counter(item.name for item in mapping.values())
        self._mapping: Mapping[str, VT] = mapping

    def __getitem__(self, key: str) -> VT:
        count = self._names[key]
        if count == 0:
            raise KeyError(key)

        matches = [item for item in self._mapping.values() if item.name == key]
        if count > 1:
            error_msg = (
                f'Multiple({count}) items with name: "{key}", '
                f'use get_id(id="...") to disambiguiate between them'
            )
            raise KeyError(error_msg, matches)

        return matches[0]

    def __contains__(self, key: Any) -> bool:
        if name := getattr(key, "name", None):
            key = name
        return key in self._names

    def __iter__(self) -> abc.Iterator[str]:
        return iter(self._names)

    def __len__(self) -> int:
        return len(self._mapping)

    def __repr__(self) -> str:
        return repr(self._mapping)

    def get_id(self, id: str) -> VT:
        return self._mapping[id]
