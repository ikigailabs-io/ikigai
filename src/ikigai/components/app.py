# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field

from ikigai import components
from ikigai.client.session import Session
from ikigai.utils.compatibility import Self
from ikigai.utils.named_mapping import NamedMapping
from ikigai.utils.protocols import Directory


class AppBuilder:
    _name: str
    _description: str
    _directory: dict[str, str]
    _icon: str
    _images: list[str]
    __session: Session

    def __init__(self, session: Session) -> None:
        self.__session = session
        self._name = ""
        self._description = ""
        self._directory = {}
        self._icon = ""
        self._images = []

    def new(self, name: str) -> Self:
        self._name = name
        return self

    def description(self, description: str) -> Self:
        self._description = description
        return self

    def directory(self, directory: Directory) -> Self:
        self._directory = {
            "directory_id": directory.directory_id,
            "type": directory.type,
        }
        return self

    def build(self) -> App:
        resp = self.__session.post(
            path="/component/create-project",
            json={
                "project": {
                    "name": self._name,
                    "description": self._description,
                    "directory": self._directory,
                },
            },
        ).json()
        app_id = resp["project_id"]
        resp = self.__session.get(
            path="/component/get-project", params={"project_id": app_id}
        ).json()
        app = App.from_dict(data=resp["project"], session=self.__session)
        return app


class App(BaseModel):
    app_id: str = Field(validation_alias="project_id")
    name: str
    owner: EmailStr
    description: str
    created_at: datetime
    modified_at: datetime
    last_used_at: datetime
    __session: Session

    @classmethod
    def from_dict(cls, data: dict, session: Session) -> Self:
        self = cls.model_validate(data)
        self.__session = session
        return self

    """
    Operations on App
    """

    def to_dict(self) -> dict:
        return {
            "app_id": self.app_id,
            "name": self.name,
            "owner": self.owner,
            "description": self.description,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "last_used_at": self.last_used_at,
        }

    def delete(self) -> None:
        self.__session.post(
            path="/component/delete-project",
            json={"project": {"project_id": self.app_id}},
        )
        return None

    def rename(self, name: str) -> Self:
        _ = self.__session.post(
            path="/component/edit-project",
            json={"project": {"project_id": self.app_id, "name": name}},
        )
        # TODO: handle error case, currently it is a raise NotImplemented from Session
        self.name = name
        return self

    def update_description(self, description: str) -> Self:
        _ = self.__session.post(
            path="/component/edit-project",
            json={"project": {"project_id": self.app_id, "description": description}},
        ).json()
        # TODO: handle error case, currently it is a raise NotImplemented from Session
        self.description = description
        return self

    def describe(self) -> dict:
        response: dict[str, Any] = self.__session.get(
            path="/component/get-components-for-project",
            params={"project_id": self.app_id},
        ).json()

        # Combine components information with app info
        return_value = {
            "app": self.to_dict(),
            "components": response["project_components"][self.app_id],
        }

        return return_value

    """
    Access Components in the App
    """

    def datasets(self) -> NamedMapping[components.Dataset]:
        resp = self.__session.get(
            path="/component/get-datasets-for-project",
            params={"project_id": self.app_id},
        ).json()
        datasets = {
            dataset.dataset_id: dataset
            for dataset in (
                components.Dataset.from_dict(data=dataset_dict, session=self.__session)
                for dataset_dict in resp["datasets"]
            )
        }

        return NamedMapping(datasets)

    @property
    def dataset(self) -> components.DatasetBuilder:
        return components.DatasetBuilder(session=self.__session, app_id=self.app_id)
