# SPDX-FileCopyrightText: 2026-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import ast
import textwrap
from collections.abc import Mapping
from datetime import datetime
from functools import cached_property
from logging import getLogger
from pathlib import Path
from typing import Any

from pydantic import (
    AliasChoices,
    BaseModel,
    EmailStr,
    Field,
    PrivateAttr,
    field_validator,
)

from ikigai.client import Client, datax
from ikigai.specs import (
    CustomFacetArgumentSpec,
    CustomFacetType,
    FacetType,
    FacetTypes,
)
from ikigai.typing import ComponentBrowser, NamedMapping
from ikigai.utils import CustomFacetAccessLevel, CustomFacetArgumentType
from ikigai.utils.compatibility import Self, deprecated

logger = getLogger("ikigai.components")


class CustomFacetBuilder:
    _name: str
    _facet_type: FacetType | None
    _description: str
    _script: str
    _requirements: list[str]
    _system_access: bool
    _arguments: dict[str, CustomFacetArgumentSpec]
    __client: Client

    def __init__(self, client: Client) -> None:
        """
        Initialize the CustomFacetBuilder

        Parameters
        ----------
        client : Client
            The Ikigai client to use for API interactions

        Returns
        -------
        None
        """
        self.__client = client
        self._name = ""
        self._facet_type = None
        self._description = ""
        self._script = ""
        self._requirements = []
        self._system_access = False
        self._arguments = {}

    def new(self, name: str, facet_type: FacetType) -> Self:
        self._name = name
        self._facet_type = facet_type
        return self

    def description(self, description: str) -> Self:
        """
        Specify the description for the custom facet.

        Parameters
        ----------
        description : str
            The description for the custom facet.

        Returns
        -------
        Self
            The CustomFacetBuilder instance with the description set.
        """
        self._description = description
        return self

    def script(
        self,
        script: str | Path,
        *,
        requirements: list[str] | Path | None = None,
        system_access: bool = False,
        arguments: dict[str, str | int | float | bool] | None = None,
    ) -> Self:
        """
        Set the script and related dependencies for the custom facet

        You can specify the script and any PyPI libraries,
        as well as the arguments that are required to run the script.
        By default, the script has limited access to filesystem and environment,
        but you can request for more access to the environment, filesystem, and syscalls
        by setting the system_access flag to True.

        Note
        -----
        The user must have rootkit access to request system access.

        Parameters
        ----------
        script : str | Path
            The draft script for the custom facet.
            Can either be the text of the script or
            a path to a file containing the script.

        requirements : list[str] | Path | None
            The requirements for the custom facet.
            Can either be a path to a file containing the requirements in pip format,
            or be a list of strings each representing a single requirement.

        system_access : bool, optional
            Whether to grant system access to the custom facet, by default False.
            If True, the custom facet will have unrestricted access to the
            python environment and libraries.
            Creating a custom facet with system access will fail if
            the user does not have rootkit access.

        arguments : dict[str, str | int | float | bool]
            The arguments for the custom facet script and their default values.

        Examples
        --------
        >>> script_file = Path("./script.py")
        >>> builder = ikigai.custom_facet.new(...)
        >>> builder.script(script=script_file)

        >>> builder = ikigai.custom_facet.new(...)
        >>> builder.script(
        ...    script="result = data  # no-op",
        ...    requirements=["scikit-learn", "pandas==1.5.2"],
        ...    system_access=True,
        ...    arguments={"input-1": "input-1"},
        ... )

        >>> script_file = Path("./script.py")
        >>> builder = ikigai.custom_facet.new(...)
        >>> builder.script(
        ...    script=script_file,
        ...    requirements=Path("requirements.txt"),
        ...    system_access=True,
        ...    arguments={"input-1": "input-1", "input-2": "input-2"},
        ... )

        Returns
        -------
        Self
            The CustomFacetBuilder instance with the script set.
        """
        if isinstance(script, Path):
            with script.open("r") as fp:
                script = fp.read()
        script = textwrap.dedent(script)
        # Validate the script syntax againt ikigai platform's python version
        # IPLT-11330: See if we can avoid hardcoding the python version
        ast.parse(script, feature_version=(3, 10))
        self._script = script

        if requirements is None:
            requirements = []
        if isinstance(requirements, Path):
            with requirements.open("r") as fp:
                requirements = fp.readlines()
        self._requirements = requirements

        if arguments is None:
            arguments = {}
        self._arguments = {
            name: CustomFacetArgumentSpec(
                name=name,
                argument_type=CustomFacetArgumentType.from_value(value),
                value=value,
            )
            for name, value in arguments.items()
        }

        self._system_access = system_access
        return self

    def build(self) -> CustomFacet:
        """
        Build the custom facet object.

        Creates the custom facet in the Ikigai platform using the provided
        parameters and returns the corresponding CustomFacet object.

        Returns
        -------
        CustomFacet
            The created CustomFacet object.
        """
        # Validate the facet type
        if self._facet_type is None:
            error_msg = "Facet type is required to build a CustomFacet"
            raise ValueError(error_msg)

        # If rootkit is required, generate it from the script
        rootkit_token = (
            self.__client.access.generate_rootkit_token(script=self._script)
            if self._system_access
            else ""
        )

        # Create the custom facet
        arguments = [argument.to_dict() for argument in self._arguments.values()]

        custom_facet_id = self.__client.component.create_custom_facet(
            name=self._name,
            chain_group=self._facet_type.facet_info.chain_group,
            description=self._description,
            tags=[],
            python_script=self._script,
            libraries=self._requirements,
            rootkit_token=rootkit_token,
            arguments=arguments,
        )

        custom_facet_dict = self.__client.component.get_custom_facet(
            custom_facet_id=custom_facet_id,
        )
        return CustomFacet.from_dict(data=custom_facet_dict, client=self.__client)


