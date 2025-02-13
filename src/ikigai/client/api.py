# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import InitVar
from typing import Any

from pydantic import Field
from pydantic.dataclasses import dataclass

from ikigai.client.session import Session
from ikigai.typing.api import GetDatasetMultipartUploadUrlsResponse

_UNSET: Any = object()


@dataclass
class ComponentAPI:
    # Init only vars
    session: InitVar[Session]

    __session: Session = Field(init=False)

    def __post_init__(self, session: Session) -> None:
        self.__session = session

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

    def get_project_directories_for_user(
        self, directory_id: str = _UNSET
    ) -> list[dict]:
        if directory_id == _UNSET:
            directory_id = ""

        return self.__session.get(
            path="/component/get-project-directories-for-user",
            params={"directory_id": directory_id},
        ).json()["directories"]

    def get_projects_for_user(self, directory_id: str = _UNSET) -> list[dict]:
        fetch_all = directory_id == _UNSET
        if directory_id == _UNSET:
            directory_id = ""

        return self.__session.get(
            path="/component/get-projects-for-user",
            params={"fetch_all": fetch_all, "directory_id": directory_id},
        ).json()["projects"]
