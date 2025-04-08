# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from dataclasses import InitVar
from http import HTTPStatus
from typing import Any

import requests
from pydantic import AnyUrl, ConfigDict, EmailStr, Field
from pydantic.dataclasses import dataclass
from requests import Response

from ikigai.utils.compatibility import HTTPMethod

logger = logging.getLogger("ikigai.client")


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Session:
    # Init only vars
    user_email: InitVar[EmailStr]
    api_key: InitVar[str]

    base_url: AnyUrl
    __session: requests.Session = Field(init=False)

    def __post_init__(self, user_email: EmailStr, api_key: str) -> None:
        self.__session = requests.Session()
        self.__session.headers.update({"user": user_email, "api-key": api_key})

    def request(
        self,
        method: HTTPMethod,
        path: str,
        params: dict[str, str] | None = None,
        json: dict | None = None,
    ) -> Response:
        logger.debug(
            "[%(method)s] %(path)s %(params)s\n" "json: %(json)s",
            {"method": method, "path": path, "params": params, "json": json},
        )
        url = f"{self.base_url}{path}"
        resp = self.__session.request(
            method=method,
            url=url,
            params=params,
            json=json,
        )
        if resp.status_code < HTTPStatus.BAD_REQUEST:
            return resp
        elif resp.status_code < HTTPStatus.INTERNAL_SERVER_ERROR:
            # A 4XX error happened
            logger.error(
                "Request"
                "[%(method)s] %(path)s %(params)s\n"
                "%(request)s\n\n"
                "Response [%(status)s]"
                "headers: %(response_headers)s\n"
                "%(response)s\n\n",
                {
                    "method": method,
                    "path": path,
                    "params": params,
                    "request": resp.request.body,
                    "status": resp.status_code,
                    "response_headers": resp.headers,
                    "response": resp.text,
                },
            )
            todo = "TODO: Add error reporting"
            raise NotImplementedError(todo)
        else:
            # A 5XX error happened
            logger.error(
                "Request"
                "[%(method)s] %(path)s %(params)s\n"
                "%(request)s\n\n"
                "Response [%(status)s]"
                "headers: %(response_headers)s\n"
                "%(response)s\n\n",
                {
                    "method": method,
                    "path": path,
                    "params": params,
                    "request": resp.request.body,
                    "status": resp.status_code,
                    "response_headers": resp.headers,
                    "response": resp.text,
                },
            )
            todo = "TODO: Add error reporting"
            raise NotImplementedError(todo)
        return resp

    def get(self, path: str, params: dict[str, Any] | None = None) -> Response:
        return self.request(method=HTTPMethod.GET, path=path, params=params)

    def post(self, path: str, json: dict[Any, Any] | None = None) -> Response:
        return self.request(method=HTTPMethod.POST, path=path, json=json)

    def __del__(self) -> None:
        self.__session.close()
