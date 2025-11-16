# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import InitVar

from pydantic import AnyUrl, EmailStr, Field
from pydantic.dataclasses import dataclass

from ikigai import components
from ikigai.client import Client
from ikigai.utils.compatibility import deprecated
from ikigai.utils.component_browser import ComponentBrowser
from ikigai.utils.config import SSLConfig
from ikigai.utils.missing import MISSING, MissingType
from ikigai.utils.named_mapping import NamedMapping


@dataclass
class Ikigai:
    """
    Main Ikigai class to interact with the Ikigai platform

    Parameters
    ----------
    user_email: str
        Email of the user

    api_key: str
        API key for authentication

    base_url: str
        Base URL of the Ikigai API endpoints, by default it is set to:
        "https://api.ikigailabs.io"

    ssl: bool or str or tuple
        SSL configuration see `ikigai.utils.config` for more details
        Set to `False` to disable SSL verification (unsafe) or provide
        custom SSL certificate by providing path to certificate (.pem) file or
        a tuple of (certificate, key).
    """

    user_email: EmailStr
    api_key: InitVar[str]
    base_url: AnyUrl = Field(default=AnyUrl("https://api.ikigailabs.io"))
    ssl: InitVar[SSLConfig | MissingType] = MISSING
    __client: Client = Field(init=False)

    def __post_init__(
        self, api_key: str, ssl: SSLConfig | MissingType = MISSING
    ) -> None:
        if ssl is MISSING:
            ssl = True
        self.__client = Client(
            user_email=self.user_email, api_key=api_key, base_url=self.base_url, ssl=ssl
        )

    @property
    def apps(self) -> ComponentBrowser[components.App]:
        """
        Browser object to interact with Apps

        It helps to list, get and search for Apps accessible to the user in the
        Ikigai platform.

        Returns
        -------
        ComponentBrowser[components.App]
            Browser for Apps
        """
        return components.AppBrowser(client=self.__client)

    @property
    def app(self) -> components.AppBuilder:
        """
        Builder to create a new App

        Returns
        -------
        components.AppBuilder
            A new App builder object
        """
        return components.AppBuilder(client=self.__client)

    @deprecated("Use ikigai.app_directories() instead")
    def directories(self) -> NamedMapping[components.AppDirectory]:
        return self.app_directories()

    def app_directories(self) -> NamedMapping[components.AppDirectory]:
        """
        Get all App Directories for the user

        Returns
        -------
        NamedMapping[components.AppDirectory]
            Mapping of names to Directories
        """
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
    def app_directory(self) -> components.AppDirectoryBuilder:
        """
        Builder to create a new App Directory

        Returns
        -------
        components.AppDirectoryBuilder
            A new App Directory builder object
        """
        return components.AppDirectoryBuilder(client=self.__client)

    @property
    def builder(self) -> components.FlowDefinitionBuilder:
        """
        Builder to create a new Flow Definition

        Returns
        -------
        components.FlowDefinitionBuilder
            A new Flow Definition builder object
        """
        return components.FlowDefinitionBuilder()

    @property
    def facet_types(self) -> components.FacetTypes:
        """
        Available facet types in the Ikigai platform

        Returns
        -------
        components.FacetTypes
            Available facet types
        """
        return components.FacetTypes.from_dict(
            data=self.__client.component.get_facet_specs()
        )

    @property
    def model_types(self) -> components.ModelTypes:
        """
        Available model types in the Ikigai platform

        Returns
        -------
        components.ModelTypes
            Available model types
        """
        return components.ModelTypes.from_list(
            data=self.__client.component.get_model_specs()
        )
