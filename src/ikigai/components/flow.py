# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
import time
from collections.abc import Mapping
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import AliasChoices, BaseModel, EmailStr, Field
from tqdm.auto import tqdm

from ikigai.client import Client
from ikigai.components.flow_definition import FlowDefinition
from ikigai.typing.api import RunVariablesRequest
from ikigai.typing.protocol import (
    Directory,
    DirectoryType,
    FlowDefinitionDict,
    FlowDict,
    NamedDirectoryDict,
)
from ikigai.utils.compatibility import UTC, Self, deprecated
from ikigai.utils.custom_validators import OptionalStr
from ikigai.utils.named_mapping import NamedMapping
from ikigai.utils.shim import flow_versioning_shim

logger = logging.getLogger("ikigai.components")


class FlowBrowser:
    __app_id: str
    __client: Client

    def __init__(self, app_id: str, client: Client) -> None:
        self.__app_id = app_id
        self.__client = client

    @deprecated("Prefer directly loading by name:\n\tapp.flows['flow_name']")
    def __call__(self) -> NamedMapping[Flow]:
        flows = {
            flow["pipeline_id"]: Flow.from_dict(data=flow, client=self.__client)
            for flow in self.__client.component.get_flows_for_app(app_id=self.__app_id)
        }

        return NamedMapping(flows)

    def __getitem__(self, name: str) -> Flow:
        flow_dict = self.__client.component.get_flow_by_name(
            app_id=self.__app_id, name=name
        )

        return Flow.from_dict(data=flow_dict, client=self.__client)

    def search(self, query: str) -> NamedMapping[Flow]:
        matched_flows = {
            flow["pipeline_id"]: Flow.from_dict(data=flow, client=self.__client)
            for flow in self.__client.search.search_flows_for_project(
                app_id=self.__app_id, query=query
            )
        }

        return NamedMapping(matched_flows)


class FlowBuilder:
    _app_id: str
    _name: str
    _directory: Directory | None
    _high_volume_preference: bool
    _flow_definition: FlowDefinitionDict
    __client: Client

    def __init__(self, client: Client, app_id: str) -> None:
        """
        Initialize the FlowBuilder

        Note
        ----
        The FlowBuilder initialization should only happen internally via
        the App object.

        Parameters
        ----------
        client : Client
            The Ikigai client to use for API interactions

        app_id : str
            The ID of the App to which the flow will belong

        Returns
        -------
        None
        """
        self.__client = client
        self._app_id = app_id
        self._name = ""
        self._directory = None
        self._high_volume_preference = False
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
            flow_dict = self.__client.component.get_flow(flow_id=definition.flow_id)
            self._flow_definition = flow_dict["definition"]
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

    def high_volume_preference(self, optimize: bool) -> Self:
        """
        Set the high volume preference flag for the flow.

        Parameters
        ----------
        optimize : bool
            The high volume preference to set for the flow.
            True if the flow should be optimized for high volume data processing,
            False otherwise.

        Returns
        -------
        Self
            The FlowBuilder instance with high volume preference set.
        """
        self._high_volume_preference = optimize
        return self

    def build(self) -> Flow:
        """
        Build the Flow object

        Creates the flow in the Ikigai platform using the provided
        parameters and returns the corresponding Flow object.

        Returns
        -------
        Flow
            The created Flow object
        """
        flow_id = self.__client.component.create_flow(
            app_id=self._app_id,
            name=self._name,
            directory=self._directory,
            high_volume_preference=self._high_volume_preference,
            flow_definition=self._flow_definition,
        )

        # Populate Flow object
        flow_dict = self.__client.component.get_flow(flow_id=flow_id)

        return Flow.from_dict(data=flow_dict, client=self.__client)


class FlowStatus(str, Enum):
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


class FlowStatusReport(BaseModel):
    status: FlowStatus
    progress: int | None = Field(default=None)
    message: str

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Self:
        return cls.model_validate(data)


class RunLog(BaseModel):
    log_id: str
    status: FlowStatus
    user: EmailStr
    erroneous_facet_id: OptionalStr
    data: str = Field(validation_alias="message")
    timestamp: datetime

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Self:
        return cls.model_validate(data)


