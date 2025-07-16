# SPDX-FileCopyrightText: 2025-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from collections import ChainMap
from collections.abc import Generator, Mapping
from typing import Any

from pydantic import AliasPath, BaseModel, ConfigDict, Field, RootModel

from ikigai.typing.protocol import (
    FacetSpecsDict,
    ModelHyperparameterSpecDict,
    ModelSpecDict,
    SubModelSpecDict,
)
from ikigai.utils.compatibility import Self, override
from ikigai.utils.custom_validators import LowercaseStr
from ikigai.utils.helpful import Helpful

logger = logging.getLogger("ikigai.components.specs")


class FacetRequirementSpec(BaseModel):
    max_child_count: int
    min_child_count: int
    max_parent_count: int
    min_parent_count: int


class ArgumentSpec(BaseModel, Helpful):
    name: str
    argument_type: str
    default_value: Any | None = None
    children: dict[str, ArgumentSpec]
    have_sub_arguments: bool
    is_deprecated: bool
    is_hidden: bool
    is_list: bool
    is_required: bool
    options: list | None = None

    model_config = ConfigDict(frozen=True)

    @override
    def _help(self) -> Generator[str]:
        argument_type = (
            f"{self.argument_type}"
            if not self.is_list
            else f"list[{self.argument_type}]"
        )
        if self.is_required:
            argument_type += " | None"
        if not self.children:
            argument_value = f" = {self.default_value!r}" if self.default_value else ""
            yield f"{self.name}: {argument_type}{argument_value}" + (
                f"  options=[{'|'.join(self.options)}]" if self.options else ""
            )

        if self.children:
            start_brackets, end_brackets = ("[{", "}]") if self.is_list else ("{", "}")
            yield f"{self.name}: {argument_type} = " + start_brackets
            for child in self.children.values():
                if child.is_hidden:
                    continue
                yield from (f"  {child_help}" for child_help in child._help())
            yield end_brackets


class FacetType(BaseModel, Helpful):
    facet_uid: str = Field(validation_alias=AliasPath("facet_info", "facet_uid"))
    name: str = Field(validation_alias=AliasPath("facet_info", "facet_type"))
    is_deprecated: bool
    is_hidden: bool
    facet_requirement: FacetRequirementSpec
    facet_arguments: list[ArgumentSpec]
    in_arrow_arguments: list[ArgumentSpec]
    out_arrow_arguments: list[ArgumentSpec]

    model_config = ConfigDict(frozen=True)

    @override
    def _help(self) -> Generator[str]:
        # Facet name
        yield f"{self.name.title()}:"
        # Facet Arguments
        visible_facet_arguments = [
            argument for argument in self.facet_arguments if not argument.is_hidden
        ]
        if not visible_facet_arguments:
            yield "  No arguments"
            return

        if visible_facet_arguments:
            yield "  facet_arguments:"
            for argument in visible_facet_arguments:
                yield from (
                    f"    {argument_help}" for argument_help in argument._help()
                )

        # Arrow Arguments
        visible_in_arrow_arguments, out_arrow_arguments = (
            [
                argument
                for argument in self.in_arrow_arguments
                if not argument.is_hidden
            ],
            [
                argument
                for argument in self.out_arrow_arguments
                if not argument.is_hidden
            ],
        )

        # In Arrow Arguments
        if visible_in_arrow_arguments:
            yield "  in_arrow_arguments:"
            for argument in visible_in_arrow_arguments:
                yield from (
                    f"    {argument_help}" for argument_help in argument._help()
                )
        # Out Arrow Arguments
        if out_arrow_arguments:
            yield "  out_arrow_arguments:"
            for argument in out_arrow_arguments:
                yield from (
                    f"    {argument_help}" for argument_help in argument._help()
                )

    def check_arguments(self, arguments: dict) -> None:
        # TODO: Add facet spec checking here,
        #  right now we let platform inform the user on create/edit
        ...


