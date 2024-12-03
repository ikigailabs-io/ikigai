# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

import requests
from pydantic import ConfigDict
from requests import Response
from pydantic.dataclasses import dataclass


@dataclass
class Session:
    base_url: str
    session: requests.Session

    __pydantic_config__ = ConfigDict(arbitrary_types_allowed=True)

    def request(self, path: str, **kwargs) -> Response:
        kwargs["url"] = f"{self.base_url}{path}"
        resp = self.session.request(**kwargs)
        if resp.status_code < 400:
            return resp
        elif resp.status_code < 500:
            # A 4XX error happened
            raise NotImplementedError("TODO: Add error reporting")
        elif resp.status_code < 600:
            # A 5XX error happened
            raise NotImplementedError("TODO: Add error reporting")
        return resp

    def get(self, path: str, **kwargs) -> Response:
        return self.request(method="GET", path=path, **kwargs)

    def post(self, path: str, **kwargs) -> Response:
        return self.request(method="POST", path=path, **kwargs)

    def __del__(self) -> None:
        self.session.close()
