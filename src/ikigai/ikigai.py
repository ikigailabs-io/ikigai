# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

import requests
from pydantic import AnyUrl, EmailStr, Field
from pydantic.dataclasses import dataclass

from ikigai import components
from ikigai.client import Client
from ikigai.utils.named_mapping import NamedMapping


@dataclass
class Ikigai:
    user_email: EmailStr
    api_key: str = Field(repr=False)
    base_url: AnyUrl = Field(default=AnyUrl("https://api.ikigailabs.io"))
    __client: Client = Field(init=False)

    def __post_init__(self) -> None:
        session = requests.Session()
        session.headers.update({"user": self.user_email, "api-key": self.api_key})
        self.__client = Client(base_url=str(self.base_url), session=session)

    def apps(self) -> NamedMapping[components.App]:
        resp = self.__client.get(
            path="/component/get-projects-for-user", params={"fetch_all": True}
        ).json()
        apps = {
            app.app_id: app
            for app in (
                components.App.from_dict(data=app_dict, client=self.__client)
                for app_dict in resp["projects"]
            )
        }

        return NamedMapping(apps)

    @property
    def app(self) -> components.AppBuilder:
        return components.AppBuilder(client=self.__client)

    def directories(self) -> NamedMapping[components.AppDirectory]:
        resp = self.__client.get("/component/get-project-directories-for-user").json()
        directories = {
            directory.directory_id: directory
            for directory in (
                components.AppDirectory.from_dict(
                    data=directory_dict, client=self.__client
                )
                for directory_dict in resp["directories"]
            )
        }

        return NamedMapping(directories)
