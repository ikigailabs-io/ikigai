# SPDX-FileCopyrightText: 2026-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from logging import getLogger
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
from ikigai.utils.compatibility import Self, deprecated

logger = getLogger("ikigai.components")


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