class FacetTypes(BaseModel, Helpful):
    class ChainGroup(RootModel, Helpful):
        root: dict[LowercaseStr, FacetType]

        def __post_init__(self) -> None:
            self.root = {
                facet_type.lower().replace("_", "").replace(" ", ""): facet_spec
                for facet_type, facet_spec in self.root.items()
            }

        def __contains__(self, name: str) -> bool:
            key = name.lower().replace("_", "").replace(" ", "")
            return key in self.root

        def __getitem__(self, name: str) -> FacetType:
            if name not in self:
                error_msg = f"{name.title()} facet does not exist"
                raise AttributeError(error_msg)
            key = name.lower().replace("_", "").replace(" ", "")
            return self.root[key]

        def __getattr__(self, name: str) -> FacetType:
            return self[name]

        @property
        def types(self) -> list[str]:
            return [
                facet_type.name
                for facet_type in self.root.values()
                if not facet_type.is_hidden
            ]

        def __repr__(self) -> str:
            keys = list(self.root.keys())
            return f"ChainGroup({keys})"

        def __dir__(self) -> list[str]:
            # Default dir() will return the attributes of the class
            attributes = list(super().__dir__())

            # Add the keys from the chain group
            attributes.extend([key.upper() for key in self.root])
            return attributes

        @override
        def _help(self) -> Generator[str]:
            for facet_spec in self.root.values():
                yield from (f"  {facet_help}" for facet_help in facet_spec._help())

    INPUT: ChainGroup
    MID: ChainGroup
    OUTPUT: ChainGroup

    model_config = ConfigDict(frozen=True)

    @classmethod
    def from_dict(cls, data: FacetSpecsDict) -> Self:
        flattened_data = {
            "INPUT": ChainMap(*data["INPUT"].values()),
            "MID": ChainMap(*data["MID"].values()),
            "OUTPUT": ChainMap(*data["OUTPUT"].values()),
        }
        self = cls.model_validate(flattened_data)

        return self

    @override
    def _help(self) -> Generator[str]:
        # INPUT Chain
        yield "INPUT"
        yield from (f"  {chain_help}" for chain_help in self.INPUT._help())
        # MID Chain
        yield "MID"
        yield from (f"  {chain_help}" for chain_help in self.MID._help())
        # OUTPUT Chain
        yield "OUTPUT"
        yield from (f"  {chain_help}" for chain_help in self.OUTPUT._help())


class ModelMetricsSpec(RootModel, Helpful):
    root: dict[LowercaseStr, Any]

    def __post_init__(self) -> None:
        self.root = {metric.lower(): value for metric, value in self.root.items()}

    def __contains__(self, name: str) -> bool:
        return name.lower() in self.root

    def __getitem__(self, name: str) -> Any:
        if name not in self:
            error_msg = f"{name.title()} metric does not exist"
            raise AttributeError(error_msg)
        return self.root[name.lower()]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        self = cls.model_validate({key.lower(): value for key, value in data.items()})
        return self

    @override
    def _help(self) -> Generator[str]:
        yield "metrics:"
        if not self.root:
            yield "  No metrics"
            return

        for metric, value in self.root.items():
            yield f"  {metric}: {value}"


class ModelParameterSpec(BaseModel, Helpful):
    name: str
    default_value: Any | None = None
    have_options: bool
    is_deprecated: bool
    is_hidden: bool
    is_list: bool
    options: list | None = None
    parameter_type: str

    model_config = ConfigDict(frozen=True)

    @override
    def _help(self) -> Generator[str]:
        parameter_type = (
            f"{self.parameter_type}"
            if not self.is_list
            else f"list[{self.parameter_type}]"
        )
        parameter_value = (
            f" = {self.default_value!r}" if self.default_value is not None else ""
        ) + (
            f"  options=[{'|'.join([str(option) for option in self.options])}]"
            if self.options
            else ""
        )
        yield f"{self.name}: {parameter_type}{parameter_value}"


