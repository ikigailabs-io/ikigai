# SPDX-FileCopyrightText: 2026-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import Any

from ikigai.utils.compatibility import Self, StrEnum

# -------------------------------------------------------------------------------------
# App Related Enums


class AppAccessLevel(StrEnum):
    OWNER = "OWNER"
    BUILDER = "BUILDER"
    VIEWER = "VIEWER"


# -------------------------------------------------------------------------------------
# Custom Facet Related Enums


class CustomFacetArgumentType(StrEnum):
    BOOLEAN = "bool"
    INTEGER = "int"
    STRING = "str"
    FLOAT = "float"

    @classmethod
    def from_value(cls, value: Any) -> Self:
        type_name = type(value).__name__
        return cls(type_name)

    @property
    def python_type(self) -> type[bool | int | str | float]:
        return {
            CustomFacetArgumentType.BOOLEAN: bool,
            CustomFacetArgumentType.INTEGER: int,
            CustomFacetArgumentType.STRING: str,
            CustomFacetArgumentType.FLOAT: float,
        }[self]

    def to_facet_argument_type(self) -> FacetArgumentType:
        return {
            CustomFacetArgumentType.BOOLEAN: FacetArgumentType.BOOLEAN,
            CustomFacetArgumentType.INTEGER: FacetArgumentType.NUMBER,
            CustomFacetArgumentType.STRING: FacetArgumentType.TEXT,
            CustomFacetArgumentType.FLOAT: FacetArgumentType.NUMBER,
        }[self]


# -------------------------------------------------------------------------------------
# Dataset Related Enums


class DatasetDownloadStatus(StrEnum):
    SUCCESS = "SUCCESS"
    IN_PROGRESS = "IN_PROGRESS"
    FAILED = "FAILED"


class DatasetDataType(StrEnum):
    NUMERIC = "NUMERIC"
    TEXT = "TEXT"
    CATEGORICAL = "CATEGORICAL"
    TIME = "TIME"


# -------------------------------------------------------------------------------------
# Directory Related Enums


class DirectoryType(StrEnum):
    APP = "PROJECT"
    DATASET = "DATASET"
    FLOW = "PIPELINE"
    MODEL = "MODEL"


# -------------------------------------------------------------------------------------
# Flow Related Enums


class FlowStatus(StrEnum):
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"
    IDLE = "IDLE"
    UNKNOWN = "UNKNOWN"
    SUCCESS = "SUCCESS"  # Not available via /component/is-pipeline-running

    def __repr__(self) -> str:
        return self.value


# -------------------------------------------------------------------------------------
# Specs Related Enums


class FacetArgumentType(StrEnum):
    MAP = "MAP"
    BOOLEAN = "BOOLEAN"
    TEXT = "TEXT"
    NUMBER = "NUMBER"


class ModelHyperparameterType(StrEnum):
    MAP = "MAP"
    BOOLEAN = "BOOLEAN"
    TEXT = "TEXT"
    NUMBER = "NUMBER"


class ModelParameterType(StrEnum):
    BOOLEAN = "BOOLEAN"
    TEXT = "TEXT"
    NUMBER = "NUMBER"


# -------------------------------------------------------------------------------------
