# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from functools import cached_property
from typing import Any

from pydantic import BaseModel, EmailStr, Field, PrivateAttr

from ikigai import components
from ikigai.client import Client
from ikigai.typing.protocol import (
    Directory,
    NamedDirectoryDict,
)
from ikigai.utils.compatibility import Self, deprecated
from ikigai.utils.component_browser import ComponentBrowser
from ikigai.utils.enums import AppAccessLevel, DirectoryType
from ikigai.utils.named_mapping import NamedMapping


class AppBrowser:
    __client: Client

    def __init__(self, client: Client) -> None:
        self.__client = client

    @deprecated("Prefer directly loading by name:\n\tikigai.apps['app_name']")
    def __call__(self) -> NamedMapping[App]:
        apps = {
            app["project_id"]: components.App.from_dict(data=app, client=self.__client)
            for app in self.__client.component.get_apps_for_user()
        }

        return NamedMapping(apps)

    def __getitem__(self, name: str) -> App:
        app_dict = self.__client.component.get_app_by_name(name)
        return components.App.from_dict(data=app_dict, client=self.__client)

    def search(self, query: str) -> NamedMapping[App]:
        matching_apps = {
            app["project_id"]: components.App.from_dict(data=app, client=self.__client)
            for app in self.__client.search.search_projects_for_user(query=query)
        }

        return NamedMapping(matching_apps)


class AppBuilder:
    _name: str
    _description: str
    _directory: Directory | None
    _icon: str
    _images: list[str]
    __client: Client

    def __init__(self, client: Client) -> None:
        self.__client = client
        self._name = ""
        self._description = ""
        self._directory = None
        self._icon = ""
        self._images = []

    def new(self, name: str) -> Self:
        self._name = name
        return self

    def description(self, description: str) -> Self:
        self._description = description
        return self

    def directory(self, directory: Directory) -> Self:
        self._directory = directory
        return self

    def build(self) -> App:
        app_id = self.__client.component.create_app(
            name=self._name,
            description=self._description,
            directory=self._directory,
        )
        app_dict = self.__client.component.get_app(app_id=app_id)
        return App.from_dict(data=app_dict, client=self.__client)


class AppAccess(BaseModel):
    """
    Access manager for the App.

    Grant/Update/Revoke access to the App.
    """

    __app_id: str = PrivateAttr()
    __client: Client = PrivateAttr()

    def __init__(self, *, app_id: str, client: Client) -> None:
        super().__init__()
        self.__app_id = app_id
        self.__client = client

    def grant(self, email: EmailStr, access_level: AppAccessLevel) -> Self:
        """
        Grant access to the App.

        Parameters
        ----------

        email: EmailStr
            Email address of the user to grant access to.

        access_level: AppAccessLevel
            Access level to grant to the user.

        Returns
        -------

        Self
            Access manager for the App.
        """
        self.__client.component.grant_app_access(
            app_id=self.__app_id,
            email=email,
            access_level=access_level,
        )
        return self

    def update(self, email: EmailStr, access_level: AppAccessLevel) -> Self:
        """
        Update access to the App.

        Parameters
        ----------

        email: EmailStr
            Email address of the user to update access for.

        access_level: AppAccessLevel
            New access level for the user.

        Returns
        -------

        Self
            Access manager for the App.
        """
        self.__client.component.update_app_access(
            app_id=self.__app_id,
            email=email,
            access_level=access_level,
        )
        return self

    def revoke(self, email: EmailStr) -> Self:
        """
        Revoke access to the App.

        Parameters
        ----------

        email: EmailStr
            Email address of the user to revoke access for.

        Returns
        -------

        Self
            Access manager for the App.
        """
        self.__client.component.revoke_app_access(
            app_id=self.__app_id,
            email=email,
        )
        return self


