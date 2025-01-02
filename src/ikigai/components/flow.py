# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from ikigai.client.session import Session
from ikigai.utils.compatibility import Self


class FlowBuilder:
    def __init__(self, session: Session, app_id: str) -> None:
        raise NotImplementedError()


class FlowStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"
    IDLE = "IDLE"

    def __repr__(self) -> str:
        return self.value


class FlowStatusReport(BaseModel):
    status: FlowStatus
    progress: int | None = Field(default=None)
    message: str

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        self = cls.model_validate(data)
        return self


class Flow(BaseModel):
    app_id: str = Field(validation_alias="project_id")
    flow_id: str = Field(validation_alias="pipeline_id")
    name: str
    created_at: datetime
    modified_at: datetime
    __session: Session

    @classmethod
    def from_dict(cls, data: dict, session: Session) -> Self:
        self = cls.model_validate(data)
        self.__session = session
        return self

    def status(self) -> FlowStatusReport:
        resp = self.__session.get(
            path="/component/is-pipeline-running",
            params={"project_id": self.app_id, "pipeline_id": self.flow_id},
        ).json()

        if not resp["status"]:
            return FlowStatusReport(status=FlowStatus.IDLE, message="")

        return FlowStatusReport.from_dict(resp["progress"])

