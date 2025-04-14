# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypedDict


class GetDatasetMultipartUploadUrlsResponse(TypedDict):
    upload_id: str
    content_type: str
    urls: dict[int, str]


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