class CustomFacetAccess(BaseModel):
    """
    Access manager for the Custom Facet.

    Grant/Update/Revoke access to the Custom Facet.
    """

    __custom_facet_id: str = PrivateAttr()
    __client: Client = PrivateAttr()

    def __init__(self, *, custom_facet_id: str, client: Client) -> None:
        super().__init__()
        self.__custom_facet_id = custom_facet_id
        self.__client = client

    def grant(self, email: EmailStr, access_level: CustomFacetAccessLevel) -> Self:
        """
        Grant access to the Custom Facet.

        Parameters
        ----------

        email: EmailStr
            Email address of the user to grant access to.

        access_level: CustomFacetAccessLevel
            Access level to grant to the user.

        Returns
        -------
        Self
            Access manager for the Custom Facet.
        """
        self.__client.component.grant_custom_facet_access(
            custom_facet_id=self.__custom_facet_id,
            email=email,
            access_level=access_level,
        )
        return self

    def update(self, email: EmailStr, access_level: CustomFacetAccessLevel) -> Self:
        """
        Update access to the Custom Facet.

        Parameters
        ----------

        email: EmailStr
            Email address of the user to update access for.

        access_level: CustomFacetAccessLevel
            New access level for the user.

        Returns
        -------
        Self
            Access manager for the Custom Facet.
        """
        self.__client.component.update_custom_facet_access(
            custom_facet_id=self.__custom_facet_id,
            email=email,
            access_level=access_level,
        )
        return self

    def revoke(self, email: EmailStr) -> Self:
        """
        Revoke access to the Custom Facet.

        Note
        -----

        Ikigai does not support revoking access to a custom facet.
        Please file a feature request if you need this.

        """
        error_msg = (
            "Revoking access to a custom facet is not supported, please file a feature "
            "request if you need this"
        )
        raise NotImplementedError(error_msg)


