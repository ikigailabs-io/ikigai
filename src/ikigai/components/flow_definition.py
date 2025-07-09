# SPDX-FileCopyrightText: 2025-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from random import randbytes
from typing import Any, cast

from pydantic import BaseModel, Field

from ikigai.components.specs import FacetType
from ikigai.typing.protocol import FlowDefinitionDict, ModelType
from ikigai.utils.compatibility import Self, StrEnum

logger = logging.getLogger("ikigai.components")


class KnownModelFacetUIDS(StrEnum):
    """Known facet UIDs used for ml facets."""

    AiCast = "M_039"
    AiLLM = "M_041"
    AiMatch = "M_015"
    AiPlan = "M_036"
    AiPredict = "M_049"
    Predict = "M_016"

    @classmethod
    def values(cls) -> list[str]:
        """Get all known model facet UIDs."""
        return [member.value for member in cls.__members__.values()]


class FacetBuilder:
    __name: str
    __arguments: dict[str, Any]
    __arrow_builders: list[ArrowBuilder]
    __facet: Facet | None
    __arrows: list[Arrow] | None
    _facet_type: FacetType
    _builder: FlowDefinitionBuilder

    def __init__(
        self, builder: FlowDefinitionBuilder, facet_type: FacetType, name: str = ""
    ) -> None:
        self._builder = builder
        self._facet_type = facet_type
        self.__name = name
        self.__arguments = {}
        self.__arrow_builders = []
        self.__facet = None
        self.__arrows = None

        # TODO: Check if deprecation warning is needed

    @property
    def facet_id(self) -> str:
        if self.__facet is None:
            error_msg = "Facet not built yet, cannot access facet_id"
            raise RuntimeError(error_msg)
        return self.__facet.facet_id

    def facet(
        self,
        facet_type: FacetType,
        name: str = "",
        args: dict[str, Any] | None = None,
        arrow_args: dict[str, Any] | None = None,
    ) -> FacetBuilder:
        if arrow_args is None:
            arrow_args = {}
        facet = self._builder.facet(
            facet_type=facet_type, name=name, args=args
        ).add_arrow(self, **arrow_args)
        return facet

    def model_facet(
        self,
        facet_type: FacetType,
        model_type: ModelType,
        name: str = "",
        args: dict[str, Any] | None = None,
        arrow_args: dict[str, Any] | None = None,
    ) -> ModelFacetBuilder:
        if arrow_args is None:
            arrow_args = {}

        facet = self._builder.model_facet(
            facet_type=facet_type, model_type=model_type, name=name, args=args
        ).add_arrow(self, **arrow_args)
        return facet

    def arguments(self, **arguments: Any) -> Self:
        self.__arguments.update(arguments)
        return self

    def add_arrow(self, parent: FacetBuilder, /, **args) -> Self:
        self.__arrow_builders.append(
            ArrowBuilder(source=parent, destination=self, arguments=args)
        )
        return self

    def _build(self) -> tuple[Facet, list[Arrow]]:
        if self.__facet is not None:
            assert self.__arrows is not None, "Arrows should've been initialized"
            return self.__facet, self.__arrows

        # Check if the facet spec is satisfied
        self._facet_type.check_arguments(arguments=self.__arguments)

        self.__facet = Facet(
            facet_id=randbytes(4).hex(),
            facet_uid=self._facet_type.facet_uid,
            name=self.__name,
            arguments=self.__arguments,
        )

        self.__arrows = [
            arrow_builder._build() for arrow_builder in self.__arrow_builders
        ]
        return self.__facet, self.__arrows

    def build(self) -> FlowDefinition:
        flow_definition = self._builder.build()
        logger.debug("Built flow definition: %s", flow_definition.to_dict())
        return flow_definition


