# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from ikigai.client.session import Session
from ikigai.utils.compatibility import Self


class FlowBuilder:
    def __init__(self, session: Session, app_id: str) -> None:
        raise NotImplementedError()


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
