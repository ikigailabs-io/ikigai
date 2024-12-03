# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations
from datetime import datetime
from typing import Self
from pydantic import BaseModel, EmailStr
from ikigai.client.session import Session


class Project(BaseModel):
    project_id: str
    name: str
    owner: EmailStr
    description: str
    created_at: datetime
    modified_at: datetime
    last_used_at: datetime
    __session: Session

    @classmethod
    def from_dict(cls, data: dict, session: Session) -> Self:
        self = cls.model_validate(data)
        self.__session = session
        return self
