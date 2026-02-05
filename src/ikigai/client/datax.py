# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypedDict

from ikigai.typing.protocol import DirectoryDict
from ikigai.utils.compatibility import NotRequired
from ikigai.utils.enums import DatasetDownloadStatus

# -------------------------------------------------------------------------------------
# App Related Data Exchange Types


class AppDict(TypedDict):
    project_id: str
    name: str
    owner: str
    description: str
    icon: str
    images: list[str]
    directory: DirectoryDict
    created_at: str
    modified_at: str
    last_used_at: str


class GetComponentsForProjectResponse(TypedDict):
    charts: list[Mapping[str, Any]]
    connectors: list[Mapping[str, Any]]
    dashboards: list[Mapping[str, Any]]
    datasets: list[Mapping[str, Any]]
    databases: list[Mapping[str, Any]]
    pipelines: list[Mapping[str, Any]]
    models: list[Mapping[str, Any]]
    external_resources: list[Mapping[str, Any]]
    users: list[Mapping[str, Any]]
    connector_directories: list[Mapping[str, Any]]
    dashboard_directories: list[Mapping[str, Any]]
    dataset_directories: list[Mapping[str, Any]]
    database_directories: list[Mapping[str, Any]]
    pipeline_directories: list[Mapping[str, Any]]
    model_directories: list[Mapping[str, Any]]
    external_resource_directories: list[Mapping[str, Any]]


# -------------------------------------------------------------------------------------
# Dataset Related Data Exchange Types


class GetDatasetMultipartUploadUrlsResponse(TypedDict):
    upload_id: str
    content_type: str
    urls: dict[int, str]


class _InitializeDatasetDownloadFailedResponse(TypedDict):
    status: Literal[DatasetDownloadStatus.FAILED]


class _InitializeDatasetDownloadInProgressResponse(TypedDict):
    status: Literal[DatasetDownloadStatus.IN_PROGRESS]


class _InitializeDatasetDownloadSuccessResponse(TypedDict):
    status: Literal[DatasetDownloadStatus.SUCCESS]
    url: str


InitializeDatasetDownloadResponse = (
    _InitializeDatasetDownloadFailedResponse
    | _InitializeDatasetDownloadInProgressResponse
    | _InitializeDatasetDownloadSuccessResponse
)


class DatasetDict(TypedDict):
    project_id: str
    dataset_id: str
    name: str
    filename: str
    data_types: dict[str, DataTypeDict]
    directory: DirectoryDict
    is_optimized: bool
    file_extension: str
    size: int
    is_visible: bool
    created_at: str
    modified_at: str


class DataTypeDict(TypedDict):
    data_type: str
    data_formats: str


class DatasetLogDict(TypedDict):
    status: str
    timestamp: str
    job_type: str


# -------------------------------------------------------------------------------------
# Directory Related Data Exchange Types

# -------------------------------------------------------------------------------------
# Flow Related Data Exchange Types

RunVariablesRequest = dict[str, dict[Literal["value"], Any]]


class ScheduleDict(TypedDict):
    name: str
    start_time: str
    end_time: NotRequired[str]
    cron: str


class FlowDict(TypedDict):
    project_id: str
    pipeline_id: str
    name: str
    directory: DirectoryDict
    definition: FlowDefinitionDict
    trigger_downstream_pipelines: bool
    high_volume_preference: bool
    schedule: NotRequired[ScheduleDict]
    last_run: NotRequired[dict]
    next_run: NotRequired[dict]
    created_at: str
    modified_at: str


class FlowDefinitionDict(TypedDict):
    facets: list[FacetDict]
    arrows: list[ArrowDict]
    variables: NotRequired[dict[str, FlowVariableDict]]
    model_variables: NotRequired[dict[str, FlowModelVariableDict]]


class FacetDict(TypedDict):
    facet_id: str
    facet_uid: str
    name: NotRequired[str]
    arguments: NotRequired[dict]


class ArrowDict(TypedDict):
    source: str
    destination: str
    arguments: NotRequired[dict]


