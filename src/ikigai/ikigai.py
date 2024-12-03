# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

import requests
from pydantic import EmailStr, AnyUrl, Field
from pydantic.dataclasses import dataclass
from ikigai import components
from ikigai.client.session import Session


@dataclass
class Ikigai:
    user_email: EmailStr
    api_key: str
    base_url: AnyUrl = Field(default=AnyUrl("https://api.ikigailabs.io"))
    __session: Session = Field(init=False)

    def __post_init__(self) -> None:
        session = requests.Session()
        session.headers.update({"user": self.user_email, "api-key": self.api_key})
        self.__session = Session(base_url=str(self.base_url), session=session)

    def projects(self) -> list[components.Project]:
        resp = self.__session.get("/component/get-projects-for-user").json()
        projects = [
            components.Project.from_dict(data=project_dict, session=self.__session)
            for project_dict in resp["projects"]
        ]

        return projects
