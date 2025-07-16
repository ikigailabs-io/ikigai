# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import io
import logging
import math
import time
from collections.abc import Mapping
from datetime import datetime
from enum import Enum
from http import HTTPStatus
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from pydantic import BaseModel, Field

from ikigai.client import Client
from ikigai.typing.protocol import (
    Directory,
    DirectoryType,
    NamedDirectoryDict,
)
from ikigai.utils.compatibility import Self
from ikigai.utils.named_mapping import NamedMapping

logger = logging.getLogger("ikigai.components")


def __upload_data(
    client: Client,
    app_id: str,
    dataset_id: str,
    data: bytes,
    filename: str,
) -> None:
    file_size = len(data)
    multipart_upload_metadata = client.component.get_dataset_multipart_upload_urls(
        dataset_id=dataset_id,
        app_id=app_id,
        filename=filename,
        file_size=file_size,
    )

    content_type = multipart_upload_metadata["content_type"]
    upload_urls = multipart_upload_metadata["urls"]
    upload_id = multipart_upload_metadata["upload_id"]

    num_chunks = len(upload_urls)
    chunk_size = math.ceil(file_size / num_chunks)

    etags: dict[int, str] = {}
    try:
        with requests.session() as request:
            request.headers.update(
                {"Content-Type": content_type, "Cache-Control": "no-cache"}
            )
            for idx, (chunk_idx, upload_url) in enumerate(sorted(upload_urls.items())):
                chunk_start, chunk_end = (idx * chunk_size, (idx + 1) * chunk_size)
                chunk = data[chunk_start : min(chunk_end, file_size)]
                resp = request.put(url=upload_url, data=chunk)
                assert resp.status_code == HTTPStatus.OK

                # Get etags from response header
                etags[chunk_idx] = resp.headers["ETag"]
    except Exception:
        client.component.abort_datset_multipart_upload(
            app_id=app_id,
            dataset_id=dataset_id,
            filename=filename,
            upload_id=upload_id,
        )
        raise

    # Complete Dataset upload
    client.component.complete_datset_multipart_upload(
        app_id=app_id,
        dataset_id=dataset_id,
        filename=filename,
        upload_id=upload_id,
        etags=etags,
    )


def _upload_data(
    client: Client, app_id: str, dataset_id: str, name: str, data: bytes
) -> None:
    assert data is not None
    filename = f"{name}.csv"

    __upload_data(
        client=client,
        app_id=app_id,
        dataset_id=dataset_id,
        data=data,
        filename=filename,
    )

    upload_completion_time = time.time()
    client.component.verify_dataset_upload(
        app_id=app_id, dataset_id=dataset_id, filename=filename
    )

    dataset_status: str = "RUNNING"
    while dataset_status == "RUNNING":
        # Block thread while dataset is still being processed
        time.sleep(0.25)
        dataset_status = client.component.confirm_dataset_upload(
            app_id=app_id, dataset_id=dataset_id
        )

    if dataset_status != "SUCCESS":
        error_msg = f"Dataset upload failed, upload ended with status {dataset_status}"
        raise RuntimeError(error_msg)

    dataset_logs = client.component.get_dataset_log(
        app_id=app_id, dataset_id=dataset_id, limit=5
    )
    dataset_verified = [
        log
        for log in dataset_logs
        if log["status"] == "SUCCESS"
        and int(log["timestamp"]) > upload_completion_time
        and log["job_type"] == "UPLOAD_DATASET"
    ]
    if not dataset_verified:
        # TODO: Improve Error
        error_msg = "Dataset failed to verify"
        raise RuntimeError(error_msg, dataset_logs)


class DatasetBuilder:
    _app_id: str
    _name: str
    _data: bytes | None
    _directory: Directory | None
    __client: Client

    def __init__(self, client: Client, app_id: str) -> None:
        self.__client = client
        self._app_id = app_id
        self._name = ""
        self._data = None
        self._directory = None

    def new(self, name: str) -> Self:
        self._name = name
        return self

    def df(self, data: pd.DataFrame) -> Self:
        buffer = io.BytesIO()
        data.to_csv(buffer, index_label=False, index=False)
        self._data = buffer.getvalue()
        return self

    def csv(self, file: Path | str) -> Self:
        if isinstance(file, str):
            file = Path(file)
        with file.open("rb") as fp:
            self._data = fp.read()
        return self

    def directory(self, directory: Directory) -> Self:
        self._directory = directory
        return self

    def build(self) -> Dataset:
        if self._data is None:
            error_msg = "Dataset is empty"
            raise ValueError(error_msg)

        dataset_id = self.__client.component.create_dataset(
            app_id=self._app_id, name=self._name, directory=self._directory
        )

        try:
            _upload_data(
                client=self.__client,
                app_id=self._app_id,
                dataset_id=dataset_id,
                name=self._name,
                data=self._data,
            )
        except Exception:
            # Delete created record and re-raise
            self.__client.component.delete_dataset(
                app_id=self._app_id, dataset_id=dataset_id
            )
            raise

        # Populate Dataset object
        dataset_dict = self.__client.component.get_dataset(
            app_id=self._app_id, dataset_id=dataset_id
        )
        dataset = Dataset.from_dict(data=dataset_dict, client=self.__client)
        return dataset


