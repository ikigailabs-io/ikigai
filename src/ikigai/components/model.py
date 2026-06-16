# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, Field, PrivateAttr

from ikigai.client import Client
from ikigai.specs import SubModelSpec
from ikigai.typing import ComponentBrowser, Directory, NamedDirectoryDict, NamedMapping
from ikigai.utils import DirectoryType
from ikigai.utils.compatibility import Self, deprecated, override

logger = logging.getLogger("ikigai.components")


class ModelBuilder:
    """
    Builder class for creating new models within an app.

    Configure a model using the `new`, `model_type`, `description`, and
    `directory` methods, then call `build` to create the model. The resulting
    `Model` is returned.

    Examples
    --------

    >>> model = (
    ...     app.model.new("Simple Linear Regression with Lasso")
    ...     .model_type(model_type=model_types.Linear.Lasso)
    ...     .build()
    ... )
    """
    _app_id: str
    _name: str
    _directory: Directory | None
    _model_type: SubModelSpec | None
    _description: str
    __client: Client

    def __init__(self, client: Client, app_id: str) -> None:
        self.__client = client
        self._app_id = app_id
        self._name = ""
        self._directory = None
        self._model_type = None
        self._description = ""

    def new(self, name: str) -> Self:
        """
        Create a new model in the current app with the specified name.

        Parameters
        ----------

        name: str
            Name of the new model.

        Returns
        -------

        ModelBuilder
            The builder instance. Enables method chaining.

        Examples
        --------

        >>> new_model = app.model.new("Simple Linear Regression with Lasso")
        """
        self._name = name
        return self

    def directory(self, directory: Directory) -> Self:
        """
        Set the directory where the model will be stored.

        Parameters
        ----------

        directory: Directory
            The target storage location.

        Returns
        -------

        ModelBuilder
            The builder instance. Enables method chaining.
        """
        self._directory = directory
        return self

    def model_type(self, model_type: SubModelSpec) -> Self:
        """
        Set the model type.

        Call `model_types.types` to view a list of all available Ikigai model
        types.

        Parameters
        ----------
        model_type : SubModelSpec
            Specification describing the model type and configuration.

        Returns
        -------
        ModelBuilder
            The builder instance. Enables method chaining.

        Examples
        --------

        model = app.model.model_type(model_type="Linear")
        """
        self._model_type = model_type
        return self

    def description(self, description: str) -> Self:
        """
        Set the model description.

        Parameters
        ----------
        description : str
            Description for the model.

        Returns
        -------
        ModelBuilder
            The builder instance. Enables method chaining.
        """
        self._description = description
        return self

    def build(self) -> Model:
        """
        Create the model using the configurations.

        This method creates a new model using the configured name, model type,
        directory, and description, and returns a `Model` instance.

        Returns
        -------
        Model
            The created model instance populated with the configurations.
        """
        if self._model_type is None:
            error_msg = "Model type must be specified"
            raise ValueError(error_msg)

        model_id = self.__client.component.create_model(
            app_id=self._app_id,
            name=self._name,
            directory=self._directory,
            model_type=self._model_type,
            description=self._description,
        )
        # Populate the model object
        model_dict = self.__client.component.get_model(
            app_id=self._app_id, model_id=model_id
        )

        return Model.from_dict(data=model_dict, client=self.__client)