class App(BaseModel):
    """
    Represents an App in the Ikigai platform.

    Apps are the basic organizational units in Ikigai.

    Attributes
    ----------

    app_id: str
        Unique identifier of the app.

    name: str
        Name of the App.

    owner: EmailStr
        Email address of the app owner.

    description: str
        Description of the app.

    created_at: datetime
        Timestamp when the app was created.

    modified_at: datetime
        Timestamp when the app was last modified.

    last_used_at: datetime
        Timestamp when the app was last used.
    """

    app_id: str = Field(validation_alias="project_id")
    name: str
    owner: EmailStr
    description: str
    created_at: datetime
    modified_at: datetime
    last_used_at: datetime
    __client: Client = PrivateAttr()

    @classmethod
    def from_dict(cls, data: Mapping[str, Any], client: Client) -> Self:
        self = cls.model_validate(data)
        self.__client = client
        return self

    """
    Operations on App
    """

    def to_dict(self) -> dict:
        """
        Convert the App to a dictionary representation.

        Returns
        -------

        dict
            Dictionary containing the App attributes.
        """
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
        """
        Delete the App.

        Returns
        -------

        None
        """
        self.__client.component.delete_app(app_id=self.app_id)
        return None

    def rename(self, name: str) -> Self:
        """
        Rename the App.

        Parameters
        ----------

        name: str
            New name for the App.

        Returns
        -------

        Self
            Updated App.
        """
        _ = self.__client.component.edit_app(app_id=self.app_id, name=name)
        # TODO: handle error case, currently it is a raise NotImplemented from Session
        self.name = name
        return self

    def move(self, directory: Directory) -> Self:
        """
        Move the App to the target directory.

        Parameters
        ----------

        directory: Directory
            Target directory.

        Returns
        -------

        Self
            Updated App.
        """
        _ = self.__client.component.edit_app(app_id=self.app_id, directory=directory)
        return self

    def update_description(self, description: str) -> Self:
        """
        Update the App's description.

        Parameters
        ----------

        description: str
            The new description for the App.

        Returns
        -------

        Self
            The updated App with the new description.
        """
        _ = self.__client.component.edit_app(
            app_id=self.app_id, description=description
        )
        # TODO: handle error case, currently it is a raise NotImplemented from Session
        self.description = description
        return self

    @cached_property
    def access(self) -> AppAccess:
        """
        Manage access to the App.

        Returns
        -------

        AppAccess
            Access manager for the App.
        """
        return AppAccess(app_id=self.app_id, client=self.__client)

    def describe(self) -> dict[str, Any]:
        """
        Get details about the App including its components.

        Returns
        -------

        dict[str, Any]
            Dictionary containing App details and its associated
            components.
        """
        components = self.__client.component.get_components_for_app(app_id=self.app_id)

        # Combine components information with app info
        return {
            "app": self.to_dict(),
            "components": components,
        }

    """
    Access Components in the App
    """

    @property
    def datasets(self) -> ComponentBrowser[components.Dataset]:
        """
        Access the datasets associated with the App.

        Returns a `ComponentBrowser[Dataset]` to access this app's datasets.

        Returns
        -------

        DatasetBrowser
            Dataset browser for interacting with the App's datasets.

        Examples
        --------

        Use `search(query: str)`, which returns datasets matching a query
        string.

        >>> datasets = app.datasets
        >>> dataset = datasets.search("Examp")

        Retrieve a dataset by name.

        >>> datasets = app.datasets
        >>> dataset = datasets['Example Dataset']
        """
        return components.DatasetBrowser(app_id=self.app_id, client=self.__client)

    @property
    def dataset(self) -> components.DatasetBuilder:
        return components.DatasetBuilder(client=self.__client, app_id=self.app_id)

    def dataset_directories(self) -> NamedMapping[components.DatasetDirectory]:
        directory_dicts = self.__client.component.get_dataset_directories_for_app(
            app_id=self.app_id
        )
        directories = {
            directory.directory_id: directory
            for directory in (
                components.DatasetDirectory.from_dict(
                    data=directory_dict, client=self.__client
                )
                for directory_dict in directory_dicts
            )
        }

        return NamedMapping(directories)

    @property
    def dataset_directory(self) -> components.DatasetDirectoryBuilder:
        return components.DatasetDirectoryBuilder(
            client=self.__client, app_id=self.app_id
        )

    @property
    def flows(self) -> ComponentBrowser[components.Flow]:
        """
        Access the flows associated with the App.

        Returns a `ComponentBrowser[Flow]` to access this app's flows.

        Returns
        -------

        FlowBrowser
            Flow browser for interacting with the App's flows.

        Examples
        --------

        Use `search(query: str)` to retrieve flows matching a query.

        >>> flows = app.flows
        >>> flow = flows.search("Examp")

        Retrieve a flow by name.

        >>> flows = app.flows
        >>> flow = flows['Example Flow']
        """
        return components.FlowBrowser(app_id=self.app_id, client=self.__client)

    @property
    def flow(self) -> components.FlowBuilder:
        return components.FlowBuilder(client=self.__client, app_id=self.app_id)

    def flow_directories(self) -> NamedMapping[components.FlowDirectory]:
        directory_dicts = self.__client.component.get_flow_directories_for_app(
            app_id=self.app_id
        )
        directories = {
            directory.directory_id: directory
            for directory in (
                components.FlowDirectory.from_dict(
                    data=directory_dict, client=self.__client
                )
                for directory_dict in directory_dicts
            )
        }

        return NamedMapping(directories)

    @property
    def flow_directory(self) -> components.FlowDirectoryBuilder:
        return components.FlowDirectoryBuilder(client=self.__client, app_id=self.app_id)

    @property
    def models(self) -> ComponentBrowser[components.Model]:
        """
        Access the models associated with the App.

        Returns a `ComponentBrowser[Model]` to access this app's models.

        Returns
        -------

        ModelBrowser
            Model browser for interacting with the App's models.

        Examples
        --------

        Use `search(query: str)` to retrieve flows matching a query.

        >>> models = app.models
        >>> model = models.search("model")

        Retrieve a model by name.

        >>> models = app.models
        >>> model = models['model_name']
        """
        return components.ModelBrowser(app_id=self.app_id, client=self.__client)

    @property
    def model(self) -> components.ModelBuilder:
        return components.ModelBuilder(client=self.__client, app_id=self.app_id)

    def model_directories(self) -> NamedMapping[components.ModelDirectory]:
        directory_dicts = self.__client.component.get_model_directories_for_app(
            app_id=self.app_id
        )
        directories = {
            directory.directory_id: directory
            for directory in (
                components.ModelDirectory.from_dict(
                    data=directory_dict, client=self.__client
                )
                for directory_dict in directory_dicts
            )
        }

        return NamedMapping(directories)

    @property
    def model_directory(self) -> components.ModelDirectoryBuilder:
        return components.ModelDirectoryBuilder(
            client=self.__client, app_id=self.app_id
        )


