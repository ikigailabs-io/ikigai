# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import time
from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field
from tqdm.auto import tqdm

from ikigai.client.session import Session
from ikigai.utils.compatibility import Self
from ikigai.utils.custom_validators import OptionalInt


class FlowBuilder:
    def __init__(self, session: Session, app_id: str) -> None:
        raise NotImplementedError()


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
    erroneous_facet_id: OptionalInt
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
