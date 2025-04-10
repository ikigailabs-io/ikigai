# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Generic, Protocol, TypedDict, TypeVar

from ikigai.typing.protocol.directory import DirectoryDict
from ikigai.typing.protocol.generic import Empty


class ModelType(Protocol):
    @property
    def model_type(self) -> str: ...

    @property
    def sub_model_type(self) -> str: ...


class ModelDict(TypedDict):
    project_id: str
    model_id: str
    name: str
    latest_version_id: str
    directory: DirectoryDict
    model_type: str
    sub_model_type: str
    description: str
    created_at: str
    modified_at: str


class ModelVersionDict(TypedDict):
    version_id: str
    model_id: str
    version: str
    hyperparameters: dict
    metrics: dict
    created_at: str
    modified_at: str


# TODO: This needs to be reviewed by someone from the ML team
# that is familiar with the model spec.
class ModelSpecDict(TypedDict):
    name: str
    is_deprecated: bool
    is_hidden: bool
    keywords: list[str]
    metrics: ModelMetricsSpecDict
    sub_model_types: list[SubModelSpecDict]


class SubModelSpecDict(TypedDict):
    name: str
    is_deprecated: bool
    is_hidden: bool
    keywords: list[str]
    metrics: ModelMetricsSpecDict
    parameters: list[ModelParameterSpecDict]
    hyperparameters: list[ModelHyperparameterSpecDict]


ModelMetricsSpecDict = dict[str, Empty]

VT = TypeVar("VT")


class ModelParameterSpecDict(Generic[VT], TypedDict):
    name: str
    default_value: VT | None
    have_options: bool
    is_deprecated: bool
    is_hidden: bool
    is_list: bool
    options: list[VT]
    parameter_type: str


class ModelHyperparameterSpecDict(Generic[VT], TypedDict):
    name: str
    default_value: VT
    have_options: bool
    have_sub_hyperparameters: bool
    hyperparameter_group: str
    hyperparameter_type: str
    is_deprecated: bool
    is_hidden: bool
    is_list: bool
    children: list[dict]
    options: list[VT]
    sub_hyperparameter_requirements: list[list]
