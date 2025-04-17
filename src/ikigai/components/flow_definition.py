# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from random import randbytes
from typing import cast

from pydantic import AliasPath, BaseModel, ConfigDict, Field

from ikigai.client.client import Client
from ikigai.typing.protocol import FlowDefinitionDict
from ikigai.utils.compatibility import Self

logger = logging.getLogger("ikigai.components")


class FacetRequirementSpec(BaseModel):
    max_child_count: int
    min_child_count: int
    max_parent_count: int
    min_parent_count: int


class ArgumentSpec(BaseModel):
    name: str
    type: str
    children: dict[str, ArgumentSpec]
    have_options: bool
    have_sub_arguments: bool
    is_deprecated: bool
    is_hidden: bool
    is_list: bool
    is_required: bool
    options: list


class FacetSpec(BaseModel):
    facet_uid: str = Field(validation_alias=AliasPath("facet_info", "facet_uid"))
    is_deprecated: bool
    is_hidden: bool
    facet_requirement: FacetRequirementSpec
    facet_arguments: list[ArgumentSpec]
    in_arrow_arguments: list[ArgumentSpec]
    out_arrow_arguments: list[ArgumentSpec]

    def check_arguments(self, arguments: dict) -> None: ...

    def check_in_arrows(self, arrows: list[ArrowBuilder]) -> None: ...

    def check_out_arrows(self, arrows: list[ArrowBuilder]) -> None: ...


class FacetBuilder:
    __name: str
    __arguments: dict
    __arrows: list[ArrowBuilder]
    __facet_spec: FacetSpec
    __facet: Facet | None
    __builder: FlowDefinitionBuilder

    def __init__(
        self, builder: FlowDefinitionBuilder, facet_type, name: str = ""
    ) -> None:
        self.__builder = builder
        self.__facet_spec = facet_type
        self.__name = name
        self.__arguments = {}
        self.__arrows = []
        self.__facet = None

        # TODO: Check if deprecation warning is needed

    @property
    def facet_id(self) -> str:
        if self.__facet is None:
            error_msg = "Facet not built yet, cannot access facet_id"
            raise RuntimeError(error_msg)
        return self.__facet.facet_id

    def facet(
        self, facet_type, name: str = "", arrow_args: dict | None = None
    ) -> FacetBuilder:
        facet = self.__builder.facet(facet_type=facet_type, name=name).add_arrow(
            parent=self, args=arrow_args
        )
        return facet

    def arguments(self, arguments: dict) -> Self:
        self.__arguments.update(arguments)
        return self

    def argument(self, key: str, value: str) -> Self:
        self.__arguments[key] = value
        return self

    def add_arrow(self, parent: FacetBuilder, args: dict | None = None) -> Self:
        if args is None:
            args = {}
        self.__arrows.append(
            ArrowBuilder(source=parent, destinition=self, arguments=args)
        )
        return self

    def build(self) -> tuple[Facet, list[Arrow]]:
        if self.__facet is not None:
            error_msg = "Facet already built, cannot build again"
            raise RuntimeError(error_msg)

        # Check if the facet spec is satisfied
        self.__facet_spec.check_arguments(arguments=self.__arguments)
        self.__facet_spec.check_in_arrows(arrows=self.__arrows)

        self.__facet = Facet(
            facet_id=randbytes(4).hex(),
            facet_uid=self.__facet_spec.facet_uid,
            name=self.__name,
            arguments=self.__arguments,
        )

        arrows = [arrow_builder.build() for arrow_builder in self.__arrows]
        return self.__facet, arrows


class ArrowBuilder:
    source: FacetBuilder
    destinition: FacetBuilder
    arguments: dict

    def __init__(
        self, source: FacetBuilder, destinition: FacetBuilder, arguments: dict
    ) -> None:
        self.source = source
        self.destinition = destinition
        self.arguments = arguments

    def build(self) -> Arrow:
        return Arrow(
            source=self.source.facet_id,
            destinition=self.destinition.facet_id,
            arguments=self.arguments,
        )


class FacetSpecs(BaseModel):
    INPUT: dict[str, FacetSpec]
    MID: dict[str, FacetSpec]
    OUTPUT: dict[str, FacetSpec]

    model_config = ConfigDict(frozen=True)

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls.model_validate(data)


class FlowDefinitionBuilder:
    _facets: list[FacetBuilder]
    __facet_specs: FacetSpecs
    __client: Client

    def __init__(self, client: Client) -> None:
        self.__client = client
        self.__facet_specs = FacetSpecs.from_dict(
            self.__client.component.get_facet_specs()
        )
        self._facets = []

    def facet(self, facet_type, name: str = "") -> FacetBuilder:
        facet_builder = FacetBuilder(builder=self, facet_type=facet_type, name=name)
        self._facets.append(facet_builder)
        return facet_builder

    def build(self) -> FlowDefinition:
        facets: list[Facet] = []
        arrows: list[Arrow] = []
        for facet_builder in self._facets:
            facet, arrows = facet_builder.build()
            facets.append(facet)
            arrows.extend(arrows)
        flow_definition = FlowDefinition(
            _facets=facets,
            _arrows=arrows,
            _arguments={},
            _variables={},
            _model_variables={},
        )
        return flow_definition


class Facet(BaseModel):
    facet_id: str
    facet_uid: str
    name: str = ""
    arguments: dict


class Arrow(BaseModel):
    source: str
    destinition: str
    arguments: dict


class FlowDefinition(BaseModel):
    _facets: list[Facet] = []
    _arrows: list[Arrow] = []
    _arguments: dict = {}
    _variables: dict = {}
    _model_variables: dict = {}

    def to_dict(self) -> FlowDefinitionDict:
        # TODO: Check if this is correct
        return cast(FlowDefinitionDict, self.model_dump(by_alias=True))
