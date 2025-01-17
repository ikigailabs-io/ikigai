# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import time
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr, Field
from tqdm.auto import tqdm

from ikigai.client.session import Session
from ikigai.utils.compatibility import UTC, Self
from ikigai.utils.custom_validators import OptionalStr
from ikigai.utils.protocols import Directory


class FlowDefinition(BaseModel):
    facets: list = []
    arrows: list = []
    # TODO: Add Flow Definition

    def to_dict(self) -> dict[str, Any]:
        # TODO: Update implementation when feature is available
        return {
            "facets": [],
            "arrows": [],
        }


class FlowBuilder:
    _app_id: str
    _name: str
    _directory: dict[str, str]
    _flow_definition: dict[str, Any]
    __session: Session

    def __init__(self, session: Session, app_id: str) -> None:
        self.__session = session
        self._app_id = app_id
        self._name = ""
        self._directory = {}
        self._flow_definition = FlowDefinition().to_dict()

    def new(self, name: str) -> Self:
        self._name = name
        return self

    def definition(self, definition: Flow | FlowDefinition | dict[str, Any]) -> Self:
        if isinstance(definition, FlowDefinition):
            self._flow_definition = definition.to_dict()
            return self

        if isinstance(definition, Flow):
            if definition.app_id != self._app_id:
                error_msg = (
                    "Building flow from a diferent app is not supported\n"
                    "source_app != destination_app "
                    f"({definition.app_id} != {self._app_id})"
                )
                raise ValueError(error_msg)
            resp = self.__session.get(
                path="/component/get-pipeline",
                params={"project_id": self._app_id, "pipeline_id": definition.flow_id},
            ).json()
            self._flow_definition = resp["pipeline"]["definition"]
            return self

        if isinstance(definition, dict):
            self._flow_definition = definition
            return self

        error_msg = (
            f"Definition was of type {type(definition)} but, "
            "must be a Flow or FlowDefinition or dict"
        )
        raise TypeError(error_msg)

    def directory(self, directory: Directory) -> Self:
        self._directory = {
            "directory_id": directory.directory_id,
            "type": directory.type,
        }
        return self

    def build(self) -> Flow:
        resp = self.__session.post(
            path="/component/create-pipeline",
            json={
                "pipeline": {
                    "project_id": self._app_id,
                    "name": self._name,
                    "directory": self._directory,
                    "definition": self._flow_definition,
                }
            },
        ).json()
        flow_id = resp["pipeline_id"]

        # Populate Flow object
        resp = self.__session.get(
            path="/component/get-pipeline", params={"pipeline_id": flow_id}
        ).json()
        flow = Flow.from_dict(data=resp["pipeline"], session=self.__session)
        return flow


class FlowStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"
    IDLE = "IDLE"
    SUCCESS = "SUCCESS"  # Not available via /component/is-pipeline-running

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


class RunLog(BaseModel):
    log_id: str
    status: FlowStatus
    user: EmailStr
    erroneous_facet_id: OptionalStr
    data: str = Field(validation_alias="message")
    timestamp: datetime

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

    def to_dict(self) -> dict:
        return {
            "flow_id": self.flow_id,
            "name": self.name,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
        }

    def delete(self) -> None:
        self.__session.post(
            path="/component/delete-pipeline",
            json={"pipeline": {"project_id": self.app_id, "pipeline_id": self.flow_id}},
        )
        return None

    def rename(self, name: str) -> Self:
        _ = self.__session.post(
            path="/component/edit-pipeline",
            json={
                "pipeline": {
                    "project_id": self.app_id,
                    "pipeline_id": self.flow_id,
                    "name": name,
                }
            },
        )
        # TODO: handle error case, currently it is a raise NotImplemented from Session
        self.name = name
        return self

    def status(self) -> FlowStatusReport:
        resp = self.__session.get(
            path="/component/is-pipeline-running",
            params={"project_id": self.app_id, "pipeline_id": self.flow_id},
        ).json()

        if not resp["status"]:
            return FlowStatusReport(status=FlowStatus.IDLE, message="")

        return FlowStatusReport.from_dict(resp["progress"])

    def run_logs(
        self, max_count: int = 1, since: datetime | None = None
    ) -> list[RunLog]:
        resp = self.__session.get(
            path="/component/get-pipeline-log",
            params={
                "pipeline_id": self.flow_id,
                "project_id": self.app_id,
                "limit": max_count,
            },
        ).json()

        run_logs = [RunLog.from_dict(data=log) for log in resp["pipeline_log"]]
        if since is not None:
            run_logs = [log for log in run_logs if log.timestamp > since]
        return run_logs

    def run(self) -> RunLog:
        # Start running pipeline
        self.__session.post(
            path="/component/run-pipeline",
            json={"pipeline": {"project_id": self.app_id, "pipeline_id": self.flow_id}},
        )

        return self.__await_run()

    def __await_run(self) -> RunLog:
        start_time = datetime.now(UTC)
        # TODO: Switch to using websockets once they are available
        with tqdm(total=100, dynamic_ncols=True) as progress_bar:
            status_report = self.status()
            progress_bar.desc = status_report.status
            progress_bar.update(0)

            # Initially wait while pipeline is scheduled
            while status_report.status == FlowStatus.SCHEDULED:
                time.sleep(5)
                status_report = self.status()

            last_progress = status_report.progress if status_report.progress else 0
            progress_bar.desc = status_report.status
            progress_bar.update(last_progress)

            # Wait while pipeline is running
            while status_report.status == FlowStatus.RUNNING:
                time.sleep(1)
                status_report = self.status()
                progress = status_report.progress if status_report.progress else 100
                progress_bar.desc = status_report.status
                progress_bar.update(progress - last_progress)
                last_progress = progress
            # Flow run completed

            # Get status from logs and update progress bar
            run_logs = self.run_logs(max_count=1, since=start_time)
            if not run_logs:
                # TODO: Give a better error message
                error_msg = (
                    "No logs found for"
                    f" <Flow(flow_id={self.flow_id}, name={self.name})>"
                    f" after the flow started running ({start_time=})."
                )
                raise RuntimeError(error_msg)
            run_log = run_logs[0]

            progress = 100
            progress_bar.desc = run_log.status
            progress_bar.update(progress - last_progress)

            return run_log
