# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import InitVar
from functools import cache
from typing import Any, cast

from pydantic import Field
from pydantic.dataclasses import dataclass

from ikigai.client.session import Session
from ikigai.typing.api import (
    GetComponentsForProjectResponse,
    GetDatasetMultipartUploadUrlsResponse,
)
from ikigai.typing.protocol import (
    AppDict,
    DatasetDict,
    DatasetLogDict,
    Directory,
    DirectoryDict,
    FlowDefinitionDict,
    FlowDict,
    FlowLogDict,
    FlowStatusReportDict,
    ModelDict,
    ModelSpecDict,
    ModelType,
    ModelVersionDict,
)

_UNSET: Any = object()


@dataclass
class ComponentAPI:
    # Init only vars
    session: InitVar[Session]

    __session: Session = Field(init=False)

    def __post_init__(self, session: Session) -> None:
        self.__session = session

    def __hash__(self) -> int:
        # Enable the usage of @cache on specs related apis
        return hash(id(self))

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

    def edit_app(
        self,
        app_id: str,
        name: str = _UNSET,
        directory: Directory = _UNSET,
        description: str = _UNSET,
    ) -> str:
        app: dict[str, Any] = {"project_id": app_id}

        if name != _UNSET:
            app["name"] = name
        if directory != _UNSET:
            app["directory"] = directory.to_dict()
        if description != _UNSET:
            app["description"] = description

        resp = self.__session.post(
            path="/component/edit-project",
            json={"project": app},
        ).json()

        return resp["project_id"]

    def delete_app(self, app_id: str) -> str:
        resp = self.__session.post(
            path="/component/delete-project",
            json={"project": {"project_id": app_id}},
        ).json()

        return resp["project_id"]

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

    def get_dataset_download_url(self, app_id: str, dataset_id: str) -> str:
        resp = self.__session.get(
            path="/component/get-dataset-download-url",
            params={
                "project_id": app_id,
                "dataset_id": dataset_id,
            },
        ).json()
        return resp["url"]

    def get_dataset(self, app_id: str, dataset_id: str) -> DatasetDict:
        resp = self.__session.get(
            path="/component/get-dataset",
            params={"project_id": app_id, "dataset_id": dataset_id},
        ).json()
        dataset = resp["dataset"]

        return cast(DatasetDict, dataset)

    def get_datasets_for_app(
        self, app_id: str, directory_id: str = _UNSET
    ) -> list[DatasetDict]:
        params = {"project_id": app_id}
        if directory_id != _UNSET:
            params["directory_id"] = directory_id

        resp = self.__session.get(
            path="/component/get-datasets-for-project",
            params=params,
        ).json()
        datasets = resp["datasets"]

        return cast(list[DatasetDict], datasets)

    def get_dataset_multipart_upload_urls(
        self, dataset_id: str, app_id: str, filename: str, file_size: int
    ) -> GetDatasetMultipartUploadUrlsResponse:
        # TODO: Remove api-backwards compatibility once production apis are updated
        # Compatability: Also provide number of parts for backwards compatability
        CHUNK_SIZE = int(50e6)  # noqa: N806 -- 50 MB
        num_parts = (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE
        resp = self.__session.get(
            path="/component/get-dataset-multipart-upload-urls",
            params={
                "dataset_id": dataset_id,
                "project_id": app_id,
                "filename": filename,
                "number_of_parts": num_parts,
                "file_size": file_size,
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

    def get_dataset_log(
        self, app_id: str, dataset_id: str, limit: int = 5
    ) -> list[DatasetLogDict]:
        dataset_log = self.__session.get(
            path="/component/get-dataset-log",
            params={"dataset_id": dataset_id, "project_id": app_id, "limit": limit},
        ).json()["dataset_log"]

        return dataset_log

    def edit_dataset(
        self,
        app_id: str,
        dataset_id: str,
        name: str = _UNSET,
        directory: Directory = _UNSET,
    ) -> str:
        dataset: dict[str, Any] = {
            "project_id": app_id,
            "dataset_id": dataset_id,
        }

        if name != _UNSET:
            dataset["name"] = name
        if directory != _UNSET:
            dataset["directory"] = directory.to_dict()

        resp = self.__session.post(
            path="/component/edit-dataset",
            json={
                "dataset": dataset,
            },
        ).json()

        return resp["dataset_id"]

    def verify_dataset_upload(
        self, app_id: str, dataset_id: str, filename: str
    ) -> None:
        self.__session.get(
            path="/component/verify-dataset-upload",
            params={
                "project_id": app_id,
                "dataset_id": dataset_id,
                "filename": filename,
            },
        )
        return None

    def confirm_dataset_upload(self, app_id: str, dataset_id: str) -> str:
        resp = self.__session.get(
            path="/component/confirm-dataset-upload",
            params={"project_id": app_id, "dataset_id": dataset_id},
        ).json()
        return resp["status"]

    def abort_datset_multipart_upload(
        self, app_id: str, dataset_id: str, filename: str, upload_id: str
    ) -> None:
        self.__session.post(
            path="/component/complete-dataset-multipart-upload",
            json={
                "abort": True,
                "dataset": {
                    "dataset_id": dataset_id,
                    "project_id": app_id,
                    "filename": filename,
                },
                "upload_id": upload_id,
            },
        )
        return None

    def complete_datset_multipart_upload(
        self,
        app_id: str,
        dataset_id: str,
        filename: str,
        upload_id: str,
        etags: dict[int, str],
    ) -> None:
        self.__session.post(
            path="/component/complete-dataset-multipart-upload",
            json={
                "abort": False,
                "dataset": {
                    "dataset_id": dataset_id,
                    "project_id": app_id,
                    "filename": filename,
                },
                "upload_id": upload_id,
                "etags": etags,
            },
        )
        return None

    def delete_dataset(self, app_id: str, dataset_id: str) -> str:
        resp = self.__session.post(
            path="/component/delete-dataset",
            json={"dataset": {"project_id": app_id, "dataset_id": dataset_id}},
        ).json()

        return resp["dataset_id"]

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
        self, app_id: str, directory_id: str = _UNSET
    ) -> list[FlowDict]:
        params = {"project_id": app_id}

        if directory_id != _UNSET:
            params["directory_id"] = directory_id

        flows = self.__session.get(
            path="/component/get-pipelines-for-project",
            params=params,
        ).json()["pipelines"]

        return cast(list[FlowDict], flows)

    def get_flow_log(
        self, app_id: str, flow_id: str, max_count: int
    ) -> list[FlowLogDict]:
        log_dicts = self.__session.get(
            path="/component/get-pipeline-log",
            params={
                "pipeline_id": flow_id,
                "project_id": app_id,
                "limit": max_count,
            },
        ).json()["pipeline_log"]

        return log_dicts

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

        # BE is a bit inconsistent with the response so clean it up
        status = resp["progress"]["status"] if resp["status"] else "IDLE"
        progress = resp["progress"].get("progress")
        message = resp["progress"].get("message")

        return FlowStatusReportDict(
            status=status,
            progress=progress,
            message=message,
        )

    """
    Model APIs
    """

    def create_model(
        self,
        app_id: str,
        name: str,
        directory: Directory | None,
        model_type: ModelType,
        description: str,
    ) -> str:
        directory_dict = (
            cast(dict, directory.to_dict()) if directory is not None else {}
        )

        resp = self.__session.post(
            path="/component/create-model",
            json={
                "model": {
                    "project_id": app_id,
                    "name": name,
                    "directory": directory_dict,
                    "model_type": model_type.model_type,
                    "sub_model_type": model_type.sub_model_type,
                    "description": description,
                }
            },
        ).json()

        return resp["model_id"]

    def get_model(self, app_id: str, model_id: str) -> ModelDict:
        resp = self.__session.get(
            path="/component/get-model",
            params={"project_id": app_id, "model_id": model_id},
        ).json()
        model = resp["model"]
        return cast(ModelDict, model)

    def get_models_for_app(
        self, app_id: str, directory_id: str = _UNSET
    ) -> list[ModelDict]:
        params = {"project_id": app_id}
        if directory_id != _UNSET:
            params["directory_id"] = directory_id

        resp = self.__session.get(
            path="/component/get-models-for-project",
            params=params,
        ).json()
        models = resp["models"]

        return cast(list[ModelDict], models)

    @cache
    def get_model_specs(self) -> list[ModelSpecDict]:
        resp = self.__session.get(
            path="/component/get-model-specs",
        ).json()

        model_specs = resp.values()

        return cast(list[ModelSpecDict], model_specs)

    def edit_model(
        self,
        app_id: str,
        model_id: str,
        name: str = _UNSET,
        directory: Directory = _UNSET,
        description: str = _UNSET,
    ) -> str:
        model: dict[str, Any] = {
            "project_id": app_id,
            "model_id": model_id,
        }

        if name != _UNSET:
            model["name"] = name
        if directory != _UNSET:
            model["directory"] = directory.to_dict()
        if description != _UNSET:
            model["description"] = description

        resp = self.__session.post(
            path="/component/edit-model",
            json={"model": model},
        ).json()

        return resp["model_id"]

    def delete_model(self, app_id: str, model_id: str) -> str:
        resp = self.__session.post(
            path="/component/delete-model",
            json={"model": {"project_id": app_id, "model_id": model_id}},
        ).json()

        return resp["model_id"]

    """
    Model Version APIs
    """

    def get_model_version(self, app_id: str, version_id: str) -> ModelVersionDict:
        resp = self.__session.get(
            path="/component/get-model-version",
            params={"project_id": app_id, "version_id": version_id},
        ).json()
        model_version = resp["model_version"]

        return cast(ModelVersionDict, model_version)

    def get_model_versions(self, app_id: str, model_id: str) -> list[ModelVersionDict]:
        resp = self.__session.get(
            path="/component/get-model-versions",
            params={"project_id": app_id, "model_id": model_id},
        ).json()
        model_versions = resp["versions"]

        return cast(list[ModelVersionDict], model_versions)

    """
    Directory APIs
    """

    def create_dataset_directory(
        self, app_id: str, name: str, parent: Directory | None = None
    ) -> str:
        parent_id = parent.directory_id if parent else ""

        resp = self.__session.post(
            path="/component/create-dataset-directory",
            json={
                "directory": {
                    "name": name,
                    "project_id": app_id,
                    "parent_id": parent_id,
                }
            },
        ).json()

        return resp["directory_id"]

    def get_dataset_directory(self, app_id: str, directory_id: str) -> DirectoryDict:
        directory = self.__session.get(
            path="/component/get-dataset-directory",
            params={"project_id": app_id, "directory_id": directory_id},
        ).json()["directory"]

        return cast(DirectoryDict, directory)

    def get_dataset_directories_for_app(
        self, app_id: str, parent: Directory = _UNSET
    ) -> list[DirectoryDict]:
        params = {"project_id": app_id}
        if parent != _UNSET:
            params["directory_id"] = parent.directory_id

        resp = self.__session.get(
            path="/component/get-dataset-directories-for-project",
            params=params,
        ).json()
        directories = resp["directories"]

        return cast(list[DirectoryDict], directories)

    def create_flow_directory(
        self, app_id: str, name: str, parent: Directory | None = None
    ) -> str:
        parent_id = parent.directory_id if parent else ""

        resp = self.__session.post(
            path="/component/create-pipeline-directory",
            json={
                "directory": {
                    "name": name,
                    "project_id": app_id,
                    "parent_id": parent_id,
                }
            },
        ).json()

        return resp["directory_id"]

    def get_flow_directory(self, app_id: str, directory_id: str) -> DirectoryDict:
        directory = self.__session.get(
            path="/component/get-pipeline-directory",
            params={"project_id": app_id, "directory_id": directory_id},
        ).json()["directory"]

        return cast(DirectoryDict, directory)

    def get_flow_directories_for_app(
        self, app_id: str, parent: Directory = _UNSET
    ) -> list[DirectoryDict]:
        params = {"project_id": app_id}
        if parent != _UNSET:
            params["directory_id"] = parent.directory_id

        resp = self.__session.get(
            path="/component/get-pipeline-directories-for-project",
            params=params,
        ).json()

        directories = resp["directories"]
        return cast(list[DirectoryDict], directories)

    def create_model_directory(
        self, app_id: str, name: str, parent: Directory | None = None
    ) -> str:
        parent_id = parent.directory_id if parent else ""

        resp = self.__session.post(
            path="/component/create-model-directory",
            json={
                "directory": {
                    "name": name,
                    "project_id": app_id,
                    "parent_id": parent_id,
                }
            },
        ).json()

        return resp["directory_id"]

    def get_model_directory(self, app_id: str, directory_id: str) -> DirectoryDict:
        directory = self.__session.get(
            path="/component/get-model-directory",
            params={"project_id": app_id, "directory_id": directory_id},
        ).json()["directory"]

        return cast(DirectoryDict, directory)

    def get_model_directories_for_app(
        self, app_id: str, parent: Directory = _UNSET
    ) -> list[DirectoryDict]:
        params = {"project_id": app_id}
        if parent != _UNSET:
            params["directory_id"] = parent.directory_id

        resp = self.__session.get(
            path="/component/get-model-directories-for-project",
            params=params,
        ).json()

        directories = resp["directories"]
        return cast(list[DirectoryDict], directories)
