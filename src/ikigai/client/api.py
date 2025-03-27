# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import InitVar
from typing import Any, cast

from pydantic import Field
from pydantic.dataclasses import dataclass

from ikigai.client.session import Session
from ikigai.typing.api import (
    GetComponentsForProjectResponse,
    GetDatasetMultipartUploadUrlsResponse,
)
from ikigai.typing.protocol import (
    Directory,
    DirectoryDict,
    FlowDefinitionDict,
    FlowStatusReportDict,
)
from ikigai.typing.protocol.app import AppDict
from ikigai.typing.protocol.flow import FlowDict

_UNSET: Any = object()


@dataclass
class ComponentAPI:
    # Init only vars
    session: InitVar[Session]

    __session: Session = Field(init=False)

    def __post_init__(self, session: Session) -> None:
        self.__session = session

    """
    App APIs
    """

    def create_app(
        self,
        name: str,
        description: str,
        directory: Directory | None,
    ) -> str:
        directory_dict = (
            cast(dict, directory.to_dict()) if directory is not None else {}
        )
        resp = self.__session.post(
            path="/component/create-project",
            json={
                "project": {
                    "name": name,
                    "description": description,
                    "directory": directory_dict,
                },
            },
        ).json()
        return resp["project_id"]

    def get_app(self, app_id: str) -> AppDict:
        app_dict = self.__session.get(
            path="/component/get-project", params={"project_id": app_id}
        ).json()["project"]

        return cast(AppDict, app_dict)

    def get_app_directories_for_user(
        self, directory_id: str = _UNSET
    ) -> list[DirectoryDict]:
        if directory_id == _UNSET:
            directory_id = ""

        directory_dicts = self.__session.get(
            path="/component/get-project-directories-for-user",
            params={"directory_id": directory_id},
        ).json()["directories"]

        return cast(list[DirectoryDict], directory_dicts)

    def get_apps_for_user(self, directory_id: str = _UNSET) -> list[AppDict]:
        fetch_all = directory_id == _UNSET
        if directory_id == _UNSET:
            directory_id = ""

        app_dicts = self.__session.get(
            path="/component/get-projects-for-user",
            params={"fetch_all": fetch_all, "directory_id": directory_id},
        ).json()["projects"]

        return cast(list[AppDict], app_dicts)

    def get_components_for_app(self, app_id: str) -> GetComponentsForProjectResponse:
        resp = self.__session.get(
            path="/component/get-components-for-project",
            params={"project_id": app_id},
        ).json()["project_components"][app_id]

        return cast(GetComponentsForProjectResponse, resp)

    """
    Dataset APIs
    """

    def create_dataset(
        self, app_id: str, name: str, directory: Directory | None
    ) -> str:
        directory_dict = (
            cast(dict, directory.to_dict()) if directory is not None else {}
        )
        resp = self.__session.post(
            path="/component/create-dataset",
            json={
                "dataset": {
                    "project_id": app_id,
                    "name": name,
                    "directory": directory_dict,
                },
            },
        ).json()
        return resp["dataset_id"]

    def get_dataset_multipart_upload_urls(
        self, dataset_id: str, app_id: str, filename: str, num_parts: int
    ) -> GetDatasetMultipartUploadUrlsResponse:
        resp = self.__session.get(
            path="/component/get-dataset-multipart-upload-urls",
            params={
                "dataset_id": dataset_id,
                "project_id": app_id,
                "filename": filename,
                "number_of_parts": num_parts,
            },
        ).json()

        return GetDatasetMultipartUploadUrlsResponse(
            upload_id=resp["upload_id"],
            content_type=resp["content_type"],
            urls={
                int(chunk_idx): upload_url
                for chunk_idx, upload_url in resp["urls"].items()
            },
        )

    """
    Flow APIs
    """

    def create_flow(
        self,
        app_id: str,
        name: str,
        directory: Directory | None,
        flow_definition: FlowDefinitionDict,
    ) -> str:
        directory_dict = (
            cast(dict, directory.to_dict()) if directory is not None else {}
        )
        resp = self.__session.post(
            path="/component/create-pipeline",
            json={
                "pipeline": {
                    "project_id": app_id,
                    "name": name,
                    "directory": directory_dict,
                    "definition": flow_definition,
                },
            },
        ).json()
        return resp["pipeline_id"]

    def get_flow(self, flow_id: str) -> FlowDict:
        flow = self.__session.get(
            path="/component/get-pipeline", params={"pipeline_id": flow_id}
        ).json()["pipeline"]

        return cast(FlowDict, flow)

    def get_flows_for_app(
        self, app_id: str, directory_id: str | None = None
    ) -> list[FlowDict]:
        params = {"project_id": app_id}

        if directory_id is not None:
            params["directory_id"] = directory_id

        flows = self.__session.get(
            path="/component/get-pipelines-for-project",
            params=params,
        ).json()["pipelines"]

        return cast(list[FlowDict], flows)

    def edit_flow(
        self,
        app_id: str,
        flow_id: str,
        name: str | None = None,
        directory: Directory | None = None,
        flow_definition: FlowDefinitionDict | None = None,
    ) -> str:
        pipeline: dict[str, Any] = {
            "project_id": app_id,
            "pipeline_id": flow_id,
        }

        if name is not None:
            pipeline["name"] = name
        if directory is not None:
            pipeline["directory"] = directory.to_dict()
        if flow_definition is not None:
            pipeline["definition"] = flow_definition

        resp = self.__session.post(
            path="/component/edit-pipeline", json={"pipeline": pipeline}
        ).json()
        return resp["pipeline_id"]

    def delete_flow(self, app_id: str, flow_id: str) -> str:
        resp = self.__session.post(
            path="/component/delete-pipeline",
            json={"pipeline": {"project_id": app_id, "pipeline_id": flow_id}},
        ).json()

        return resp["pipeline_id"]

    def run_flow(self, app_id: str, flow_id: str) -> str:
        resp = self.__session.post(
            path="/component/run-pipeline",
            json={"pipeline": {"project_id": app_id, "pipeline_id": flow_id}},
        ).json()

        return resp["pipeline_id"]

    def is_flow_runing(self, app_id: str, flow_id: str) -> FlowStatusReportDict:
        resp = self.__session.get(
            path="/component/is-pipeline-running",
            params={"project_id": app_id, "pipeline_id": flow_id},
        ).json()
        return resp["progress"]