class CustomFacet(BaseModel):
    custom_facet_id: str
    name: str
    facet_type: FacetType
    description: str
    script: str = Field(validation_alias=AliasChoices("script", "python_script"))
    requirements: list[str] = Field(
        validation_alias=AliasChoices("requirements", "libraries")
    )
    rootkit_token: str
    arguments: dict[str, CustomFacetArgumentSpec]
    created_at: datetime
    modified_at: datetime
    __client: Client = PrivateAttr()

    @field_validator("arguments", mode="before")
    @classmethod
    def validate_arguments(cls, v: list[dict]) -> dict[str, CustomFacetArgumentSpec]:
        return {
            argument["name"]: CustomFacetArgumentSpec.model_validate(argument)
            for argument in v
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any], client: Client) -> Self:
        logger.debug("Creating a %s from %s", cls.__name__, data)
        facet_types = FacetTypes.from_dict(client.component.get_facet_specs())
        facet_type = facet_types.find_by_uid(uid=data["facet_uid"])
        self = cls.model_validate({**data, "facet_type": facet_type})
        self.__client = client
        return self

    """
    Operations on Custom Facet
    """

    def rename(self, name: str) -> Self:
        """
        Rename the custom facet.

        Parameters
        ----------
        name : str
            The new name for the custom facet.

        Returns
        -------
        Self
            The CustomFacet instance with the name set.
        """
        self.__client.component.edit_custom_facet(
            custom_facet_id=self.custom_facet_id,
            chain_group=self.facet_type.facet_info.chain_group,
            name=name,
        )
        self.name = name
        return self

    def update_description(self, description: str) -> Self:
        """
        Update the description for the custom facet.

        Parameters
        ----------
        description : str
            The new description for the custom facet.

        Returns
        -------
        Self
            The CustomFacet instance with the new description.
        """
        self.__client.component.edit_custom_facet(
            custom_facet_id=self.custom_facet_id,
            chain_group=self.facet_type.facet_info.chain_group,
            description=description,
        )
        self.description = description
        return self

    def update_script(
        self,
        script: str | Path,
        *,
        requirements: list[str] | Path | None = None,
        system_access: bool = False,
        arguments: dict[str, str | int | float | bool] | None = None,
    ) -> Self:
        """
        Update the script and related dependencies for the custom facet

        You can specify the script and any PyPI libraries,
        as well as the arguments that are required to run the script.
        By default, the script has limited access to filesystem and environment,
        but you can request for more access to the environment, filesystem, and syscalls
        by setting the system_access flag to True.

        Note
        -----
        The user must have rootkit access to request system access.

        Parameters
        ----------
        script : str | Path
            The draft script for the custom facet.
            Can either be the text of the script or
            a path to a file containing the script.

        requirements : list[str] | Path | None
            The requirements for the custom facet.
            Can either be a path to a file containing the requirements in pip format,
            or be a list of strings each representing a single requirement.

        system_access : bool, optional
            Whether to grant system access to the custom facet, by default False.
            If True, the custom facet will have unrestricted access to the
            python environment and libraries.
            Creating a custom facet with system access will fail if
            the user does not have rootkit access.

        arguments : dict[str, str | int | float | bool]
            The arguments for the custom facet script and their default values.

        Returns
        -------
        Self
            The updated CustomFacet instance.
        """
        if isinstance(script, Path):
            with script.open("r") as fp:
                script = fp.read()
        script = textwrap.dedent(script)
        # Validate the script syntax againt ikigai platform's python version
        # IPLT-11330: See if we can avoid hardcoding the python version
        ast.parse(script, feature_version=(3, 10))

        if requirements is None:
            requirements = []
        if isinstance(requirements, Path):
            with requirements.open("r") as fp:
                requirements = fp.readlines()

        if arguments is None:
            arguments = {}
        new_arguments = {
            name: CustomFacetArgumentSpec(
                name=name,
                argument_type=CustomFacetArgumentType.from_value(value),
                value=value,
            )
            for name, value in arguments.items()
        }

        # If rootkit is required, generate it from the script
        rootkit_token = (
            self.__client.access.generate_rootkit_token(script=script)
            if system_access
            else ""
        )

        # Update the custom facet
        arguments_list = [argument.to_dict() for argument in new_arguments.values()]

        self.__client.component.edit_custom_facet(
            custom_facet_id=self.custom_facet_id,
            chain_group=self.facet_type.facet_info.chain_group,
            python_script=script,
            libraries=requirements,
            rootkit_token=rootkit_token,
            arguments=arguments_list,
        )

        self.script = script
        self.requirements = requirements
        self.rootkit_token = rootkit_token
        self.arguments = new_arguments
        return self

    @cached_property
    def access(self) -> CustomFacetAccess:
        """
        Manage access to the Custom Facet.

        Returns
        -------
        CustomFacetAccess
            Access manager for the Custom Facet.
        """
        return CustomFacetAccess(
            custom_facet_id=self.custom_facet_id, client=self.__client
        )

    def describe(self) -> datax.CustomFacetDict:
        return self.__client.component.get_custom_facet(
            custom_facet_id=self.custom_facet_id
        )

    def delete(self) -> None:
        self.__client.component.delete_custom_facet(
            custom_facet_id=self.custom_facet_id
        )
        return None

    def create_version(self, name: str) -> CustomFacetVersion:
        arguments_list = [argument.to_dict() for argument in self.arguments.values()]

        custom_facet_version_id = self.__client.component.create_custom_facet_version(
            custom_facet_id=self.custom_facet_id,
            version=name,
            description=self.description,
            python_script=self.script,
            libraries=self.requirements,
            rootkit_token=self.rootkit_token,
            arguments=arguments_list,
        )

        custom_facet_version_dict = self.__client.component.get_custom_facet_version(
            custom_facet_id=self.custom_facet_id,
            version_id=custom_facet_version_id,
        )

        return CustomFacetVersion.from_dict(
            data=custom_facet_version_dict,
            facet_type=self.facet_type,
            client=self.__client,
        )

    def versions(self) -> NamedMapping[CustomFacetVersion]:
        version_dicts = self.__client.component.get_custom_facet_versions(
            custom_facet_id=self.custom_facet_id
        )
        versions = {
            version.version_id: version
            for version in (
                CustomFacetVersion.from_dict(
                    data=version_dict, facet_type=self.facet_type, client=self.__client
                )
                for version_dict in version_dicts
            )
        }
        return NamedMapping(versions)

    def unpinned(self) -> CustomFacetVersion:
        latest_version = next(
            iter(
                sorted(
                    self.versions().values(), key=lambda x: x.created_at, reverse=True
                )
            ),
            None,
        )

        description = latest_version.description if latest_version else self.description
        arguments = [
            argument.to_dict()
            for argument in (
                latest_version.arguments if latest_version else self.arguments
            ).values()
        ]
        created_at = str(
            int(
                (
                    latest_version.created_at if latest_version else self.created_at
                ).timestamp()
            )
        )

        return CustomFacetVersion.from_dict(
            data={
                "version": "",
                "version_id": "",
                "custom_facet_id": self.custom_facet_id,
                "description": description,
                "arguments": arguments,
                "created_at": created_at,
            },
            facet_type=self.facet_type,
            client=self.__client,
        )