class ModelHyperparameterSpec(BaseModel, Helpful):
    name: str
    default_value: Any | None = None
    have_options: bool
    have_sub_hyperparameters: bool
    hyperparameter_group: str | None
    hyperparameter_type: str
    is_deprecated: bool
    is_hidden: bool
    is_list: bool
    children: dict[str, ModelHyperparameterSpec]
    options: list | None = None
    sub_hyperparameter_requirements: dict[Any, list[str]]

    model_config = ConfigDict(frozen=True)

    @classmethod
    def from_dict(cls, data: ModelHyperparameterSpecDict) -> Self:
        children = {
            name: ModelHyperparameterSpec.from_dict(child)
            for name, child in data["children"].items()
        }
        sub_hyperparameter_requirements = {
            requirement[0]: requirement[1]
            for requirement in data.get("sub_hyperparameter_requirements", [])
        }

        self = cls(
            name=data["name"],
            default_value=data.get("default_value"),
            have_options=data["have_options"],
            have_sub_hyperparameters=data["have_sub_hyperparameters"],
            hyperparameter_group=data.get("hyperparameter_group"),
            hyperparameter_type=data["hyperparameter_type"],
            is_deprecated=data["is_deprecated"],
            is_hidden=data["is_hidden"],
            is_list=data["is_list"],
            children=children,
            options=data.get("options"),
            sub_hyperparameter_requirements=sub_hyperparameter_requirements,
        )
        return self

    @override
    def _help(self) -> Generator[str]:
        hyperparameter_type = (
            f"{self.hyperparameter_type}"
            if not self.is_list
            else f"list[{self.hyperparameter_type}]"
        )
        hyperparameter_value = (
            f" = {self.default_value!r}" if self.default_value is not None else ""
        ) + (
            f"  options=[{'|'.join([str(option) for option in self.options])}]"
            if self.options
            else ""
        )
        if not self.children:
            yield f"{self.name}: {hyperparameter_type}{hyperparameter_value}"

        if self.children:
            yield f"{self.name}: {hyperparameter_type} = " "{"
            for child in self.children.values():
                if child.is_hidden:
                    continue
                yield from (f"  {child_help}" for child_help in child._help())
            yield "}"


class SubModelSpec(BaseModel, Helpful):
    name: str
    model_type: str
    is_deprecated: bool
    is_hidden: bool
    keywords: list[str]
    metrics: ModelMetricsSpec
    parameters: list[ModelParameterSpec]
    hyperparameters: list[ModelHyperparameterSpec]

    model_config = ConfigDict(frozen=True)

    @property
    def sub_model_type(self) -> str:
        return self.name

    @classmethod
    def from_dict(cls, model_type: str, data: SubModelSpecDict) -> Self:
        data_dict = {
            **data,
            "parameters": list(data["parameters"].values()),
            "hyperparameters": [
                ModelHyperparameterSpec.from_dict(hyperparameter_dict)
                for hyperparameter_dict in data["hyperparameters"].values()
            ],
            "model_type": model_type,
        }
        self = cls.model_validate(data_dict)
        return self

    @override
    def _help(self) -> Generator[str]:
        # Sub-model name
        yield f"{self.name.title()}:"
        if self.keywords:
            yield f"  keywords: {self.keywords}"

        yield from (f"  {metric_spec}" for metric_spec in self.metrics._help())

        # Parameters and Hyperparameters
        visible_parameters = [
            parameter for parameter in self.parameters if not parameter.is_hidden
        ]
        visible_hyperparameters = [
            hyperparameter
            for hyperparameter in self.hyperparameters
            if not hyperparameter.is_hidden
        ]
        yield "  parameters:"
        if visible_parameters:
            for parameter in visible_parameters:
                yield from (
                    f"    {parameter_spec}" for parameter_spec in parameter._help()
                )
        else:
            yield "    No parameters"

        yield "  hyperparameters:"
        if visible_hyperparameters:
            for hyperparameter in visible_hyperparameters:
                yield from (
                    f"    {hyperparameter_spec}"
                    for hyperparameter_spec in hyperparameter._help()
                )
        else:
            yield "    No hyperparameters"


