# SPDX-FileCopyrightText: 2026-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from collections.abc import Generator, Mapping
from functools import cached_property
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator,
    model_validator,
)

from ikigai.typing.protocol import (
    HyperParameterGroupName,
    HyperParameterName,
    ModelSpecDict,
    SubModelSpecDict,
)
from ikigai.utils.compatibility import Self, override
from ikigai.utils.custom_validators import LowercaseStr
from ikigai.utils.enums import (
    ModelHyperparameterType,
    ModelParameterType,
)
from ikigai.utils.helpful import Helpful
from ikigai.utils.missing import MISSING, MissingType

logger = logging.getLogger("ikigai.components.specs")


class ModelMetricsSpec(RootModel, Helpful):
    root: dict[LowercaseStr, Any]

    @model_validator(mode="after")
    def validate_lowercase_keys(self) -> Self:
        self.root = {metric.lower(): value for metric, value in self.root.items()}
        return self

    def __contains__(self, name: str) -> bool:
        return name.lower() in self.root

    def __getitem__(self, name: str) -> Any:
        if name not in self:
            error_msg = f"{name.title()} metric does not exist"
            raise AttributeError(error_msg)
        return self.root[name.lower()]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls.model_validate({key.lower(): value for key, value in data.items()})

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

    def __validation_error_message(
        self, model: str, expectation: str, actuals: MissingType | Any = MISSING
    ) -> str:
        if actuals is MISSING:
            actuals_str = ""
        elif actuals is None:
            actuals_str = ", got 'None'"
        elif isinstance(actuals, type):
            actuals_str = f", got type '{actuals.__name__}'"
        else:
            actuals_str = f", got {actuals.__class__.__name__}({actuals!r})"

        return f"Parameter '{self.name}' for {model} {expectation}{actuals_str}"

    def validate_value(self, model: str, value: Any) -> None:
        if self.is_list:
            return self.__validate_list_value(model, value)

        # Not a list or dict, so it must be a scalar value
        return self.__validate_scalar_value(model, value)

    def __validate_list_value(self, model: str, value: Any) -> None:
        if not isinstance(value, list):
            error_msg = self.__validation_error_message(model, "must be list", value)
            raise TypeError(error_msg)

        scalar_parameter_spec = self.model_copy(update={"is_list": False})
        for item in value:
            scalar_parameter_spec.validate_value(model, item)
        return None  # All items validated

    def __validate_scalar_value(self, model: str, value: Any) -> None:
        if self.options and value not in self.options:
            error_msg = self.__validation_error_message(
                model, "must be one of {self.options}", value
            )
            raise ValueError(error_msg)

        if self.parameter_type == ModelParameterType.BOOLEAN and not isinstance(
            value, bool
        ):
            error_msg = self.__validation_error_message(model, "must be boolean", value)
            raise TypeError(error_msg)

        if self.parameter_type == ModelParameterType.TEXT and not isinstance(
            value, str
        ):
            error_msg = self.__validation_error_message(model, "must be string", value)
            raise TypeError(error_msg)

        if self.parameter_type == ModelParameterType.NUMBER and not isinstance(
            value, int | float
        ):
            error_msg = self.__validation_error_message(model, "must be numeric", value)
            raise TypeError(error_msg)

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
    hyperparameter_type: ModelHyperparameterType
    is_deprecated: bool
    is_hidden: bool
    is_list: bool
    children: dict[str, ModelHyperparameterSpec]
    options: list | None = None
    sub_hyperparameter_requirements: dict[Any, list[str]] = Field(default_factory=dict)

    model_config = ConfigDict(frozen=True)

    @field_validator("sub_hyperparameter_requirements", mode="before")
    @classmethod
    def validate_sub_hyperparameter_requirements(cls, v: Any) -> dict[Any, list[str]]:
        if isinstance(v, list):
            if not (
                all(
                    isinstance(item, tuple | list) and len(item) == 2  # noqa: PLR2004 -- 2 is a fairly reasonable literal len
                    for item in v
                )
            ):
                error_msg = (
                    "Expected a list of "
                    "(hyperparameter_value, [required_hyperparameter_names]) tuples"
                )
                raise ValueError(error_msg)
            return dict(v)

        if isinstance(v, dict):
            return v

        error_msg = "Expected a dictionary or list of requirements"
        raise ValueError(error_msg)

    def __validation_error_message(
        self, model: str, expectation: str, actuals: MissingType | Any = MISSING
    ) -> str:
        if actuals is MISSING:
            actuals_str = ""
        elif actuals is None:
            actuals_str = ", got 'None'"
        elif isinstance(actuals, type):
            actuals_str = f", got type '{actuals.__name__}'"
        else:
            actuals_str = f", got {actuals.__class__.__name__}({actuals!r})"

        return f"Hyperparameter '{self.name}' for {model} {expectation}{actuals_str}"

    def validate_value(self, model: str, value: Any) -> None:
        if self.is_list:
            return self.__validate_list_value(model, value)

        if self.hyperparameter_type == ModelHyperparameterType.MAP:
            return self.__validate_dict_value(model, value)

        # Not a list or dict, so it must be a scalar value
        return self.__validate_scalar_value(model, value)

    def __validate_list_value(self, model: str, value: Any) -> None:
        if not isinstance(value, list):
            error_msg = self.__validation_error_message(model, "must be list", value)
            raise TypeError(error_msg)

        scalar_hyperparameter_spec = self.model_copy(update={"is_list": False})
        for item in value:
            scalar_hyperparameter_spec.validate_value(model, item)
        return None  # All items validated

    def __validate_dict_value(self, model: str, value: Any) -> None:
        if not isinstance(value, Mapping):
            error_msg = self.__validation_error_message(model, "must be mapping", value)
            raise TypeError(error_msg)

        for name, child_value in value.items():
            if name not in self.children:
                error_msg = self.__validation_error_message(
                    model, f"provided with unexpected child hyperparameter '{name}'"
                )
                raise KeyError(error_msg)
            child_spec = self.children[name]
            child_spec.validate_value(model, child_value)
        return None  # All child hyperparameters validated

    def __validate_scalar_value(self, model: str, value: Any) -> None:
        if self.options and value not in self.options:
            error_msg = self.__validation_error_message(
                model, f"must be one of {self.options}", value
            )
            raise ValueError(error_msg)

        if (
            self.hyperparameter_type == ModelHyperparameterType.BOOLEAN
            and not isinstance(value, bool)
        ):
            error_msg = self.__validation_error_message(model, "must be boolean", value)
            raise TypeError(error_msg)

        if self.hyperparameter_type == ModelHyperparameterType.TEXT and not isinstance(
            value, str
        ):
            error_msg = self.__validation_error_message(model, "must be string", value)
            raise TypeError(error_msg)

        if (
            self.hyperparameter_type == ModelHyperparameterType.NUMBER
            and not isinstance(value, int | float)
        ):
            error_msg = self.__validation_error_message(model, "must be numeric", value)
            raise TypeError(error_msg)

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
            yield f"{self.name}: {hyperparameter_type} = {{"
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
    parameters: dict[str, ModelParameterSpec]
    hyperparameters: dict[str, ModelHyperparameterSpec]

    model_config = ConfigDict(frozen=True)

    @field_validator("parameters", mode="after")
    @classmethod
    def validate_parameters(
        cls, v: dict[str, ModelParameterSpec]
    ) -> dict[str, ModelParameterSpec]:
        return {parameter.name: parameter for parameter in v.values()}

    @field_validator("hyperparameters", mode="after")
    @classmethod
    def validate_hyperparameters(
        cls, v: dict[str, ModelHyperparameterSpec]
    ) -> dict[str, ModelHyperparameterSpec]:
        # If one hyperparameter has a group, then all hyperparameters must have groups
        has_any_groups = any(
            hyperparameter.hyperparameter_group is not None
            for hyperparameter in v.values()
        )
        has_all_groups = all(
            hyperparameter.hyperparameter_group is not None
            for hyperparameter in v.values()
        )

        if has_any_groups and not has_all_groups:
            message = (
                "Inconsistent hyperparameter groups for: "
                "Some hyperparameters have groups while others do not.\n"
                "This is likely a due to a bug in the model specification."
            )
            logger.error(message, extra={"hyperparameter specification": v})
            raise ValueError(message)
        return {hyperparameter.name: hyperparameter for hyperparameter in v.values()}

    @property
    def sub_model_type(self) -> str:
        return self.name

    @classmethod
    def from_dict(cls, model_type: str, data: SubModelSpecDict) -> Self:
        data_dict = {
            **data,
            "model_type": model_type,
        }

        return cls.model_validate(data_dict)

    @cached_property
    def _hyperparameter_groups(
        self,
    ) -> dict[HyperParameterName, HyperParameterGroupName]:
        # Create a mapping from hyperparameter name to its group
        return {
            hyperparameter.name: hyperparameter.hyperparameter_group
            for hyperparameter in self.hyperparameters.values()
            if hyperparameter.hyperparameter_group
        }

    @override
    def _help(self) -> Generator[str]:
        # Sub-model name
        yield f"{self.name.title()}:"
        if self.keywords:
            yield f"  keywords: {self.keywords}"

        yield from (f"  {metric_spec}" for metric_spec in self.metrics._help())

        # Parameters and Hyperparameters
        visible_parameters = [
            parameter
            for parameter in self.parameters.values()
            if not parameter.is_hidden
        ]
        visible_hyperparameters = [
            hyperparameter
            for hyperparameter in self.hyperparameters.values()
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

        return self  # noqa: RET504 -- seperating construction and return for clarity

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
        return cls(
            {
                model_name.lower()
                .replace("_", "")
                .replace(" ", ""): ModelSpec.from_dict(model_spec)
                for model_name, model_spec in data.items()
            }
        )

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
