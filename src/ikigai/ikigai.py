# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

import requests
from pydantic import AnyUrl, EmailStr, Field
from pydantic.dataclasses import dataclass

from ikigai import components
from ikigai.client.session import Session
from ikigai.utils.named_mapping import NamedMapping


@dataclass
class Ikigai:
    user_email: EmailStr
    api_key: str = Field(repr=False)
    base_url: AnyUrl = Field(default=AnyUrl("https://api.ikigailabs.io"))
    __session: Session = Field(init=False)

    def __post_init__(self) -> None:
        session = requests.Session()
        session.headers.update({"user": self.user_email, "api-key": self.api_key})
        self.__session = Session(base_url=str(self.base_url), session=session)

    def apps(self) -> NamedMapping[components.App]:
        resp = self.__session.get("/component/get-projects-for-user").json()
        apps = {
            app.app_id: app
            for app in (
                components.App.from_dict(data=app_dict, session=self.__session)
                for app_dict in resp["projects"]
            )
        }

        return NamedMapping(apps)

    @property
    def app(self) -> components.AppBuilder:
        return components.AppBuilder(session=self.__session)
