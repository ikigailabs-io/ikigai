# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any, TypedDict

from ikigai.typing.protocol.directory import DirectoryDict
from ikigai.utils.compatibility import NotRequired


class FlowDict(TypedDict):
    project_id: str
    pipeline_id: str
    name: str
    directory: DirectoryDict
    definition: FlowDefinitionDict
    trigger_downstream_pipelines: bool
    high_volume_preference: bool
    schedule: dict
    last_run: NotRequired[dict]
    next_run: NotRequired[dict]
    created_at: str
    modified_at: str


class FlowDefinitionDict(TypedDict):
    facets: list[FacetDict]
    arrows: list[ArrowDict]
    arguments: NotRequired[dict]
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