class Model(BaseModel):
    """
    A Model on the Ikigai platform.

    Attributes
    ----------

    app_id: str
        The app this model belongs to.

    model_id: str
        Unique identifier of the model.

    name: str
        Name of the model.

    model_type: str
        Model type of this model.

    sub_model_type: str
        Submodel type of this model.

    description: str
        Description for this model.

    created_at: datetime
        Datetime indicating when the model was created.

    modified_at: datetime
        Datetime indicating when the model was last modified.
    """
    app_id: str = Field(validation_alias=AliasChoices("app_id", "project_id"))
    model_id: str
    name: str
    model_type: str
    sub_model_type: str
    description: str
    created_at: datetime
    modified_at: datetime
    __client: Client = PrivateAttr()

    @classmethod
    def from_dict(cls, data: Mapping[str, Any], client: Client) -> Self:
        logger.debug("Creating a %s from %s", cls.__name__, data)
        self = cls.model_validate(data)
        self.__client = client
        return self

    def delete(self) -> None:
        """
        Delete the model.

        Returns
        -------

        None
        """
        self.__client.component.delete_model(app_id=self.app_id, model_id=self.model_id)
        return None

    def rename(self, name: str) -> Self:
        """
        Rename the model.

        Parameters
        ----------

        name: str
            New name for the model.

        Returns
        -------

        Model
            The updated model instance.
        """
        self.__client.component.edit_model(
            app_id=self.app_id, model_id=self.model_id, name=name
        )
        self.name = name
        return self

    def move(self, directory: Directory) -> Self:
        """
        Move the model to a different directory.

        Parameters
        ----------

        directory: Directory
            Target directory to which the model should be moved.

        Returns
        -------

        Model
            The updated model instance.
        """
        self.__client.component.edit_model(
            app_id=self.app_id, model_id=self.model_id, directory=directory
        )
        return self

    def update_description(self, description: str) -> Self:
        """
        Update the model description.

        Parameters
        ----------

        description: str
            New description.

        Returns
        -------

        Model
            The updated model instance.
        """
        self.__client.component.edit_model(
            app_id=self.app_id, model_id=self.model_id, description=description
        )
        self.description = description
        return self

    def versions(self) -> NamedMapping[ModelVersion]:
        """
        Get all versions of the model.

        Returns
        -------

        NamedMapping[ModelVersion]
            Mapping of version IDs to model version objects.
        """
        version_dicts = self.__client.component.get_model_versions(
            app_id=self.app_id, model_id=self.model_id
        )
        versions = {
            version.version_id: version
            for version in (
                ModelVersion.from_dict(
                    app_id=self.app_id, data=version_dict, client=self.__client
                )
                for version_dict in version_dicts
            )
        }

        return NamedMapping(versions)

    def describe(self) -> Mapping[str, Any]:
        """
        Get details about the model, including creation time, directory
        location, type, and other information.

        Returns
        -------

        Mapping[str, Any]
            Dictionary containing model details.
        """
        return self.__client.component.get_model(
            app_id=self.app_id, model_id=self.model_id
        )


class ModelBrowser(ComponentBrowser[Model]):
    """
    Provides access to models by name and search functionality.
    """
    __app_id: str
    __client: Client

    def __init__(self, app_id: str, client: Client) -> None:
        self.__app_id = app_id
        self.__client = client

    @deprecated("Prefer directly loading by name:\n\tapp.models['model_name']")
    @override
    def __call__(self) -> NamedMapping[Model]:
        models = {
            model["model_id"]: Model.from_dict(data=model, client=self.__client)
            for model in self.__client.component.get_models_for_app(
                app_id=self.__app_id
            )
        }

        return NamedMapping(models)

    @override
    def __getitem__(self, name: str) -> Model:
        model_dict = self.__client.component.get_model_by_name(
            app_id=self.__app_id, name=name
        )

        return Model.from_dict(data=model_dict, client=self.__client)

    @override
    def search(self, query: str) -> NamedMapping[Model]:
        """
        Search for models in the current app matching a query string.

        Parameters
        ----------

        query: str
            String used to match models.

        Returns
        -------

        NamedMapping[Model]
            A mapping of models that match the provided string.

        Examples
        --------

        >>> results = app.models.search("example model")
        >>> for model in results.values():
        ...     print(model.model_id)
        abcdef123456
        uvwxyz654321
        """
        matching_models = {
            model["model_id"]: Model.from_dict(data=model, client=self.__client)
            for model in self.__client.search.search_models_for_project(
                app_id=self.__app_id, query=query
            )
        }

        return NamedMapping(matching_models)


