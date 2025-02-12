# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import InitVar
from typing import Any

from pydantic import Field
from pydantic.dataclasses import dataclass

from ikigai.client.session import Session

_UNSET: Any = object()


@dataclass
class ComponentAPI:
    # Init only vars
    session: InitVar[Session]

    __session: Session = Field(init=False)

    def __post_init__(self, session: Session) -> None:
        self.__session = session

    def get_projects_for_user(self, directory_id: str = _UNSET) -> list[dict]:
        fetch_all = directory_id == _UNSET
        if directory_id == _UNSET:
            directory_id = ""
        return self.__session.get(
            path="/component/get-projects-for-user",
            params={"fetch_all": fetch_all, "directory_id": directory_id},
        ).json()["projects"]
