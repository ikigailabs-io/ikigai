# SPDX-FileCopyrightText: 2026-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import ast
from collections.abc import Mapping
from datetime import datetime
from logging import getLogger
from pathlib import Path
from typing import Any

from pydantic import AliasChoices, BaseModel, Field, PrivateAttr

from ikigai.client import Client
from ikigai.specs import (
    CustomFacetArgumentSpec,
    CustomFacetType,
    FacetType,
    FacetTypes,
)
from ikigai.typing import ComponentBrowser, NamedMapping
from ikigai.utils import CustomFacetArgumentType
from ikigai.utils.compatibility import Self, deprecated

logger = getLogger("ikigai.components")


class CustomFacetBuilder:
    _name: str
    _facet_type: FacetType | None
    _description: str
    _script: str
    _requirements: list[str]
    _tags: list[str]
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
        self._tags = []
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

    def tags(self, tags: list[str]) -> Self:
        """
        Specify the tags for the custom facet.

        Parameters
        ----------
        tags : list[str]
            The tags for the custom facet.

        Returns
        -------
        Self
            The CustomFacetBuilder instance with the tags set.
        """
        self._tags = tags
        return self

    def script(self, script: str | Path, system_access: bool = False) -> Self:
        """
        Set the draft script for the custom facet

        Parameters
        ----------
        script : str | Path
            The draft script for the custom facet.
            Can either be the text of the script or
            a path to a file containing the script.

        system_access : bool, optional
            Whether to grant system access to the custom facet, by default False.
            If True, the custom facet will have unrestricted access to the
            python environment and libraries.
            Creating a custom facet with system access will fail if
            the user does not have rootkit access.

        Examples
        --------
        >>> builder.script("result = data  # no-op")
        >>> builder.script(Path("./script.py"))

        Returns
        -------
        Self
            The CustomFacetBuilder instance with the script set.
        """
        if isinstance(script, Path):
            with script.open("r") as fp:
                script = fp.read()

        # Validate the script syntax againt ikigai platform's python version
        # IPLT-11330: See if we can avoid hardcoding the python version
        ast.parse(script, feature_version=(3, 10))

        self._script = script
        self._system_access = system_access
        return self

    def requirements(self, requirements: list[str] | Path | str) -> Self:
        """
        Specify the library requirements for the custom facet.

        Parameters
        ----------
        requirements : list[str] | Path | str
            The requirements for the custom facet.
            Can either be a path to a file containing the requirements in pip format,
            or be a list of strings each representing a single requirement,
            or a string path to a file containing the requirements.

        Examples
        --------
        >>> builder.requirements(["scikit-learn", "pandas==1.5.2"])
        >>> builder.requirements(Path("requirements.txt"))
        >>> builder.requirements("./requirements.txt")

        Returns
        -------
        Self
            The CustomFacetBuilder instance with the library requirements set.
        """
        if isinstance(requirements, str):
            requirements = Path(requirements)
        if isinstance(requirements, Path):
            with requirements.open("r") as fp:
                requirements = fp.readlines()

        self._requirements = requirements
        return self

    def arguments(self, **arguments: str | int | float | bool) -> Self:
        """
        Specify the arguments for the custom facet.

        Parameters
        ----------
        arguments : **str | int | float | bool
            The arguments for the custom facet.

        Returns
        -------
        Self
            The CustomFacetBuilder instance with the arguments defined.
        """
        self._arguments = {
            name: CustomFacetArgumentSpec(
                name=name,
                argument_type=CustomFacetArgumentType.from_value(value),
                value=value,
            )
            for name, value in arguments.items()
        }
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
            self.__client.access.generate_rootkit_token(
                script=self._script,
            )
            if self._system_access
            else ""
        )

        # Create the custom facet
        arguments = [argument.to_dict() for argument in self._arguments.values()]

        custom_facet_id = self.__client.component.create_custom_facet(
            name=self._name,
            chain_group=self._facet_type.facet_info.facet_group,
            description=self._description,
            tags=self._tags,
            python_script=self._script,
            libraries=self._requirements,
            rootkit_token=rootkit_token,
            arguments=arguments,
        )

        custom_facet_dict = self.__client.component.get_custom_facet(
            custom_facet_id=custom_facet_id,
        )
        return CustomFacet.from_dict(data=custom_facet_dict, client=self.__client)


class CustomFacet(BaseModel):
    custom_facet_id: str
    name: str
    facet_spec: FacetType
    created_at: datetime
    modified_at: datetime
    __client: Client = PrivateAttr()

    @classmethod
    def from_dict(cls, data: Mapping[str, Any], client: Client) -> Self:
        logger.debug("Creating a %s from %s", cls.__name__, data)
        facet_types = FacetTypes.from_dict(client.component.get_facet_specs())
        facet_type = facet_types.find_by_uid(uid=data["facet_uid"])
        self = cls.model_validate({**data, "facet_spec": facet_type})
        self.__client = client
        return self

    def versions(self) -> NamedMapping[CustomFacetVersion]:
        version_dicts = self.__client.component.get_custom_facet_versions(
            custom_facet_id=self.custom_facet_id
        )
        versions = {
            version.version_id: version
            for version in (
                CustomFacetVersion.from_dict(
                    data=version_dict, facet_type=self.facet_spec, client=self.__client
                )
                for version_dict in version_dicts
            )
        }
        return NamedMapping(versions)

    def unpinned(self) -> CustomFacetVersion:
        return CustomFacetVersion.from_dict(
            data={
                "version": "",
                "version_id": "",
                "custom_facet_id": self.custom_facet_id,
                "arguments": [],
            },
            facet_type=self.facet_spec,
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
        custom_facet_dict = self.__client.component.get_custom_facet_by_name(name)
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
    arguments: NamedMapping[CustomFacetArgumentSpec]
    __facet_type: CustomFacetType = PrivateAttr()
    __client: Client = PrivateAttr()

    @classmethod
    def from_dict(
        cls, data: Mapping[str, Any], facet_type: FacetType, client: Client
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
