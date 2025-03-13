# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
import time
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr, Field
from tqdm.auto import tqdm

from ikigai.client import Client
from ikigai.typing.protocol import (
    Directory,
    DirectoryType,
    FlowDefinitionDict,
    NamedDirectoryDict,
)
from ikigai.utils.compatibility import UTC, Self
from ikigai.utils.custom_validators import OptionalStr
from ikigai.utils.named_mapping import NamedMapping

logger = logging.getLogger("ikigai.components")


class FlowDefinition(BaseModel):
    _facets: list = []
    _arrows: list = []
    _arguments: dict = {}
    _variables: dict = {}
    _model_variables: dict = {}

    def to_dict(self) -> FlowDefinitionDict:
        # TODO: Update implementation when feature is available
        return {
            "facets": self._facets,
            "arrows": self._arrows,
            "arguments": self._arguments,
            "variables": self._variables,
            "model_variables": self._model_variables,
        }


class FlowBuilder:
    _app_id: str
    _name: str
    _directory: Directory | None
    _flow_definition: FlowDefinitionDict
    __client: Client

    def __init__(self, client: Client, app_id: str) -> None:
        self.__client = client
        self._app_id = app_id
        self._name = ""
        self._directory = None
        self._flow_definition = FlowDefinition().to_dict()

    def new(self, name: str) -> Self:
        self._name = name
        return self

    def definition(
        self, definition: Flow | FlowDefinition | FlowDefinitionDict
    ) -> Self:
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
            resp = self.__client.get(
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
            "must be a Flow or FlowDefinition or FlowDefinitionDict"
        )
        raise TypeError(error_msg)

    def directory(self, directory: Directory) -> Self:
        self._directory = directory
        return self

    def build(self) -> Flow:
        flow_id = self.__client.component.create_flow(
            app_id=self._app_id,
            name=self._name,
            directory=self._directory,
            flow_definition=self._flow_definition,
        )

        # Populate Flow object
        resp = self.__client.get(
            path="/component/get-pipeline", params={"pipeline_id": flow_id}
        ).json()
        flow = Flow.from_dict(data=resp["pipeline"], client=self.__client)
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
    __client: Client

    @classmethod
    def from_dict(cls, data: dict, client: Client) -> Self:
        logger.debug("Creating a %s from %s", cls.__name__, data)
        self = cls.model_validate(data)
        self.__client = client
        return self

    def to_dict(self) -> dict:
        return {
            "flow_id": self.flow_id,
            "name": self.name,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
        }

    def delete(self) -> None:
        self.__client.post(
            path="/component/delete-pipeline",
            json={"pipeline": {"project_id": self.app_id, "pipeline_id": self.flow_id}},
        )
        return None

    def rename(self, name: str) -> Self:
        _ = self.__client.post(
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

    def move(self, directory: Directory) -> Self:
        _ = self.__client.post(
            path="/component/edit-pipeline",
            json={
                "pipeline": {
                    "project_id": self.app_id,
                    "pipeline_id": self.flow_id,
                    "directory": {
                        "directory_id": directory.directory_id,
                        "type": directory.type,
                    },
                }
            },
        )
        return self

    def status(self) -> FlowStatusReport:
        resp = self.__client.get(
            path="/component/is-pipeline-running",
            params={"project_id": self.app_id, "pipeline_id": self.flow_id},
        ).json()

        if not resp["status"]:
            return FlowStatusReport(status=FlowStatus.IDLE, message="")

        return FlowStatusReport.from_dict(resp["progress"])

    def run_logs(
        self, max_count: int = 1, since: datetime | None = None
    ) -> list[RunLog]:
        resp = self.__client.get(
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
        self.__client.post(
            path="/component/run-pipeline",
            json={"pipeline": {"project_id": self.app_id, "pipeline_id": self.flow_id}},
        )

        return self.__await_run()

    def describe(self) -> dict:
        response: dict[str, Any] = self.__client.get(
            path="/component/get-pipeline", params={"pipeline_id": self.flow_id}
        ).json()

        return response

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


class FlowDirectoryBuilder:
    _app_id: str
    _name: str
    _parent_id: str
    __client: Client

    def __init__(self, client: Client, app_id: str) -> None:
        self.__client = client
        self._app_id = app_id
        self._name = ""
        self._parent_id = ""

    def new(self, name: str) -> Self:
        self._name = name
        return self

    def parent(self, parent: Directory) -> Self:
        self._parent_id = parent.directory_id
        return self

    def build(self) -> FlowDirectory:
        resp = self.__client.post(
            path="/component/create-pipeline-directory",
            json={
                "directory": {
                    "name": self._name,
                    "project_id": self._app_id,
                    "parent_id": self._parent_id,
                }
            },
        ).json()
        directory_id = resp["directory_id"]
        resp = self.__client.get(
            path="/component/get-pipeline-directory",
            params={"project_id": self._app_id, "directory_id": directory_id},
        ).json()

        directory = FlowDirectory.from_dict(
            data=resp["directory"], client=self.__client
        )
        return directory


class FlowDirectory(BaseModel):
    app_id: str = Field(validation_alias="project_id")
    directory_id: str
    name: str
    __client: Client

    @property
    def type(self) -> DirectoryType:
        return DirectoryType.FLOW

    @classmethod
    def from_dict(cls, data: dict, client: Client) -> Self:
        logger.debug("Creating a %s from %s", cls.__name__, data)
        self = cls.model_validate(data)
        self.__client = client
        return self

    def to_dict(self) -> NamedDirectoryDict:
        return {"directory_id": self.directory_id, "type": self.type, "name": self.name}

    def directories(self) -> NamedMapping[Self]:
        resp = self.__client.get(
            path="/component/get-pipeline-directories-for-project",
            params={"project_id": self.app_id, "directory_id": self.directory_id},
        ).json()
        directories = {
            directory.directory_id: directory
            for directory in (
                self.from_dict(data=directory_dict, client=self.__client)
                for directory_dict in resp["directories"]
            )
        }

        return NamedMapping(directories)

    def flows(self) -> NamedMapping[Flow]:
        resp = self.__client.get(
            path="/component/get-pipelines-for-project",
            params={"project_id": self.app_id, "directory_id": self.directory_id},
        ).json()

        flows = {
            flow.flow_id: flow
            for flow in (
                Flow.from_dict(data=flow_dict, client=self.__client)
                for flow_dict in resp["pipelines"]
            )
        }

        return NamedMapping(flows)
