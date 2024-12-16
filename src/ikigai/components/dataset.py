# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import sys
from enum import Enum
from datetime import datetime
from typing import Any, Optional
import pandas as pd
from pydantic import BaseModel, Field
from ikigai.client.session import Session
from ikigai.utils.protocols import Directory

# Multiple python version compatible import for Self
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


class DatasetBuilder:
    _app_id: str
    _name: str
    _data: Optional[pd.DataFrame]
    _directory: dict[str, str]
    __session: Session

    def __init__(self, session: Session, app_id: str) -> None:
        self.__session = session
        self._app_id = app_id
        self._name = ""
        self._data = None
        self._directory = dict()

    def new(self, name: str) -> Self:
        self._name = name
        return self

    def data(self, df: pd.DataFrame) -> Self:
        self._data = df
        return self

    def directory(self, directory: Directory) -> Self:
        self._directory = {
            "directory_id": directory.directory_id,
            "type": directory.type,
        }
        return self

    def build(self) -> Dataset:
        resp = self.__session.post(
            path="/component/create-dataset",
            json={
                "dataset": {
                    "project_id": self._app_id,
                    "name": self._name,
                    "directory": self._directory,
                },
            },
        ).json()
        dataset_id = resp["dataset_id"]
        resp = self.__session.get(
            path="/component/get-dataset", params={"dataset_id": dataset_id}
        ).json()
        dataset = Dataset.from_dict(data=resp["dataset"], session=self.__session)
        return dataset


class DataType(Enum):
    NUMERIC = "NUMERIC"
    TEXT = "TEXT"
    CATEGORICAL = "CATEGORICAL"
    TIME = "TIME"


class ColumnDataType(BaseModel):
    data_type: DataType
    data_formats: dict[str, list[str]]


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
    __session: Session

    @classmethod
    def from_dict(cls, data: dict, session: Session) -> Self:
        self = cls.model_validate(data)
        self.__session = session
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
        self.__session.post(
            path="/component/delete-dataset",
            json={"dataset": {"dataset_id": self.dataset_id}},
        )
        return None

    def rename(self, name: str) -> Self:
        _ = self.__session.post(
            path="/component/edit-dataset",
            json={
                "dataset": {
                    "project_id": self.app_id,
                    "dataset_id": self.dataset_id,
                    "name": name,
                }
            },
        )
        # TODO: handle error case, currently it is a raise NotImplemented from Session
        self.name = name
        return self

    def describe(self) -> dict:
        response: dict[str, Any] = self.__session.get(
            path="/component/get-dataset",
            params={"dataset_id": self.dataset_id},
        ).json()

        return response