class ModelVersion(BaseModel):
    """
    A specific version of a model.

    Attributes
    ----------

    app_id: str
        The app this model version belongs to.

    model_id: str
        Unique identifier of the model.

    version_id: str
        Unique identifier of the model version.

    version: str
        Name of this model version.

    hyperparameters: dict[str, Any]
        Dictionary containing the hyperparameter configurations associated with
        this model version.

    metrics: dict[str, Any]
        Dictionary containing the metrics associated with this model version.

    created_at: datetime
        Datetime indicating when the model version was created.

    modified_at: datetime
        Datetime indicating when the model version was last modified.
    """
    app_id: str = Field(validation_alias=AliasChoices("app_id", "project_id"))
    model_id: str
    version_id: str
    version: str
    hyperparameters: dict[str, Any]
    metrics: dict[str, Any]
    created_at: datetime
    modified_at: datetime
    __client: Client = PrivateAttr()

    @property
    def name(self) -> str:
        # Implement the named protocol
        return self.version

    @classmethod
    def from_dict(cls, app_id: str, data: Mapping[str, Any], client: Client) -> Self:
        """
        Create a ModelVersion instance from a dictionary.

        Parameters
        ----------

        app_id: str
            The app this model version belongs to.

        data : Mapping[str, Any]
            This model version data.

        client : Client
            Client to use for API calls.

        Returns
        -------

        ModelVersion
            Model version instance.
        """
        logger.debug("Creating a %s from %s", cls.__name__, data)
        self = cls.model_validate({"app_id": app_id, **data})
        self.__client = client
        return self

    def describe(self) -> Mapping[str, Any]:
        """
        Get details about the model version, including when it was created,
        directory information, its type, and more.

        Returns
        -------

        Mapping[str, Any]
            Dictionary containing model version details.
        """
        return self.__client.component.get_model_version(
            app_id=self.app_id, version_id=self.version_id
        )


class ModelDirectoryBuilder:
    """
    Builder class for creating a model directory.

    Configure a model directory using the `new` method, then
    call `build` to create the directory. The resulting Model
    Directory instance is returned.

    Examples
    --------
    >>> ikigai = Ikigai(user_email="user@example.com", api_key="123abc")

    >>> app = ikigai.apps['Example App']
    >>> example_model_dir = app.model_directory.new("Example Dir").build()
    """
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
        """
        Create a new model directory in the current app with the specified
        name.

        Parameters
        ----------

        name: str
            Name of the new model directory.

        Returns
        -------

        ModelDirectoryBuilder
            The builder instance. Enables method chaining.

        Examples
        --------

        >>> new_model_dir = app.model_directory.new("Example Dir")
        """
        self._name = name
        return self

    def parent(self, parent: Directory) -> ModelDirectoryBuilder:
        """
        Set the parent directory for the new model directory.

        Parameters
        ----------

        parent: Directory
            The parent directory for the new directory.

        Returns
        -------

        ModelDirectoryBuilder
            The builder instance. Enables method chaining.
        """
        self._parent = parent
        return self

    def build(self) -> ModelDirectory:
        """
        Create the model directory using the provided configurations.

        This method creates a new model directory using the configured name
        and optional parent directory.

        Returns
        -------

        ModelDirectory
            The created model directory.

        Examples
        --------

        >>> example_model_dir = app.model_directory.new("Example Dir").build()
        """
        directory_id = self.__client.component.create_model_directory(
            app_id=self._app_id, name=self._name, parent=self._parent
        )
        directory_dict = self.__client.component.get_model_directory(
            app_id=self._app_id, directory_id=directory_id
        )

        return ModelDirectory.from_dict(data=directory_dict, client=self.__client)


class ModelDirectory(BaseModel):
    """
    A model directory within an app.

    Provides methods to navigate the model directory hierarchy and retrieve
    its contents.

    Attributes
    ----------

    app_id: str
        The app this directory belongs to.

    directory_id: str
        Unique identifier of the model directory.

    name: str
        Name of the directory.
    """
    app_id: str = Field(validation_alias=AliasChoices("app_id", "project_id"))
    directory_id: str
    name: str
    __client: Client = PrivateAttr()

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
        """
        Convert the model directory details to a dictionary representation.

        Returns
        -------

        NamedDirectoryDict
            Dictionary containing the model directory details.
        """
        return {"directory_id": self.directory_id, "type": self.type, "name": self.name}

    def directories(self) -> NamedMapping[Self]:
        """
        Get the subdirectories in the current model directory.

        Returns
        -------

        NamedMapping[ModelDirectory]
            Mapping of directory IDs.
        """
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
        """
        Get models in the current model directory.

        Returns
        -------

        NamedMapping[Model]
            Mapping of model IDs.
        """
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
