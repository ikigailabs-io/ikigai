# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypedDict

from ikigai.utils.enums import DatasetDownloadStatus

RunVariablesRequest = dict[str, dict[Literal["value"], Any]]


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