class FlowVariableDict(TypedDict):
    name: str
    value: Any
    facet_name: NotRequired[str]
    type: str
    is_list: bool


class FlowModelVariableDict(TypedDict):
    facet_name: str
    model_name: str
    model_version: NotRequired[str]
    model_argument_type: str
    model_arguments: list[dict]


class FlowStatusReportDict(TypedDict):
    status: str
    progress: NotRequired[int]
    message: str


class FlowLogDict(TypedDict):
    log_id: str
    status: str
    user: str
    erroneous_facet_id: NotRequired[str]
    message: str
    timestamp: str


# -------------------------------------------------------------------------------------
# Model Related Data Exchange Types


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


HyperParameterName = str
HyperParameterGroupName = str
ModelHyperParameterGroupDict = dict[HyperParameterName, Any]
ModelHyperParameterGroupType = dict[
    HyperParameterGroupName, ModelHyperParameterGroupDict
]


# -------------------------------------------------------------------------------------
# Specs Related Data Exchange Types


class FacetSpecsDict(TypedDict):
    INPUT: dict[str, dict[str, FacetSpecDict]]
    MID: dict[str, dict[str, FacetSpecDict]]
    OUTPUT: dict[str, dict[str, FacetSpecDict]]


class FacetSpecDict(TypedDict):
    facet_info: FacetInfoDict
    is_deprecated: bool
    is_hidden: bool
    facet_keywords: list[str]
    facet_requirements: list[FacetRequirementDict]
    facet_arguments: list[FacetArgumentSpecDict]
    in_arrow_arguments: list[FacetArrowArgumentSpecDict]
    out_arrow_arguments: list[FacetArrowArgumentSpecDict]


class FacetInfoDict(TypedDict):
    chain_group: str
    facet_group: str
    facet_type: str
    facet_uid: str


class FacetRequirementDict(TypedDict):
    max_child_count: int
    max_parent_count: int
    min_child_count: int
    min_parent_count: int


class FacetArgumentSpecDict(TypedDict):
    name: str
    argument_type: str
    is_required: bool
    default_value: Any | None
    options: NotRequired[list[Any]]
    is_list: bool
    is_deprecated: bool
    is_hidden: bool
    have_sub_arguments: bool
    children: Mapping[str, FacetArgumentSpecDict]


class FacetArrowArgumentSpecDict(TypedDict):
    name: str
    argument_type: str
    is_required: bool
    options: NotRequired[list[Any]]
    is_list: bool
    is_deprecated: bool
    is_hidden: bool
    have_sub_arguments: bool
    children: Mapping[str, FacetArrowArgumentSpecDict]


class ModelSpecDict(TypedDict):
    name: str
    is_deprecated: bool
    is_hidden: bool
    keywords: list[str]
    sub_model_types: list[SubModelSpecDict]


class SubModelSpecDict(TypedDict):
    name: str
    is_deprecated: bool
    is_hidden: bool
    keywords: list[str]
    metrics: ModelMetricsSpecDict
    parameters: dict[str, ModelParameterSpecDict]
    hyperparameters: dict[str, ModelHyperparameterSpecDict]


class EmptyDict(TypedDict):
    pass


ModelMetricsSpecDict = dict[str, EmptyDict]


class ModelParameterSpecDict(TypedDict):
    name: str
    default_value: Any
    have_options: bool
    is_deprecated: bool
    is_hidden: bool
    is_list: bool
    options: list[Any]
    parameter_type: str


class ModelHyperparameterSpecDict(TypedDict):
    name: str
    default_value: Any
    have_options: bool
    have_sub_hyperparameters: bool
    hyperparameter_group: str | None
    hyperparameter_type: str
    is_deprecated: bool
    is_hidden: bool
    is_list: bool
    children: dict[str, ModelHyperparameterSpecDict]
    options: list[Any]
    sub_hyperparameter_requirements: list[tuple[Any, list[str]]]


# -------------------------------------------------------------------------------------
