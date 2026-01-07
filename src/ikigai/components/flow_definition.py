# SPDX-FileCopyrightText: 2025-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, cast

from pydantic import BaseModel, ConfigDict, Field

from ikigai.components.specs import ArgumentType, FacetType
from ikigai.components.specs import SubModelSpec as ModelType
from ikigai.typing.protocol import FlowDefinitionDict, ModelHyperParameterGroupType
from ikigai.utils.compatibility import Self
from ikigai.utils.data_structures import merge_dicts

logger = logging.getLogger("ikigai.components")


class FlowVariable(BaseModel):
    facet_name: str
    argument_name: str = Field(serialization_alias="name")

    model_config = ConfigDict(frozen=True)


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
        self._validate_arguments(**arguments)
        return self._update_arguments(**arguments)

    def variables(self, **variables: str) -> Self:
        """
        Add flow variable that target an arguments of this facet.

        To add a variable targeting an argument of this facet,
        the facet must have a name.

        Parameters
        ----------
        **variables : dict
            Any number of keyword arguments where key is the variable name and value is
            the name of the argument of this facet that it should target.

        Examples
        --------
        Add a variable called 'dataset' targeting the dataset_id argument
        >>> IMPORTED = facet_types.INPUT.IMPORTED
        >>> builder = ikigai.builder
        >>> builder.facet(facet_type=IMPORTED, name="input").variables(
        ...     dataset="dataset_id",
        ... )

        Add a variable called 'dataset' targeting the dataset_name argument
        >>> EXPORTED = facet_types.OUTPUT.EXPORTED
        >>> builder = ikigai.builder
        >>> builder.facet(facet_type=EXPORTED, name="output").variables(
        ...     dataset="dataset_name",
        ... )

        Returns
        -------
        Self
            The current FacetBuilder object

        Raises
        ------
        RuntimeError
            If the facet is already built

        ValueError
            If the facet does not have a name

        ValueError
            If any of the arguments do not exist on the facet

        ValueError
            If any of the arguments are of type MAP or LIST.
            (Currently ikigai platform does not support MAP or LIST arguments)
        """
        if self.__facet:
            error_msg = "Facet already built, cannot set arguments"
            raise RuntimeError(error_msg)

        if not self.__name:
            error_msg = (
                "Variables are only allowed on facets that have a name. "
                "Please set a name for the facet."
            )
            raise ValueError(error_msg)

        facet_type_name = self._facet_type.name.title()
        errors: list[str] = []
        for variable_name, argument_name in variables.items():
            argument_spec = self._facet_type.facet_arguments.get(argument_name)

            # If argument does not exist on the facet, add an error
            if not argument_spec:
                errors.append(
                    f"{facet_type_name} facet does not have argument '{argument_name}'"
                )
                continue

            # If argument is of type MAP or LIST, add an error
            variable_type: str = (
                "LIST" if argument_spec.is_list else argument_spec.argument_type
            )
            if argument_spec.argument_type is ArgumentType.MAP or argument_spec.is_list:
                errors.append(
                    f"Variable {variable_name!r} targeting argument {argument_name!r} "
                    f"of type {variable_type} is currently not supported."
                )
                continue

            # If there is already a variable with the same name, add an error
            if (
                existing_variable := self._builder._variables.get(variable_name)
            ) and existing_variable.facet_name != self.__name:
                errors.append(
                    f"Variable {variable_name!r} already exists for another facet "
                    f"{existing_variable.facet_name}. Please use a different "
                    "variable name."
                )
                continue

        if errors:
            error_msg = "\n".join(errors)
            raise ValueError(error_msg)

        self._builder._add_variables(
            {
                variable_name: FlowVariable(
                    facet_name=self.__name,
                    argument_name=argument_name,
                )
                for variable_name, argument_name in variables.items()
            }
        )
        return self

    def add_arrow(self, parent: FacetBuilder, /, **args) -> Self:
        self.__arrow_builders.append(
            ArrowBuilder(source=parent, destination=self, arguments=args)
        )
        return self

    def _validate_arguments(self, **arguments: Any) -> None:
        facet_name = self._facet_type.name.title()
        for arg_name, arg_value in arguments.items():
            # Validate if argument is in facet spec
            if arg_name not in self._facet_type.facet_arguments:
                error_msg = f"Argument '{arg_name}' is not valid for {facet_name} facet"
                raise ValueError(error_msg)

            # Argument is present in facet spec, validate it
            arg_spec = self._facet_type.facet_arguments[arg_name]
            arg_spec.validate_value(facet=facet_name, value=arg_value)

    def _update_arguments(self, **arguments: Any) -> Self:
        self._arguments = merge_dicts(self._arguments, arguments)
        return self

    def _build(self, facet_id: str) -> tuple[Facet, list[Arrow]]:
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
            facet_id=facet_id,
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

    def __init__(
        self,
        builder: FlowDefinitionBuilder,
        facet_type: FacetType,
        model_type: ModelType,
        name: str = "",
    ) -> None:
        super().__init__(builder=builder, facet_type=facet_type, name=name)
        if "model_name" not in facet_type.facet_arguments:
            error_msg = "Facet type must be a model facet"
            raise ValueError(error_msg)

        # TODO: Add check that model_type is compatible with the facet type
        self.__model_type = model_type

    def hyperparameters(self, **hyperparameters: Any) -> Self:
        # If no hyperparameters are defined for this model type
        #   then raise an error
        if len(self.__model_type.hyperparameters) <= 0:
            facet_name = self._facet_type.name.title()
            error_msg = f"{facet_name} Facet does not support hyperparameters"
            raise RuntimeError(error_msg)

        # If hyperparameter groups are not required for this model type
        #   then just update facet arguments directly
        if not self.__model_type._hyperparameter_groups:
            self._update_arguments(hyperparameters=hyperparameters)
            return self

        # Hyperparameter groups are needed for this model type
        #   so group them accordingly
        hyperparameter_groups: ModelHyperParameterGroupType = defaultdict(dict)
        for hyperparameter_name, hyperparameter_value in hyperparameters.items():
            group = self.__model_type._hyperparameter_groups[hyperparameter_name]
            hyperparameter_group = hyperparameter_groups[group]
            hyperparameter_group[hyperparameter_name] = hyperparameter_value

        # Handle the facet spec arguments - Respect is_list from Facet Spec
        hyperparameter_as_arguments = {
            group_name: (
                [group_params]
                if self._facet_type.facet_arguments[group_name].is_list
                else group_params
            )
            for group_name, group_params in hyperparameter_groups.items()
        }
        self._update_arguments(**hyperparameter_as_arguments)
        return self

    def parameters(self, **parameters: Any) -> Self:
        if "parameters" not in self._facet_type.facet_arguments:
            facet_name = self._facet_type.name.title()
            error_msg = f"{facet_name} Facet does not support parameters"
            raise RuntimeError(error_msg)
        self._validate_parameters(**parameters)
        self._update_arguments(parameters=parameters)
        return self

    def _validate_hyperparameters(self, **hyperparameters: Any) -> None:
        # TODO: Implement hyperparameter validation
        ...

    def _validate_parameters(self, **parameters: Any) -> None:
        # TODO: Implement parameter validation
        ...


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
    _variables: dict[str, FlowVariable]

    def __init__(self) -> None:
        self._facets = []
        self._variables = {}

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

    def _add_variables(self, variables: dict[str, FlowVariable]) -> Self:
        self._variables = merge_dicts(self._variables, variables)
        return self

    def build(self) -> FlowDefinition:
        facets: list[Facet] = []
        arrows: list[Arrow] = []
        for idx, facet_builder in enumerate(self._facets):
            facet, in_arrows = facet_builder._build(facet_id=str(idx))
            facets.append(facet)
            arrows.extend(in_arrows)

        return FlowDefinition(
            facets=facets,
            arrows=arrows,
            variables=self._variables,
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
    variables: dict[str, FlowVariable] = Field(default_factory=dict)
    model_variables: dict = Field(default_factory=dict)

    def to_dict(self) -> FlowDefinitionDict:
        # TODO: Check if this is correct
        return cast(FlowDefinitionDict, self.model_dump(by_alias=True))
