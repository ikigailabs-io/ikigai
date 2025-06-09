# SPDX-FileCopyrightText: 2025-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from random import randbytes
from typing import Any, cast

from pydantic import BaseModel

from ikigai.components.specs import FacetType
from ikigai.typing.protocol import FlowDefinitionDict
from ikigai.utils.compatibility import Self

logger = logging.getLogger("ikigai.components")


class FacetBuilder:
    __name: str
    __arguments: dict[str, Any]
    __arrows: list[ArrowBuilder]
    __facet_spec: FacetType
    __facet: Facet | None
    __builder: FlowDefinitionBuilder

    def __init__(
        self, builder: FlowDefinitionBuilder, facet_type: FacetType, name: str = ""
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

    def arguments(self, **arguments: Any) -> Self:
        self.__arguments.update(arguments)
        return self

    def add_arrow(self, parent: FacetBuilder, args: dict | None = None) -> Self:
        if args is None:
            args = {}
        self.__arrows.append(
            ArrowBuilder(source=parent, destinition=self, arguments=args)
        )
        return self

    def _build(self) -> tuple[Facet, list[Arrow]]:
        if self.__facet is not None:
            error_msg = "Facet already built, cannot build again"
            raise RuntimeError(error_msg)

        # Check if the facet spec is satisfied
        self.__facet_spec.check_arguments(arguments=self.__arguments)

        self.__facet = Facet(
            facet_id=randbytes(4).hex(),
            facet_uid=self.__facet_spec.facet_uid,
            name=self.__name,
            arguments=self.__arguments,
        )

        arrows = [arrow_builder._build() for arrow_builder in self.__arrows]
        return self.__facet, arrows

    def build(self) -> FlowDefinition:
        return self.__builder.build()


class ArrowBuilder:
    source: FacetBuilder
    destinition: FacetBuilder
    arguments: dict[str, Any]

    def __init__(
        self, source: FacetBuilder, destinition: FacetBuilder, arguments: dict[str, Any]
    ) -> None:
        self.source = source
        self.destinition = destinition
        self.arguments = arguments

    def _build(self) -> Arrow:
        return Arrow(
            source=self.source.facet_id,
            destinition=self.destinition.facet_id,
            arguments=self.arguments,
        )


class FlowDefinitionBuilder:
    _facets: list[FacetBuilder]

    def __init__(self) -> None:
        self._facets = []

    def facet(self, facet_type: FacetType, name: str = "") -> FacetBuilder:
        facet_builder = FacetBuilder(builder=self, facet_type=facet_type, name=name)
        self._facets.append(facet_builder)
        return facet_builder

    def build(self) -> FlowDefinition:
        facets: list[Facet] = []
        arrows: list[Arrow] = []
        for facet_builder in self._facets:
            facet, arrows = facet_builder._build()
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
    arguments: dict[str, Any]


class Arrow(BaseModel):
    source: str
    destinition: str
    arguments: dict[str, Any]


class FlowDefinition(BaseModel):
    _facets: list[Facet] = []
    _arrows: list[Arrow] = []
    _arguments: dict = {}
    _variables: dict = {}
    _model_variables: dict = {}

    def to_dict(self) -> FlowDefinitionDict:
        # TODO: Check if this is correct
        return cast(FlowDefinitionDict, self.model_dump(by_alias=True))