class Flow(BaseModel):
    app_id: str = Field(validation_alias=AliasChoices("app_id", "project_id"))
    flow_id: str = Field(validation_alias=AliasChoices("flow_id", "pipeline_id"))
    name: str
    created_at: datetime
    modified_at: datetime
    __client: Client

    @classmethod
    def from_dict(cls, data: Mapping[str, Any], client: Client) -> Self:
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
        self.__client.component.delete_flow(app_id=self.app_id, flow_id=self.flow_id)
        return None

    def rename(self, name: str) -> Self:
        self.__client.component.edit_flow(
            app_id=self.app_id, flow_id=self.flow_id, name=name
        )
        # TODO: handle error case, currently it is a raise NotImplemented from Session
        self.name = name
        return self

    def move(self, directory: Directory) -> Self:
        self.__client.component.edit_flow(
            app_id=self.app_id, flow_id=self.flow_id, directory=directory
        )
        return self

    def update_high_volume_preference(self, optimize: bool) -> Self:
        """
        Update the high volume preference of the flow.

        Parameters
        ----------
        optimize : bool
            The new high volume preference to set for the flow.
            True if the flow should be optimized for high volume data processing,
            False otherwise.

        Returns
        -------
        Self
            The updated Flow object.
        """
        self.__client.component.edit_flow(
            app_id=self.app_id,
            flow_id=self.flow_id,
            high_volume_preference=optimize,
        )
        return self

    def update_definition(
        self, definition: FlowDefinition | FlowDefinitionDict
    ) -> Self:
        """
        Update the flow definition.

        Replaces the existing flow definition with the provided one.

        Parameters
        ----------
        definition : FlowDefinition | FlowDefinitionDict
            The new flow definition to set. Can be provided as a FlowDefinition
            object or as a dictionary.

        Returns
        -------
        Self
            The updated Flow object.

        """
        if isinstance(definition, FlowDefinition):
            definition = definition.to_dict()

        self.__client.component.edit_flow(
            app_id=self.app_id, flow_id=self.flow_id, flow_definition=definition
        )
        return self

    def status(self) -> FlowStatusReport:
        resp = self.__client.component.is_flow_runing(
            app_id=self.app_id, flow_id=self.flow_id
        )
        return FlowStatusReport.from_dict(resp)

    def run_logs(
        self, max_count: int = 1, since: datetime | None = None
    ) -> list[RunLog]:
        log_dicts = self.__client.component.get_flow_log(
            app_id=self.app_id, flow_id=self.flow_id, max_count=max_count
        )

        run_logs = [RunLog.from_dict(data=log) for log in log_dicts]
        if since is not None:
            run_logs = [log for log in run_logs if log.timestamp > since]
        return run_logs

    def run(self, **variables) -> RunLog:
        """
        Run the flow

        This function will run the flow and wait for it to complete.
        It will accept any number of keyword arguments which will be passed as run
        variables to the flow.

        Parameters
        ----------
        **variables : dict
            Run variables to be passed to the flow, where the key is the variable name
            and the value is the variable value. Keys that start with an
            underscore ("_") are reserved for future use and will be ignored.

        Returns
        -------
        RunLog
            The final run log of the flow after completion
        """
        run_variables: RunVariablesRequest = {
            key: {"value": value}
            for key, value in variables.items()
            if not key.startswith("_")
        }

        # Start running pipeline
        self.__client.component.run_flow(
            app_id=self.app_id, flow_id=self.flow_id, variables=run_variables
        )

        return self.__await_run()

    def describe(self) -> FlowDict:
        flow = self.__client.component.get_flow(flow_id=self.flow_id)
        # Apply flow_versioning_shim to allow migration of older flows
        # TODO: Remove this shim after "important" flows are migrated
        facet_specs = self.__client.get(
            path="/component/get-facet-specs",
        ).json()
        # shim is a hack so better to keep it explicit
        shimed_flow = flow_versioning_shim(flow=flow, facet_specs=facet_specs)
        return shimed_flow  # noqa: RET504

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
            running_states = (
                FlowStatus.RUNNING,  # Flow is running
                FlowStatus.STOPPING,  # Flow is in the process of stopping
                FlowStatus.SCHEDULED,  # Flow is scheduled (again), likely a retry
                FlowStatus.UNKNOWN,  # Flow status is unknown, but known was running
            )
            while status_report.status in running_states:
                time.sleep(1)
                status_report = self.status()
                progress = status_report.progress if status_report.progress else 100
                progress_bar.desc = status_report.status
                new_progress = last_progress + max(progress - last_progress, 0)
                progress_bar.update(new_progress - last_progress)
                last_progress = new_progress
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
    _parent: Directory | None
    __client: Client

    def __init__(self, client: Client, app_id: str) -> None:
        self.__client = client
        self._app_id = app_id
        self._name = ""
        self._parent = None

    def new(self, name: str) -> Self:
        self._name = name
        return self

    def parent(self, parent: Directory) -> Self:
        self._parent = parent
        return self

    def build(self) -> FlowDirectory:
        directory_id = self.__client.component.create_flow_directory(
            app_id=self._app_id, name=self._name, parent=self._parent
        )
        directory_dict = self.__client.component.get_flow_directory(
            app_id=self._app_id, directory_id=directory_id
        )

        return FlowDirectory.from_dict(data=directory_dict, client=self.__client)


class FlowDirectory(BaseModel):
    app_id: str = Field(validation_alias="project_id")
    directory_id: str
    name: str
    __client: Client

    @property
    def type(self) -> DirectoryType:
        return DirectoryType.FLOW

    @classmethod
    def from_dict(cls, data: Mapping[str, Any], client: Client) -> Self:
        logger.debug("Creating a %s from %s", cls.__name__, data)
        self = cls.model_validate(data)
        self.__client = client
        return self

    def to_dict(self) -> NamedDirectoryDict:
        return {"directory_id": self.directory_id, "type": self.type, "name": self.name}

    def directories(self) -> NamedMapping[Self]:
        directory_dicts = self.__client.component.get_flow_directories_for_app(
            app_id=self.app_id, parent=self
        )
        directories = {
            directory.directory_id: directory
            for directory in (
                self.from_dict(data=directory_dict, client=self.__client)
                for directory_dict in directory_dicts
            )
        }

        return NamedMapping(directories)

    def flows(self) -> NamedMapping[Flow]:
        flow_dicts = self.__client.component.get_flows_for_app(
            app_id=self.app_id, directory_id=self.directory_id
        )

        flows = {
            flow.flow_id: flow
            for flow in (
                Flow.from_dict(data=flow_dict, client=self.__client)
                for flow_dict in flow_dicts
            )
        }

        return NamedMapping(flows)
