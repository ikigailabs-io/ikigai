# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field

from ikigai import components
from ikigai.client import Client
from ikigai.utils.compatibility import Self
from ikigai.utils.named_mapping import NamedMapping
from ikigai.utils.protocols import Directory, DirectoryType


class AppBuilder:
    _name: str
    _description: str
    _directory: dict[str, str]
    _icon: str
    _images: list[str]
    __client: Client

    def __init__(self, client: Client) -> None:
        self.__client = client
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
        resp = self.__client.post(
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
        resp = self.__client.get(
            path="/component/get-project", params={"project_id": app_id}
        ).json()
        app = App.from_dict(data=resp["project"], client=self.__client)
        return app


class App(BaseModel):
    app_id: str = Field(validation_alias="project_id")
    name: str
    owner: EmailStr
    description: str
    created_at: datetime
    modified_at: datetime
    last_used_at: datetime
    __client: Client

    @classmethod
    def from_dict(cls, data: dict, client: Client) -> Self:
        self = cls.model_validate(data)
        self.__client = client
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
        self.__client.post(
            path="/component/delete-project",
            json={"project": {"project_id": self.app_id}},
        )
        return None

    def rename(self, name: str) -> Self:
        _ = self.__client.post(
            path="/component/edit-project",
            json={"project": {"project_id": self.app_id, "name": name}},
        )
        # TODO: handle error case, currently it is a raise NotImplemented from Session
        self.name = name
        return self

    def move(self, directory: Directory) -> Self:
        _ = self.__client.post(
            path="/component/edit-project",
            json={
                "project": {
                    "project_id": self.app_id,
                    "directory": {
                        "directory_id": directory.directory_id,
                        "type": directory.type,
                    },
                }
            },
        )
        return self

    def update_description(self, description: str) -> Self:
        _ = self.__client.post(
            path="/component/edit-project",
            json={"project": {"project_id": self.app_id, "description": description}},
        ).json()
        # TODO: handle error case, currently it is a raise NotImplemented from Session
        self.description = description
        return self

    def describe(self) -> dict:
        response: dict[str, Any] = self.__client.get(
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
        resp = self.__client.get(
            path="/component/get-datasets-for-project",
            params={"project_id": self.app_id},
        ).json()
        datasets = {
            dataset.dataset_id: dataset
            for dataset in (
                components.Dataset.from_dict(data=dataset_dict, client=self.__client)
                for dataset_dict in resp["datasets"]
            )
        }

        return NamedMapping(datasets)

    @property
    def dataset(self) -> components.DatasetBuilder:
        return components.DatasetBuilder(client=self.__client, app_id=self.app_id)

    def dataset_directories(self) -> NamedMapping[components.DatasetDirectory]:
        resp = self.__client.get(
            path="/component/get-dataset-directories-for-project",
            params={"project_id": self.app_id},
        ).json()
        directories = {
            directory.directory_id: directory
            for directory in (
                components.DatasetDirectory.from_dict(
                    data=directory_dict, client=self.__client
                )
                for directory_dict in resp["directories"]
            )
        }

        return NamedMapping(directories)

    @property
    def dataset_directory(self) -> components.DatasetDirectoryBuilder:
        return components.DatasetDirectoryBuilder(
            client=self.__client, app_id=self.app_id
        )

    def flows(self) -> NamedMapping[components.Flow]:
        resp = self.__client.get(
            path="/component/get-pipelines-for-project",
            params={"project_id": self.app_id},
        ).json()

        flows = {
            flow.flow_id: flow
            for flow in (
                components.Flow.from_dict(data=flow_dict, client=self.__client)
                for flow_dict in resp["pipelines"]
            )
        }

        return NamedMapping(flows)

    @property
    def flow(self) -> components.FlowBuilder:
        return components.FlowBuilder(client=self.__client, app_id=self.app_id)

    def flow_directories(self) -> NamedMapping[components.FlowDirectory]:
        resp = self.__client.get(
            path="/component/get-pipeline-directories-for-project",
            params={"project_id": self.app_id},
        ).json()
        directories = {
            directory.directory_id: directory
            for directory in (
                components.FlowDirectory.from_dict(
                    data=directory_dict, client=self.__client
                )
                for directory_dict in resp["directories"]
            )
        }

        return NamedMapping(directories)

    @property
    def flow_directory(self) -> components.FlowDirectoryBuilder:
        return components.FlowDirectoryBuilder(
            client=self.__client, app_id=self.app_id
        )


class AppDirectory(BaseModel):
    directory_id: str
    name: str
    created_at: datetime
    modified_at: datetime
    __client: Client

    @property
    def type(self) -> str:
        return DirectoryType.APP.value

    @classmethod
    def from_dict(cls, data: dict, client: Client) -> Self:
        self = cls.model_validate(data)
        self.__client = client
        return self

    def directories(self) -> NamedMapping[Self]:
        resp = self.__client.get(
            path="/component/get-project-directories-for-user",
            params={"directory_id": self.directory_id},
        ).json()
        directories = {
            directory.directory_id: directory
            for directory in (
                self.from_dict(data=directory_dict, client=self.__client)
                for directory_dict in resp["directories"]
            )
        }

        return NamedMapping(directories)

    def apps(self) -> NamedMapping[App]:
        resp = self.__client.get(
            path="/component/get-projects-for-user",
            params={"directory_id": self.directory_id, "fetch_all": False},
        ).json()

        apps = {
            app.app_id: app
            for app in (
                App.from_dict(data=app_dict, client=self.__client)
                for app_dict in resp["projects"]
            )
        }

        return NamedMapping(apps)
