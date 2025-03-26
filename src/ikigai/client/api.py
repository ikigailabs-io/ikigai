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
        resp = self.__session.get(
            path="/component/get-project", params={"project_id": app_id}
        ).json()["project"]

        return AppDict(
            app_id=resp["project_id"],
            name=resp["name"],
            owner=resp["owner"],
            description=resp["description"],
            icon=resp["icon"],
            images=resp["images"],
            directory=cast(DirectoryDict, resp["directory"]),
            created_at=resp["created_at"],
            modified_at=resp["modified_at"],
            last_used_at=resp["last_used_at"],
        )

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

        return [
            AppDict(
                app_id=app_dict["project_id"],
                name=app_dict["name"],
                owner=app_dict["owner"],
                description=app_dict["description"],
                icon=app_dict["icon"],
                images=app_dict["images"],
                directory=cast(DirectoryDict, app_dict["directory"]),
                created_at=app_dict["created_at"],
                modified_at=app_dict["modified_at"],
                last_used_at=app_dict["last_used_at"],
            )
            for app_dict in app_dicts
        ]

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
