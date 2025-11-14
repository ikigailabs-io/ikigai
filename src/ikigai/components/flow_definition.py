# SPDX-FileCopyrightText: 2025-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from collections import defaultdict
from random import randbytes
from typing import Any, ClassVar, cast

from pydantic import BaseModel, Field

from ikigai.components.specs import FacetType
from ikigai.components.specs import SubModelSpec as ModelType
from ikigai.typing.protocol import FlowDefinitionDict, ModelHyperParameterGroupType
from ikigai.utils.compatibility import Self
from ikigai.utils.data_structures import merge

logger = logging.getLogger("ikigai.components")


class FacetBuilder:
    __name: str
    _arguments: dict[str, Any]
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
        self._arguments = {}
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

        return self._builder.facet(
            facet_type=facet_type, name=name, args=args
        ).add_arrow(self, **arrow_args)

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

        return self._builder.model_facet(
            facet_type=facet_type, model_type=model_type, name=name, args=args
        ).add_arrow(self, **arrow_args)

    def arguments(self, **arguments: Any) -> Self:
        self._arguments = merge(self._arguments, arguments)
        return self

    def add_arrow(self, parent: FacetBuilder, /, **args) -> Self:
        self.__arrow_builders.append(
            ArrowBuilder(source=parent, destination=self, arguments=args)
        )
        return self

    def _build(self) -> tuple[Facet, list[Arrow]]:
        if self.__facet is not None:
            if self.__arrows is None:
                error_msg = (
                    "Facet built but arrows missing, this should not happen. "
                    "Please report a bug."
                )
                raise RuntimeError(error_msg)
            return self.__facet, self.__arrows

        # Check if the facet spec is satisfied
        self._facet_type.check_arguments(arguments=self._arguments)

        self.__facet = Facet(
            facet_id=randbytes(4).hex(),  # noqa: S311 -- Not security relevant
            facet_uid=self._facet_type.facet_uid,
            name=self.__name,
            arguments=self._arguments,
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
    # TODO: @harsh-at-ikigailabs to make this dynamic
    __hyperparameter_aliases: ClassVar[set[str]] = {
        "hyperparameters",
        "model_selection",
        "processing",
        "metrics",
        "fine_tuning",
    }

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

        # TODO: @harsh-at-ikigailabs make this dynamic based on facet type
        if any(
            arg.name in self.__hyperparameter_aliases
            for arg in facet_type.facet_arguments
        ):
            self.__hyperparameters = {}

        if any(arg.name == "parameters" for arg in facet_type.facet_arguments):
            self.__parameters = {}

    def hyperparameters(self, **hyperparameters: Any) -> Self:
        if self.__hyperparameters is None:
            error_msg = "Facet type does not support hyperparameters"
            raise RuntimeError(error_msg)
        # Check if hyperparameter groups are needed for this model type
        hyperparameter_contains_groups = (
            hyperparameter.hyperparameter_group is not None
            for hyperparameter in self.__model_type.hyperparameters
        )
        if any(hyperparameter_contains_groups):
            hyperparameter_groups: ModelHyperParameterGroupType = defaultdict(dict)
            for hyperparameter in hyperparameters:
                group = self.__model_type._hyperparameter_groups[hyperparameter]
                hyperparameter_group = hyperparameter_groups[group]
                # Type narrowing for mypy
                if isinstance(hyperparameter_group, dict):
                    hyperparameter_group[hyperparameter] = hyperparameters[
                        hyperparameter
                    ]
                else:
                    message = "Unexpected hyperparameter group type"
                    raise RuntimeError(message)
            # Handle the facet spec arguments - Respect is_list from Facet Spec
            for group_name, group_params in hyperparameter_groups.items():
                facet_argument = next(
                    facet_argument
                    for facet_argument in self._facet_type.facet_arguments
                    if facet_argument.name == group_name
                )
                if facet_argument.is_list:
                    hyperparameter_groups[group_name] = cast(
                        list[dict[str, Any]], [group_params]
                    )
            self.arguments(**hyperparameter_groups)
        else:
            self.arguments(hyperparameters=hyperparameters)
        return self

    def parameters(self, **parameters: Any) -> Self:
        if self.__parameters is None:
            error_msg = "Facet type does not support parameters"
            raise RuntimeError(error_msg)
        self.arguments(parameters=parameters)
        return self


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
        if not facet_type.is_ml_facet():
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

        return FlowDefinition(
            facets=facets,
            arrows=arrows,
            arguments={},
            variables={},
            model_variables={},
        )


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