class ModelSpec(BaseModel, Helpful):
    name: str
    is_deprecated: bool
    is_hidden: bool
    keywords: list[str]
    sub_model_types: dict[str, SubModelSpec]

    model_config = ConfigDict(frozen=True)

    @property
    def model_type(self) -> str:
        return self.name

    @classmethod
    def from_dict(cls, data: ModelSpecDict) -> Self:
        logger.debug("Creating a %s from %s", cls.__name__, data)
        self = cls(
            name=data["name"],
            is_deprecated=data["is_deprecated"],
            is_hidden=data["is_hidden"],
            keywords=data["keywords"],
            sub_model_types={
                (
                    sub_model_spec["name"].lower().replace("_", "").replace(" ", "")
                ): SubModelSpec.from_dict(model_type=data["name"], data=sub_model_spec)
                for sub_model_spec in data["sub_model_types"]
            },
        )
        return self

    def __contains__(self, sub_model_type: str) -> bool:
        key = sub_model_type.lower().replace("_", "").replace(" ", "")
        return key in self.sub_model_types

    def __getitem__(self, sub_model_type: str) -> SubModelSpec:
        if sub_model_type not in self:
            error_msg = f"{sub_model_type.title()} sub-model does not exist"
            raise AttributeError(error_msg)
        key = sub_model_type.lower().replace("_", "").replace(" ", "")
        return self.sub_model_types[key]

    def __getattr__(self, sub_model_type: str) -> SubModelSpec:
        return self[sub_model_type]

    @property
    def types(self) -> list[str]:
        return [
            sub_model_spec.name
            for sub_model_spec in self.sub_model_types.values()
            if not sub_model_spec.is_hidden
        ]

    @override
    def _help(self) -> Generator[str]:
        # Model name
        yield f"{self.name.title()}:"
        if self.keywords:
            yield f"  keywords: {self.keywords}"

        # Sub-model types
        visible_sub_model_types = [
            sub_model_spec
            for sub_model_spec in self.sub_model_types.values()
            if not sub_model_spec.is_hidden
        ]
        if not visible_sub_model_types:
            return

        yield "  sub-model types:"
        for sub_model_spec in visible_sub_model_types:
            yield from (
                f"    {sub_model_spec}" for sub_model_spec in sub_model_spec._help()
            )


class ModelTypes(RootModel, Helpful):
    root: dict[LowercaseStr, ModelSpec]

    @classmethod
    def from_list(cls, data: list[ModelSpecDict]) -> Self:
        data_dict = {model_spec["name"]: model_spec for model_spec in data}
        return cls.from_dict(data_dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Self:
        self = cls(
            {
                model_name.lower()
                .replace("_", "")
                .replace(" ", ""): ModelSpec.from_dict(model_spec)
                for model_name, model_spec in data.items()
            }
        )
        return self

    def __len__(self) -> int:
        return len(self.root)

    def __contains__(self, name: str) -> bool:
        return name.lower().replace("_", "").replace(" ", "") in self.root

    def __getitem__(self, name: str) -> ModelSpec:
        if name not in self:
            error_msg = f"{name.title()} model does not exist"
            raise AttributeError(error_msg)
        key = name.lower().replace("_", "").replace(" ", "")
        return self.root[key]

    def __getattr__(self, name: str) -> ModelSpec:
        return self[name]

    @property
    def types(self) -> list[str]:
        return [model.name for model in self.root.values() if not model.is_hidden]

    @override
    def _help(self) -> Generator[str]:
        for model_spec in self.root.values():
            if model_spec.is_hidden:
                continue
            yield from model_spec._help()