class CustomFacetBrowser(ComponentBrowser[CustomFacet]):
    __client: Client

    def __init__(self, client: Client) -> None:
        self.__client = client

    @deprecated(
        "Prefer directly loading by name:\n\tikigai.custom_facets['custom_facet_name']"
    )
    def __call__(self) -> NamedMapping[CustomFacet]:
        custom_facets = {
            custom_facet["custom_facet_id"]: CustomFacet.from_dict(
                data=custom_facet, client=self.__client
            )
            for custom_facet in self.__client.component.get_custom_facets_for_user()
        }

        return NamedMapping(custom_facets)

    def __getitem__(self, name: str) -> CustomFacet:
        custom_facet_dict = self.__client.component.get_custom_facet_by_name(name=name)

        return CustomFacet.from_dict(data=custom_facet_dict, client=self.__client)

    def search(self, query: str) -> NamedMapping[CustomFacet]:
        matching_custom_facets = {
            custom_facet["custom_facet_id"]: CustomFacet.from_dict(
                data=custom_facet, client=self.__client
            )
            for custom_facet in self.__client.search.search_custom_facets_for_user(
                query=query
            )
        }

        return NamedMapping(matching_custom_facets)


class CustomFacetVersion(BaseModel):
    name: str = Field(validation_alias=AliasChoices("name", "version"))
    version_id: str
    custom_facet_id: str
    description: str
    arguments: dict[str, CustomFacetArgumentSpec]
    created_at: datetime
    __facet_type: CustomFacetType = PrivateAttr()
    __client: Client = PrivateAttr()

    @field_validator("arguments", mode="before")
    @classmethod
    def validate_arguments(cls, v: list[dict]) -> dict[str, CustomFacetArgumentSpec]:
        if not isinstance(v, list):
            error_msg = "Expected a list of argument dictionaries"
            raise ValueError(error_msg)

        return {
            argument["name"]: CustomFacetArgumentSpec.model_validate(argument)
            for argument in v
        }

    @classmethod
    def from_dict(
        cls, data: datax.CustomFacetVersionDict, facet_type: FacetType, client: Client
    ) -> Self:
        logger.debug("Creating a %s from %s", cls.__name__, data)
        self = cls.model_validate(data)
        self.__facet_type = CustomFacetType.from_facet_type(
            facet_type=facet_type,
            custom_facet_id=self.custom_facet_id,
            version_id=self.version_id,
            custom_facet_argument_specs=self.arguments,
        )
        self.__client = client
        return self

    @property
    def facet_type(self) -> CustomFacetType:
        return self.__facet_type