class AppDirectoryBuilder:
    _name: str
    _parent: Directory | None
    __client: Client

    def __init__(self, client: Client) -> None:
        self.__client = client
        self._name = ""
        self._parent = None

    def new(self, name: str) -> Self:
        self._name = name
        return self

    def parent(self, parent: Directory) -> Self:
        self._parent = parent
        return self

    def build(self) -> AppDirectory:
        directory_id = self.__client.component.create_app_directory(
            name=self._name, parent=self._parent
        )
        directory_dict = self.__client.component.get_app_directory(
            directory_id=directory_id
        )
        return AppDirectory.from_dict(data=directory_dict, client=self.__client)


class AppDirectory(BaseModel):
    directory_id: str
    name: str
    __client: Client = PrivateAttr()

    @property
    def type(self) -> DirectoryType:
        return DirectoryType.APP

    @classmethod
    def from_dict(cls, data: Mapping[str, Any], client: Client) -> Self:
        self = cls.model_validate(data)
        self.__client = client
        return self

    def to_dict(self) -> NamedDirectoryDict:
        return {"directory_id": self.directory_id, "type": self.type, "name": self.name}

    def delete(self) -> None:
        self.__client.component.delete_app_directory(directory_id=self.directory_id)
        return None

    def directories(self) -> NamedMapping[Self]:
        directory_dicts = self.__client.component.get_app_directories_for_user(
            directory_id=self.directory_id,
        )
        directories = {
            directory.directory_id: directory
            for directory in (
                self.from_dict(data=directory_dict, client=self.__client)
                for directory_dict in directory_dicts
            )
        }

        return NamedMapping(directories)

    def apps(self) -> NamedMapping[App]:
        app_dicts = self.__client.component.get_apps_for_user(
            directory_id=self.directory_id
        )

        apps = {
            app.app_id: app
            for app in (
                App.from_dict(data=app_dict, client=self.__client)
                for app_dict in app_dicts
            )
        }

        return NamedMapping(apps)
