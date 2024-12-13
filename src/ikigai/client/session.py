# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

import requests
from typing import Any, Optional
from pydantic import ConfigDict
from requests import Response
from pydantic.dataclasses import dataclass


@dataclass
class Session:
    base_url: str
    session: requests.Session

    __pydantic_config__ = ConfigDict(arbitrary_types_allowed=True)

    def request(
        self,
        method: str,
        path: str,
        params: Optional[dict[str, str]] = None,
        json: Optional[dict[Any, Any]] = None,
    ) -> Response:
        url = f"{self.base_url}{path}"
        resp = self.session.request(
            method=method,
            url=url,
            params=params,
            json=json,
        )
        if resp.status_code < 400:
            return resp
        elif resp.status_code < 500:
            # A 4XX error happened
            raise NotImplementedError("TODO: Add error reporting")
        elif resp.status_code < 600:
            # A 5XX error happened
            raise NotImplementedError("TODO: Add error reporting")
        return resp

    def get(self, path: str, params: Optional[dict[str, str]] = None) -> Response:
        return self.request(method="GET", path=path, params=params)

    def post(self, path: str, json: Optional[dict[Any, Any]] = None) -> Response:
        return self.request(method="POST", path=path, json=json)

    def __del__(self) -> None:
        self.session.close()
