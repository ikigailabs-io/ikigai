# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from pydantic import AnyUrl, EmailStr, Field
from pydantic.dataclasses import dataclass

from ikigai import components
from ikigai.client import Client
from ikigai.utils.component_browser import ComponentBrowser
from ikigai.utils.named_mapping import NamedMapping


@dataclass
class Ikigai:
    user_email: EmailStr
    api_key: str = Field(repr=False)
    base_url: AnyUrl = Field(default=AnyUrl("https://api.ikigailabs.io"))
    __client: Client = Field(init=False)

    def __post_init__(self) -> None:
        self.__client = Client(
            user_email=self.user_email, api_key=self.api_key, base_url=self.base_url
        )

    @property
    def apps(self) -> ComponentBrowser[components.App]:
        return components.AppBrowser(client=self.__client)

    @property
    def app(self) -> components.AppBuilder:
        return components.AppBuilder(client=self.__client)

    def directories(self) -> NamedMapping[components.AppDirectory]:
        directory_dicts = self.__client.component.get_app_directories_for_user()
        directories = {
            directory.directory_id: directory
            for directory in (
                components.AppDirectory.from_dict(
                    data=directory_dict, client=self.__client
                )
                for directory_dict in directory_dicts
            )
        }

        return NamedMapping(directories)

    @property
    def builder(self) -> components.FlowDefinitionBuilder:
        return components.FlowDefinitionBuilder()

    @property
    def facet_types(self) -> components.FacetTypes:
        return components.FacetTypes.from_dict(
            data=self.__client.component.get_facet_specs()
        )

    @property
    def model_types(self) -> components.ModelTypes:
        return components.ModelTypes.from_list(
            data=self.__client.component.get_model_specs()
        )
