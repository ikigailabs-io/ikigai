# SPDX-FileCopyrightText: 2026-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from ikigai.utils.compatibility import StrEnum

# -------------------------------------------------------------------------------------
# App Related Enums


class AppAccessLevel(StrEnum):
    OWNER = "OWNER"
    BUILDER = "BUILDER"
    VIEWER = "VIEWER"


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
