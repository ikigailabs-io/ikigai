# SPDX-FileCopyrightText: 2025-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, cast

from pydantic import BaseModel, ConfigDict, Field

from ikigai.client import datax
from ikigai.components.custom_facet import CustomFacetVersion
from ikigai.specs import CustomFacetType, FacetType
from ikigai.specs import SubModelSpec as ModelType
from ikigai.utils import FacetArgumentType
from ikigai.utils.compatibility import Self, override
from ikigai.utils.data_structures import merge_dicts

logger = logging.getLogger("ikigai.components")


class FlowVariable(BaseModel):
    """
    A mapping from a flow variable to a specific argument on a facet.

    Attributes
    ----------

    facet_name: str
        Name of the facet the variable is associated with.

    argument_name: str
        Name of the argument within the facet that the variable targets.
    """
    facet_name: str
    argument_name: str = Field(serialization_alias="name")

    model_config = ConfigDict(frozen=True)


class FacetBuilder:
    """
    Builder for constructing a facet.

    Provides a way to configure facet arguments, variables, and arrow
    connections to other facets.
    """
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
        """
        Create a new facet and connect it to this facet.

        Parameters
        ----------

        facet_type: FacetType
            Type of the new facet.

        name: str
            Name of the new facet.

        args : dict[str, Any] or None
            Arguments for the new facet.

        arrow_args : dict[str, Any]
            Arguments for the connecting arrow between facets. The available
            options depend on the facet type.

        Returns
        -------

        FacetBuilder
            Builder for the new facet.

        Examples
        --------
        >>> flow_builder = ikigai.builder
        >>>
        >>> facet_1 = (
        ...         flow_builder.facet(
        ...             facet_type=facet_types.INPUT.Imported
        ...         ).arguments(
        ...             dataset_id="my-input-dataset-id",
        ...             file_type="csv",
        ...             header=True,
        ...             use_raw_file=False,
        ...         )
        ... )
        >>>
        >>> facet_2 = (
        ...         facet_1.facet(
        ...             # Adds a COUNT facet attached to the imported facet.
        ...             facet_type=facet_types.MID.COUNT
        ...         ).arguments(
        ...             output_column_name="count",
        ...             sort=True,
        ...             target_columns=["col1", "col2"],
        ...         )
        ... )
        """
        if arrow_args is None:
            arrow_args = {}

        return self._builder.facet(
            facet_type=facet_type, name=name, args=args
        ).add_arrow(self, **arrow_args)

    def custom_facet(
        self,
        custom_facet_version: CustomFacetVersion,
        name: str = "",
        args: dict[str, Any] | None = None,
        arrow_args: dict[str, Any] | None = None,
    ) -> CustomFacetFacetBuilder:
        """
        Create a custom facet and connect it to this facet.

        Parameters
        ----------

        custom_facet_version: CustomFacetVersion
            Version of the custom facet.

        name: str, optional
            Name of the facet.

        args: dict[str, Any], optional
            Initial arguments.

        arrow_args: dict[str, Any], optional
            Arguments for the connecting arrow between facets. The available
            options depend on the facet type.

        Returns
        -------

        CustomFacetFacetBuilder
            Builder for the custom facet.
        """
        if arrow_args is None:
            arrow_args = {}

        return self._builder.custom_facet(
            custom_facet_version=custom_facet_version, name=name, args=args
        ).add_arrow(self, **arrow_args)

    def model_facet(
        self,
        facet_type: FacetType,
        model_type: ModelType,
        name: str = "",
        args: dict[str, Any] | None = None,
        arrow_args: dict[str, Any] | None = None,
    ) -> ModelFacetBuilder:
        """
        Create a model facet and connect it to this facet.

        Parameters
        ----------

        facet_type: FacetType
            Model facet type.

        model_type: ModelType
            Model type. Use ``model_types.types`` to view all available Ikigai
            model types.

        name: str
            Name of the facet.

        args: dict[str, Any]
            Initial model arguments.

        arrow_args: dict[str, Any]
            Arguments for the connecting arrow between facets. The available
            options depend on the facet type.

        Returns
        -------

        ModelFacetBuilder
            Builder for the model facet.
        """
        if arrow_args is None:
            arrow_args = {}

        return self._builder.model_facet(
            facet_type=facet_type, model_type=model_type, name=name, args=args
        ).add_arrow(self, **arrow_args)

    def arguments(self, **arguments: Any) -> Self:
        """
        Set or update facet arguments.

        Parameters
        ----------

        **arguments: dict
            Key-value pairs representing facet arguments.

        Returns
        -------

        Self
            Updated builder instance.

        Raises
        ------

        ValueError
            If an argument is invalid or fails validation.
        """
        self._validate_arguments(**arguments)
        return self._update_arguments(**arguments)

    def variables(self, **variables: str) -> Self:
        """
        Attach flow variables to this facet's arguments.

        To target an argument with a variable, the facet must have a name.

        Parameters
        ----------

        **variables: str
            Keyword arguments where each key is the variable name and each value
            is the name of the facet argument it targets.

        Returns
        -------
        Self
            The current FacetBuilder object.

        Raises
        ------
        RuntimeError
            If the facet has already been built.

        ValueError
            If the facet does not have a name.

        ValueError
            If any specified arguments do not exist on the facet.

        ValueError
            If any of the arguments are of type ``MAP`` or ``LIST``, which are
            not currently supported by the Ikigai platform.

        Examples
        --------

        # Add a variable called 'dataset' targeting the dataset_id argument
        >>> IMPORTED = facet_types.INPUT.IMPORTED
        >>> builder = ikigai.builder
        >>> builder.facet(facet_type=IMPORTED, name="input").variables(
        ...     dataset="dataset_id",
        ... )

        # Add a variable called 'dataset' targeting the dataset_name argument
        >>> EXPORTED = facet_types.OUTPUT.EXPORTED
        >>> builder = ikigai.builder
        >>> builder.facet(facet_type=EXPORTED, name="output").variables(
        ...     dataset="dataset_name",
        ... )
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
            if (
                argument_spec.argument_type is FacetArgumentType.MAP
                or argument_spec.is_list
            ):
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
        """
        Add a connection arrow from another facet.

        Parameters
        ----------

        parent: FacetBuilder
            Source facet builder.

        **args: dict
            Configuration arguments for the arrow connection. The available
            options depend on the facet types involved.

        Returns
        -------

        Self
            Updated builder instance.

        Examples
        --------

        >>> flow_builder = ikigai.builder
        >>>
        >>> import_1 = (
        ...         flow_builder.facet(
        ...             facet_type=facet_types.INPUT.Imported
        ...         ).arguments(
        ...             dataset_id="my-input-dataset-id",
        ...             file_type="csv",
        ...             header=True,
        ...             use_raw_file=False,
        ...         )
        ... )  # The first import facet
        >>>
        >>> import_2 = (
        ...         import_1.facet(
        ...             facet_type=facet_types.INPUT.Imported
        ...         ).arguments(
        ...             dataset_id="my-input-dataset-id-2",
        ...             file_type="csv",
        ...             header=True,
        ...             use_raw_file=False,
        ...         )
        ... )  # The second import facet
        >>>
        >>> union_facet = (
        ...         flow_builder.facet(
        ...             facet_type=facet_types.MID.UNION,
        ...             name="union",
        ...         )
        ...         .add_arrow(
        ...             import_1,
        ...             table_side="top",
        ...         )
        ...         .add_arrow(
        ...             import_2,
        ...             table_side="bottom",
        ...         )
        ...         .arguments(
        ...             option="full",
        ...         )
        ... )
        """
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

    def _build_arguments(self) -> dict[str, Any]:
        return self._arguments

    def _build(self, facet_id: str) -> tuple[Facet, list[Arrow]]:
        if self.__facet is not None:
            if self.__arrows is None:
                error_msg = (
                    "Facet built but arrows missing, this should not happen. "
                    "Please report a bug."
                )
                raise RuntimeError(error_msg)
            return self.__facet, self.__arrows

        self.__facet = Facet(
            facet_id=facet_id,
            facet_uid=self._facet_type.facet_uid,
            name=self.__name,
            arguments=self._build_arguments(),
        )

        self.__arrows = [
            arrow_builder._build() for arrow_builder in self.__arrow_builders
        ]
        return self.__facet, self.__arrows

    def build(self) -> FlowDefinition:
        """
        Build the flow definition using the configurations.

        Returns
        -------

        FlowDefinition
            The created flow definition.
        """

        flow_definition = self._builder.build()
        logger.debug("Built flow definition: %s", flow_definition.to_dict())
        return flow_definition


class CustomFacetFacetBuilder(FacetBuilder):
    """
    Builder for custom facets.

    Supports both standard facet arguments and custom-defined arguments.
    """
    __custom_facet_type: CustomFacetType
    _custom_facet_arguments: dict[str, Any]

    def __init__(
        self,
        builder: FlowDefinitionBuilder,
        custom_facet_version: CustomFacetVersion,
        name: str = "",
    ) -> None:
        if custom_facet_version.version_id == "":
            logger.warning(
                "Creating an unpinned custom facet, the flow may fail to run if the "
                "custom facet script's input/output format or arguments change. Prefer "
                "using a pinned version instead."
            )

        super().__init__(
            builder=builder, facet_type=custom_facet_version.facet_type, name=name
        )
        self.__custom_facet_type = custom_facet_version.facet_type
        self._custom_facet_arguments = {}
        super().arguments(
            custom_facet_id=custom_facet_version.custom_facet_id,
            version_id=custom_facet_version.version_id,
        )

    @override
    def arguments(self, **arguments: Any) -> Self:
        """
        Set arguments for both standard and custom facet parameters.

        Parameters
        ----------

        **arguments: Any
            Argument values.

        Returns
        -------
        Self
            Updated builder instance.

        Raises
        ------
        ValueError
            If any argument is invalid.
        """
        # if the argument is present in the facet spec, then try to add it directly.
        facet_arguments = {
            name: value
            for name, value in arguments.items()
            if name in self._facet_type.facet_arguments and name != "arguments"
        }
        # if the argument is not present in the facet spec,
        #   then consider it as a custom facet argument.
        custom_arguments = {
            name: value
            for name, value in arguments.items()
            if name not in self._facet_type.facet_arguments
        }

        # Add the facet arguments to the facet using the parent class
        super().arguments(**facet_arguments)

        # Validate the custom facet arguments and update the custom facet arguments
        self._validate_custom_arguments(**custom_arguments)
        return self._update_custom_arguments(**custom_arguments)

    def _validate_custom_arguments(self, **custom_arguments: Any) -> None:
        facet_name = self._facet_type.name.title()
        for arg_name, arg_value in custom_arguments.items():
            if arg_name not in self.__custom_facet_type.custom_facet_arguments:
                error_msg = f"Argument '{arg_name}' is not valid for {facet_name} facet"
                raise ValueError(error_msg)

            # Argument is present in custom facet spec, validate it
            arg_spec = self.__custom_facet_type.custom_facet_arguments[arg_name]
            arg_spec.validate_value(facet=facet_name, value=arg_value)

    def _update_custom_arguments(self, **custom_arguments: Any) -> Self:
        self._custom_facet_arguments = merge_dicts(
            self._custom_facet_arguments, custom_arguments
        )
        return self

    @override
    def _build_arguments(self) -> dict[str, Any]:
        custom_facet_arguments = [
            {
                "name": name,
                "value": value,
                "type": (
                    self.__custom_facet_type.custom_facet_arguments[
                        name
                    ].argument_type.value
                ),
            }
            for name, value in self._custom_facet_arguments.items()
        ]

        return {
            **(self._arguments),
            "arguments": custom_facet_arguments,
        }


class ModelFacetBuilder(FacetBuilder):
    """
    Builder for model facets.

    Configure hyperparameters and parameters according to the model
    specification.

    Examples
    --------

    >>> model_facet = (
    ...     facet_1.model_facet(
    ...         facet_type=facet_types.MID.PREDICT,
    ...         model_type=model_types.Linear.Lasso,
    ...     )
    ...     .arguments(
    ...         # Refer to the facet type help for list of arguments
    ...         model_name="my-model-name",  # Name of existing model in the app
    ...         model_version="initial",     # Model version to use or train
    ...     )
    ...     .hyperparameters(
    ...         # Refer to the model type help for list of hyperparameters
    ...         alpha=0.1,
    ...         fit_intercept=True,
    ...     )
    ...     .parameters(
    ...         # Refer to the model type help for list of model parameters
    ...         target_column="target_column_name",
    ...     )
    ... )
    """
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
        """
        Set the model hyperparameters.

        Parameters
        ----------

        **hyperparameters: Any
            Hyperparameter values.

        Returns
        -------

        Self
            Updated builder.

        Raises
        ------

        ValueError
            If a hyperparameter is invalid.

        RuntimeError
            If the model does not support hyperparameters.
        """
        # Validate the hyperparameters
        self._validate_hyperparameters(**hyperparameters)

        # If hyperparameter groups are not required for this model type
        #   then just update facet arguments directly
        if not self.__model_type._hyperparameter_groups:
            self._update_arguments(hyperparameters=hyperparameters)
            return self

        # Hyperparameter groups are needed for this model type
        #   so group them accordingly
        hyperparameter_groups: datax.ModelHyperParameterGroupType = defaultdict(dict)
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
        """
        Set model parameters.

        Parameters
        ----------

        **parameters: Any
            Parameter values.

        Returns
        -------

        Self
            Updated builder.

        Raises
        ------

        ValueError
            If a parameter is invalid.
        """
        self._validate_parameters(**parameters)
        self._update_arguments(parameters=parameters)
        return self

    def _validate_hyperparameters(self, **hyperparameters: Any) -> None:
        model_name = self.__model_type.name.title()
        # If no hyperparameters are defined for this model type
        #   then raise an error
        if len(self.__model_type.hyperparameters) <= 0:
            error_msg = f"{model_name} Model does not support hyperparameters"
            raise RuntimeError(error_msg)

        for hyperparameter_name, hyperparameter_value in hyperparameters.items():
            # Validate if hyperparameter is in model spec
            if hyperparameter_name not in self.__model_type.hyperparameters:
                error_msg = (
                    f"Hyperparameter '{hyperparameter_name}' is not valid for "
                    f"{model_name} models"
                )
                raise ValueError(error_msg)

            # Hyperparameter is in model spec, validate it
            hyperparameter_spec = self.__model_type.hyperparameters[hyperparameter_name]
            hyperparameter_spec.validate_value(
                model=model_name, value=hyperparameter_value
            )

    def _validate_parameters(self, **parameters: Any) -> None:
        model_name = self.__model_type.name.title()
        if "parameters" not in self._facet_type.facet_arguments:
            error_msg = f"{model_name} Model does not support parameters"
            raise RuntimeError(error_msg)

        for parameter_name, parameter_value in parameters.items():
            # Validate if parameter is in model spec
            if parameter_name not in self.__model_type.parameters:
                error_msg = (
                    f"Parameter '{parameter_name}' is not valid for {model_name} models"
                )
                raise ValueError(error_msg)

            # Parameter is in model spec, validate it
            parameter_spec = self.__model_type.parameters[parameter_name]
            parameter_spec.validate_value(model=model_name, value=parameter_value)


class ArrowBuilder:
    """
    Builder for creating arrow connections between facets.

    Attributes
    ----------

    source: FacetBuilder
        The source facet of the arrow connection.

    destination: FacetBuilder
        The destination facet of the arrow connection.

    arguments: dict[str, Any]
        Arguments that control the behavior of the arrow connection.
    """
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
    """
    Builder for creating a flow definition.

    The flow definition is used to add and configure facets, including
    custom and model facets. Once you have created a flow definition, you can
    build the definition using the FlowBuilder class.

    At a high-level, the process for creating a flow definition is the
    following:

    - Create a new instance of the FlowBuilder class.
    - Add facets to the instance of the FlowBuilder class.
    - Configure the facets.
    - Build the flow definition.
    """
    _facets: list[FacetBuilder]
    _variables: dict[str, FlowVariable]

    def __init__(self) -> None:
        self._facets = []
        self._variables = {}

    def facet(
        self, facet_type: FacetType, name: str = "", args: dict[str, Any] | None = None
    ) -> FacetBuilder:
        """
        Add a facet to the flow definition.

        Parameters
        ----------

        facet_type: FacetType
            The facet type to add.

        name: str
            Name of the facet.

        args: dict[str, Any] or None
            Arguments to initialize the facet with.

        Returns
        -------

        FacetBuilder
            Builder for the facet.
        """
        if args is None:
            args = {}
        facet_builder = FacetBuilder(
            builder=self, facet_type=facet_type, name=name
        ).arguments(**args)
        self._facets.append(facet_builder)
        return facet_builder

    def custom_facet(
        self,
        custom_facet_version: CustomFacetVersion,
        name: str = "",
        args: dict[str, Any] | None = None,
    ) -> CustomFacetFacetBuilder:
        """
        Add a custom facet to the flow definition.

        Parameters
        ----------

        custom_facet_version: CustomFacetVersion
            The custom facet version to use.

        name: str
            Name of the custom facet.

        args: dict[str, Any] or None
            Arguments to initialize the custom facet with.

        Returns
        -------

        CustomFacetFacetBuilder
            Builder for the created custom facet.
        """
        if args is None:
            args = {}
        custom_facet_builder = CustomFacetFacetBuilder(
            builder=self, custom_facet_version=custom_facet_version, name=name
        ).arguments(**args)
        self._facets.append(custom_facet_builder)
        return custom_facet_builder

    def model_facet(
        self,
        facet_type: FacetType,
        model_type: ModelType,
        name: str = "",
        args: dict[str, Any] | None = None,
    ) -> ModelFacetBuilder:
        """
        Add a model facet to the flow definition.

        Parameters
        ----------

        facet_type: FacetType
            The facet type to add.

        model_type: ModelType
            The model type to add.

        name: str
            Name of the model facet.

        args: dict[str, Any] or None
            Arguments to initialize the model facet with.

        Returns
        -------

        ModelFacetBuilder
            Builder for the created model facet.

        Raises
        ------

        ValueError
            If ``facet_type`` is not a valid facet type.
        """
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
        """
        Build the flow definition using the configured facets.

        Returns
        -------

        FlowDefinition
            The constructed flow definition.
        """
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
    """
    A facet on the Ikigai platform.

    Attributes
    ----------

    facet_id: str
        Unique identifier of the facet.

    facet_uid: str
        Globally unique identifier for the facet.

    name: str
        Name of the facet.

    arguments: dict[str, Any]
        Arguments for the facet.
    """
    facet_id: str
    facet_uid: str
    name: str = ""
    arguments: dict[str, Any]


class Arrow(BaseModel):
    """
    An arrow connection between two facets.

    Attributes
    ----------

    source: str
       The source facet.

    destination: str
        The destination facet.

    arguments: dict[str, Any]
        Configuration arguments for the arrow connection.
    """
    source: str
    destination: str
    arguments: dict[str, Any]


class FlowDefinition(BaseModel):
    """
    A flow definition.

    Attributes
    ----------

    facets: list[Facet]
        List of facets that make up the flow definition.

    arrows: list[Arrow]
        List of arrow connections between facets.

    variables: dict[str, FlowVariable]
        Variables associated with the facet.

    model_variables: dict
        Variables associated with model facets.
    """
    facets: list[Facet] = Field(default_factory=list)
    arrows: list[Arrow] = Field(default_factory=list)
    variables: dict[str, FlowVariable] = Field(default_factory=dict)
    model_variables: dict = Field(default_factory=dict)

    def to_dict(self) -> datax.FlowDefinitionDict:
        # TODO: Check if this is correct
        return cast(datax.FlowDefinitionDict, self.model_dump(by_alias=True))
