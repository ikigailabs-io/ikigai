# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from pydantic import AliasChoices, BaseModel, Field, RootModel

from ikigai.client.client import Client
from ikigai.typing.protocol import Directory, DirectoryType, NamedDirectoryDict
from ikigai.utils.compatibility import Self
from ikigai.utils.named_mapping import NamedMapping

logger = logging.getLogger("ikigai.components")


class ModelType(RootModel):
    model_type: str
    sub_model_type: str


class ModelBuilder:
    _app_id: str
    _name: str
    _directory: Directory | None
    _model_type: ModelType | None
    _description: str
    __client: Client

    def __init__(self, client: Client, app_id: str) -> None:
        self.__client = client
        self._app_id = app_id
        self._name = ""
        self._directory = None
        self._model_type = None


class Model(BaseModel):
    app_id: str = Field(validation_alias=AliasChoices("app_id", "project_id"))
    model_id: str
    name: str
    model_type: ModelType
    description: str
    created_at: str
    modified_at: str
    __client: Client

    @classmethod
    def from_dict(cls, data: Mapping[str, Any], client: Client) -> Model:
        logger.debug("Creating a %s from %s", cls.__name__, data)
        self = cls.model_validate(data)
        self.__client = client
        return self


class ModelDirectoryBuilder:
    _app_id: str
    _name: str
    _parent: Directory | None
    __client: Client

    def __init__(self, client: Client, app_id: str) -> None:
        self.__client = client
        self._app_id = app_id
        self._name = ""
        self._parent = None

    def new(self, name: str) -> ModelDirectoryBuilder:
        self._name = name
        return self

    def parent(self, parent: Directory) -> ModelDirectoryBuilder:
        self._parent = parent
        return self

    def build(self) -> ModelDirectory:
        directory_id = self.__client.component.create_model_directory(
            app_id=self._app_id, name=self._name, parent=self._parent
        )
        directory_dict = self.__client.component.get_model_directory(
            app_id=self._app_id, directory_id=directory_id
        )
        directory = ModelDirectory.from_dict(data=directory_dict, client=self.__client)
        return directory


class ModelDirectory(BaseModel):
    app_id: str = Field(validation_alias=AliasChoices("app_id", "project_id"))
    directory_id: str
    name: str
    __client: Client

    @property
    def type(self) -> DirectoryType:
        return DirectoryType.MODEL

    @classmethod
    def from_dict(cls, data: Mapping[str, Any], client: Client) -> Self:
        logger.debug("Creating a %s from %s", cls.__name__, data)
        self = cls.model_validate(data)
        self.__client = client
        return self

    def to_dict(self) -> NamedDirectoryDict:
        return {"directory_id": self.directory_id, "type": self.type, "name": self.name}

    def directories(self) -> NamedMapping[Self]:
        directory_dicts = self.__client.component.get_model_directories_for_app(
            app_id=self.app_id, parent=self
        )
        directories = {
            directory.directory_id: directory
            for directory in (
                self.from_dict(data=directory_dict, client=self.__client)
                for directory_dict in directory_dicts
            )
        }

        return NamedMapping(directories)

    def models(self) -> NamedMapping[Model]:
        model_dicts = self.__client.component.get_models_for_app(
            app_id=self.app_id, directory_id=self.directory_id
        )

        models = {
            model.model_id: model
            for model in (
                Model.from_dict(data=model_dict, client=self.__client)
                for model_dict in model_dicts
            )
        }

        return NamedMapping(models)
