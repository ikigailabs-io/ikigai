# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations
import sys
from datetime import datetime
from pydantic import BaseModel, EmailStr
from ikigai.client.session import Session

# Multiple python version compatible import for Self
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


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