class ModelFacetBuilder(FacetBuilder):
    __model_type: ModelType
    __parameters: dict[str, Any] | None = None
    __hyperparameters: dict[str, Any] | None = None

    def __init__(
        self,
        builder: FlowDefinitionBuilder,
        facet_type: FacetType,
        model_type: ModelType,
        name: str = "",
    ) -> None:
        super().__init__(builder=builder, facet_type=facet_type, name=name)
        if not any(arg.name == "model_name" for arg in facet_type.facet_arguments):
            error_msg = "Facet type must be a model facet"
            raise ValueError(error_msg)

        # TODO: Add check that model_type is compatible with the facet type
        self.__model_type = model_type

        if any(arg.name == "hyperparameters" for arg in facet_type.facet_arguments):
            self.__hyperparameters = {}

        if any(arg.name == "parameters" for arg in facet_type.facet_arguments):
            self.__parameters = {}

    def hyperparameters(self, **hyperparameters: Any) -> Self:
        if self.__hyperparameters is None:
            error_msg = "Facet type does not support hyperparameters"
            raise RuntimeError(error_msg)
        self.__hyperparameters.update(hyperparameters)
        return self

    def parameters(self, **parameters: Any) -> Self:
        if self.__parameters is None:
            error_msg = "Facet type does not support parameters"
            raise RuntimeError(error_msg)
        self.__parameters.update(parameters)
        return self

    def _build(self) -> tuple[Facet, list[Arrow]]:
        if self.__hyperparameters is not None:
            self.arguments(hyperparameters=self.__hyperparameters)
        if self.__parameters is not None:
            self.arguments(parameters=self.__parameters)
        return super()._build()


class ArrowBuilder:
    source: FacetBuilder
    destination: FacetBuilder
    arguments: dict[str, Any]

    def __init__(
        self, source: FacetBuilder, destination: FacetBuilder, arguments: dict[str, Any]
    ) -> None:
        self.source = source
        self.destination = destination
        self.arguments = arguments

    def _build(self) -> Arrow:
        return Arrow(
            source=self.source.facet_id,
            destination=self.destination.facet_id,
            arguments=self.arguments,
        )


class FlowDefinitionBuilder:
    _facets: list[FacetBuilder]

    def __init__(self) -> None:
        self._facets = []

    def facet(
        self, facet_type: FacetType, name: str = "", args: dict[str, Any] | None = None
    ) -> FacetBuilder:
        if args is None:
            args = {}
        facet_builder = FacetBuilder(
            builder=self, facet_type=facet_type, name=name
        ).arguments(**args)
        self._facets.append(facet_builder)
        return facet_builder

    def model_facet(
        self,
        facet_type: FacetType,
        model_type: ModelType,
        name: str = "",
        args: dict[str, Any] | None = None,
    ) -> ModelFacetBuilder:
        if facet_type.facet_uid not in KnownModelFacetUIDS.values():
            error_msg = f"{facet_type.name.title()} is not a known Model Facet"
            raise ValueError(error_msg)
        if args is None:
            args = {}
        facet_builder = ModelFacetBuilder(
            builder=self, facet_type=facet_type, model_type=model_type, name=name
        ).arguments(**args)
        self._facets.append(facet_builder)
        return facet_builder

    def build(self) -> FlowDefinition:
        facets: list[Facet] = []
        arrows: list[Arrow] = []
        for facet_builder in self._facets:
            facet, in_arrows = facet_builder._build()
            facets.append(facet)
            arrows.extend(in_arrows)
        flow_definition = FlowDefinition(
            facets=facets,
            arrows=arrows,
            arguments={},
            variables={},
            model_variables={},
        )
        return flow_definition


class Facet(BaseModel):
    facet_id: str
    facet_uid: str
    name: str = ""
    arguments: dict[str, Any]


class Arrow(BaseModel):
    source: str
    destination: str
    arguments: dict[str, Any]


class FlowDefinition(BaseModel):
    facets: list[Facet] = Field(default_factory=list)
    arrows: list[Arrow] = Field(default_factory=list)
    arguments: dict = Field(default_factory=dict)
    variables: dict = Field(default_factory=dict)
    model_variables: dict = Field(default_factory=dict)

    def to_dict(self) -> FlowDefinitionDict:
        # TODO: Check if this is correct
        return cast(FlowDefinitionDict, self.model_dump(by_alias=True))
