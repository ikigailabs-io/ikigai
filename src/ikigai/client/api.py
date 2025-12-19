# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import InitVar
from functools import cache
from typing import Any, cast

from pydantic import Field
from pydantic.dataclasses import dataclass

from ikigai.client.session import Session
from ikigai.typing.api import (
    GetComponentsForProjectResponse,
    GetDatasetMultipartUploadUrlsResponse,
    RunVariablesRequest,
)
from ikigai.typing.protocol import (
    AppDict,
    DatasetDict,
    DatasetLogDict,
    Directory,
    FlowDefinitionDict,
    FlowDict,
    FlowLogDict,
    FlowStatusReportDict,
    ModelDict,
    ModelSpecDict,
    ModelType,
    ModelVersionDict,
    NamedDirectoryDict,
)
from ikigai.typing.protocol.flow import FacetSpecsDict
from ikigai.utils.missing import MISSING, MissingType

logger = logging.getLogger("ikigai.client.api")


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

    def get_app_by_name(self, name: str) -> AppDict:
        app_dict = self.__session.get(
            path="/component/get-project", params={"name": name}
        ).json()["project"]

        return cast(AppDict, app_dict)

    def get_apps_for_user(
        self, directory_id: str | MissingType = MISSING
    ) -> list[AppDict]:
        params: dict[str, Any] = {"fetch_all": directory_id is MISSING}
        if directory_id is not MISSING:
            params["directory_id"] = directory_id

        response: dict = self.__session.get(
            path="/component/get-projects-for-user", params=params
        ).json()

        app_dicts = response["projects"]
        if warning := response["limit_warning"]:
            logger.warning(warning)

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
        name: str | MissingType = MISSING,
        directory: Directory | MissingType = MISSING,
        description: str | MissingType = MISSING,
    ) -> str:
        app: dict[str, Any] = {"project_id": app_id}

        if name is not MISSING:
            app["name"] = name
        if directory is not MISSING:
            app["directory"] = directory.to_dict()
        if description is not MISSING:
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

    def get_dataset_by_name(self, app_id: str, name: str) -> DatasetDict:
        resp = self.__session.get(
            path="/component/get-dataset",
            params={"project_id": app_id, "name": name},
        ).json()
        dataset = resp["dataset"]

        return cast(DatasetDict, dataset)

    def get_datasets_for_app(
        self, app_id: str, directory_id: str | MissingType = MISSING
    ) -> list[DatasetDict]:
        params = {"project_id": app_id, "fetch_all": directory_id is MISSING}
        if directory_id is not MISSING:
            params["directory_id"] = directory_id

        response = self.__session.get(
            path="/component/get-datasets-for-project",
            params=params,
        ).json()
        datasets = response["datasets"]
        if warning := response["limit_warning"]:
            logger.warning(warning)

        return cast(list[DatasetDict], datasets)

    def get_dataset_multipart_upload_urls(
        self, dataset_id: str, app_id: str, filename: str, file_size: int
    ) -> GetDatasetMultipartUploadUrlsResponse:
        resp = self.__session.get(
            path="/component/get-dataset-multipart-upload-urls",
            params={
                "dataset_id": dataset_id,
                "project_id": app_id,
                "filename": filename,
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

        return cast(list[DatasetLogDict], dataset_log)

    def edit_dataset(
        self,
        app_id: str,
        dataset_id: str,
        name: str | MissingType = MISSING,
        directory: Directory | MissingType = MISSING,
    ) -> str:
        dataset: dict[str, Any] = {
            "project_id": app_id,
            "dataset_id": dataset_id,
        }

        if name is not MISSING:
            dataset["name"] = name
        if directory is not MISSING:
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
        high_volume_preference: bool,
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
                    "high_volume_preference": high_volume_preference,
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

    def get_flow_by_name(self, app_id: str, name: str) -> FlowDict:
        flow = self.__session.get(
            path="/component/get-pipeline", params={"project_id": app_id, "name": name}
        ).json()["pipeline"]

        return cast(FlowDict, flow)

    def get_flows_for_app(
        self, app_id: str, directory_id: str | MissingType = MISSING
    ) -> list[FlowDict]:
        params = {"project_id": app_id, "fetch_all": directory_id is MISSING}
        if directory_id is not MISSING:
            params["directory_id"] = directory_id

        response = self.__session.get(
            path="/component/get-pipelines-for-project",
            params=params,
        ).json()

        flows = response["pipelines"]
        if warning := response["limit_warning"]:
            logger.warning(warning)

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

        return cast(list[FlowLogDict], log_dicts)

    def edit_flow(
        self,
        app_id: str,
        flow_id: str,
        name: str | None = None,
        directory: Directory | None = None,
        high_volume_preference: bool | None = None,
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
        if high_volume_preference is not None:
            pipeline["high_volume_preference"] = high_volume_preference
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

    def run_flow(
        self, app_id: str, flow_id: str, variables: RunVariablesRequest
    ) -> str:
        payload: dict[str, Mapping] = {
            "pipeline": {"project_id": app_id, "pipeline_id": flow_id}
        }
        if variables:
            payload["variables"] = variables

        resp = self.__session.post(
            path="/component/run-pipeline",
            json=payload,
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
        model = self.__session.get(
            path="/component/get-model",
            params={"project_id": app_id, "model_id": model_id},
        ).json()["model"]

        return cast(ModelDict, model)

    def get_model_by_name(self, app_id: str, name: str) -> ModelDict:
        model = self.__session.get(
            path="/component/get-model",
            params={"project_id": app_id, "name": name},
        ).json()["model"]

        return cast(ModelDict, model)

    def get_models_for_app(
        self, app_id: str, directory_id: str | MissingType = MISSING
    ) -> list[ModelDict]:
        params = {"project_id": app_id, "fetch_all": directory_id is MISSING}
        if directory_id is not MISSING:
            params["directory_id"] = directory_id

        response = self.__session.get(
            path="/component/get-models-for-project",
            params=params,
        ).json()

        models = response["models"]
        if warning := response["limit_warning"]:
            logger.warning(warning)

        return cast(list[ModelDict], models)

    def edit_model(
        self,
        app_id: str,
        model_id: str,
        name: str | MissingType = MISSING,
        directory: Directory | MissingType = MISSING,
        description: str | MissingType = MISSING,
    ) -> str:
        model: dict[str, Any] = {
            "project_id": app_id,
            "model_id": model_id,
        }

        if name is not MISSING:
            model["name"] = name
        if directory is not MISSING:
            model["directory"] = directory.to_dict()
        if description is not MISSING:
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

    def create_app_directory(self, name: str, parent: Directory | None = None) -> str:
        parent_id = parent.directory_id if parent else ""

        resp = self.__session.post(
            path="/component/create-project-directory",
            json={
                "directory": {
                    "name": name,
                    "parent_id": parent_id,
                }
            },
        ).json()

        return resp["directory_id"]

    def get_app_directory(self, directory_id: str) -> NamedDirectoryDict:
        directory = self.__session.get(
            path="/component/get-project-directory",
            params={"directory_id": directory_id},
        ).json()["directory"]

        return cast(NamedDirectoryDict, directory)

    def get_app_directories_for_user(
        self, directory_id: str | MissingType = MISSING
    ) -> list[NamedDirectoryDict]:
        """
        NOTE: Platform should add a fetch_all field to distinguish between root
            directory and no directory, in anticipation of this we just pass it in.
        """
        params: dict[str, Any] = {"fetch_all": directory_id is MISSING}
        if directory_id is not MISSING:
            params["directory_id"] = directory_id

        directory_dicts = self.__session.get(
            path="/component/get-project-directories-for-user",
            params=params,
        ).json()["directories"]

        return cast(list[NamedDirectoryDict], directory_dicts)

    def delete_app_directory(self, directory_id: str) -> str:
        resp = self.__session.post(
            path="/component/delete-project-directory",
            json={"directory": {"directory_id": directory_id}},
        ).json()

        return resp["directory_id"]

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

    def get_dataset_directory(
        self, app_id: str, directory_id: str
    ) -> NamedDirectoryDict:
        directory = self.__session.get(
            path="/component/get-dataset-directory",
            params={"project_id": app_id, "directory_id": directory_id},
        ).json()["directory"]

        return cast(NamedDirectoryDict, directory)

    def get_dataset_directories_for_app(
        self, app_id: str, parent: Directory | MissingType = MISSING
    ) -> list[NamedDirectoryDict]:
        params = {"project_id": app_id}
        if parent is not MISSING:
            params["directory_id"] = parent.directory_id

        resp = self.__session.get(
            path="/component/get-dataset-directories-for-project",
            params=params,
        ).json()
        directories = resp["directories"]

        return cast(list[NamedDirectoryDict], directories)

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

    def get_flow_directory(self, app_id: str, directory_id: str) -> NamedDirectoryDict:
        directory = self.__session.get(
            path="/component/get-pipeline-directory",
            params={"project_id": app_id, "directory_id": directory_id},
        ).json()["directory"]

        return cast(NamedDirectoryDict, directory)

    def get_flow_directories_for_app(
        self, app_id: str, parent: Directory | MissingType = MISSING
    ) -> list[NamedDirectoryDict]:
        params = {"project_id": app_id}
        if parent is not MISSING:
            params["directory_id"] = parent.directory_id

        resp = self.__session.get(
            path="/component/get-pipeline-directories-for-project",
            params=params,
        ).json()

        directories = resp["directories"]
        return cast(list[NamedDirectoryDict], directories)

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

    def get_model_directory(self, app_id: str, directory_id: str) -> NamedDirectoryDict:
        directory = self.__session.get(
            path="/component/get-model-directory",
            params={"project_id": app_id, "directory_id": directory_id},
        ).json()["directory"]

        return cast(NamedDirectoryDict, directory)

    def get_model_directories_for_app(
        self, app_id: str, parent: Directory | MissingType = MISSING
    ) -> list[NamedDirectoryDict]:
        params = {"project_id": app_id}
        if parent is not MISSING:
            params["directory_id"] = parent.directory_id

        resp = self.__session.get(
            path="/component/get-model-directories-for-project",
            params=params,
        ).json()

        directories = resp["directories"]
        return cast(list[NamedDirectoryDict], directories)

    """
    Spec APIs
    """

    @cache
    def get_facet_specs(self) -> FacetSpecsDict:
        resp = self.__session.get(
            path="/component/get-facet-specs",
        ).json()

        return cast(FacetSpecsDict, resp)

    @cache
    def get_model_specs(self) -> list[ModelSpecDict]:
        resp = self.__session.get(
            path="/component/get-model-specs",
        ).json()

        model_specs = resp.values()

        return cast(list[ModelSpecDict], model_specs)


@dataclass
class SearchAPI:
    # Init only vars
    session: InitVar[Session]

    __session: Session = Field(init=False)

    def __post_init__(self, session: Session) -> None:
        self.__session = session

    def heartbeat(self) -> None:
        self.__session.get(path="/search/heartbeat", suppress_logging=True)
        return None

    """
    Search APIs
    """

    def search_projects_for_user(self, query: str) -> list[AppDict]:
        response = self.__session.get(
            path="/search/search-projects-for-user", params={"query": query}
        ).json()

        app_dicts = response["projects"]
        if warning := response["limit_warning"]:
            logger.warning(warning)

        return cast(list[AppDict], app_dicts)

    def search_datasets_for_project(self, app_id: str, query: str) -> list[DatasetDict]:
        response = self.__session.get(
            path="/search/search-datasets-for-project",
            params={"project_id": app_id, "query": query},
        ).json()

        dataset_dict = response["datasets"]
        if warning := response["limit_warning"]:
            logger.warning(warning)

        return cast(list[DatasetDict], dataset_dict)

    def search_flows_for_project(self, app_id: str, query: str) -> list[FlowDict]:
        response = self.__session.get(
            path="/search/search-pipelines-for-project",
            params={"project_id": app_id, "query": query},
        ).json()

        flow_dict = response["pipelines"]
        if warning := response["limit_warning"]:
            logger.warning(warning)

        return cast(list[FlowDict], flow_dict)

    def search_models_for_project(self, app_id: str, query: str) -> list[ModelDict]:
        response = self.__session.get(
            path="/search/search-models-for-project",
            params={"project_id": app_id, "query": query},
        ).json()

        model_dict = response["models"]
        if warning := response["limit_warning"]:
            logger.warning(warning)

        return cast(list[ModelDict], model_dict)