class DataType(str, Enum):
    NUMERIC = "NUMERIC"
    TEXT = "TEXT"
    CATEGORICAL = "CATEGORICAL"
    TIME = "TIME"


class ColumnDataType(BaseModel):
    data_type: DataType
    data_formats: dict[str, str]


class Dataset(BaseModel):
    app_id: str = Field(validation_alias="project_id")
    dataset_id: str
    name: str
    filename: str
    file_extension: str
    data_types: dict[str, ColumnDataType]
    size: int
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
            "dataset_id": self.dataset_id,
            "name": self.name,
            "filename": self.filename,
            "file_extension": self.file_extension,
            "data_types": self.data_types,
            "size": self.size,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
        }

    def delete(self) -> None:
        self.__client.component.delete_dataset(
            app_id=self.app_id, dataset_id=self.dataset_id
        )
        return None

    def rename(self, name: str) -> Self:
        _ = self.__client.component.edit_dataset(
            app_id=self.app_id, dataset_id=self.dataset_id, name=name
        )
        # TODO: handle error case, currently it is a raise NotImplemented from Session
        self.name = name
        return self

    def move(self, directory: Directory) -> Self:
        _ = self.__client.component.edit_dataset(
            app_id=self.app_id,
            dataset_id=self.dataset_id,
            directory=directory,
        )
        return self

    def df(self, **parser_options) -> pd.DataFrame:
        download_url = self.__client.component.get_dataset_download_url(
            app_id=self.app_id,
            dataset_id=self.dataset_id,
        )
        return pd.read_csv(download_url, **parser_options)

    def edit_data(self, data: pd.DataFrame) -> None:
        buffer = io.BytesIO()
        data.to_csv(buffer, index_label=False, index=False)

        _upload_data(
            client=self.__client,
            app_id=self.app_id,
            dataset_id=self.dataset_id,
            name=self.name,
            data=buffer.getvalue(),
        )

    def describe(self) -> Mapping[str, Any]:
        dataset = self.__client.component.get_dataset(
            app_id=self.app_id, dataset_id=self.dataset_id
        )
        return dataset


class DatasetDirectoryBuilder:
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

    def build(self) -> DatasetDirectory:
        directory_id = self.__client.component.create_dataset_directory(
            app_id=self._app_id, name=self._name, parent=self._parent
        )
        directory_dict = self.__client.component.get_dataset_directory(
            app_id=self._app_id, directory_id=directory_id
        )

        directory = DatasetDirectory.from_dict(
            data=directory_dict, client=self.__client
        )
        return directory


class DatasetDirectory(BaseModel):
    app_id: str = Field(validation_alias="project_id")
    directory_id: str
    name: str
    __client: Client

    @property
    def type(self) -> DirectoryType:
        return DirectoryType.DATASET

    @classmethod
    def from_dict(cls, data: Mapping[str, Any], client: Client) -> Self:
        logger.debug("Creating a %s from %s", cls.__name__, data)
        self = cls.model_validate(data)
        self.__client = client
        return self

    def to_dict(self) -> NamedDirectoryDict:
        return {"directory_id": self.directory_id, "type": self.type, "name": self.name}

    def directories(self) -> NamedMapping[Self]:
        directory_dicts = self.__client.component.get_dataset_directories_for_app(
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

    def datasets(self) -> NamedMapping[Dataset]:
        dataset_dicts = self.__client.component.get_datasets_for_app(
            app_id=self.app_id,
            directory_id=self.directory_id,
        )
        datasets = {
            dataset.dataset_id: dataset
            for dataset in (
                Dataset.from_dict(data=dataset_dict, client=self.__client)
                for dataset_dict in dataset_dicts
            )
        }

        return NamedMapping(datasets)
