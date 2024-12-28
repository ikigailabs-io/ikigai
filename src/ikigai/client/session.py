# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import sys
from http import HTTPStatus
from typing import Any

import requests
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from requests import Response

from ikigai.utils.compatibility import HTTPMethod


@dataclass
class Session:
    base_url: str
    session: requests.Session

    __pydantic_config__ = ConfigDict(arbitrary_types_allowed=True)

    def request(
        self,
        method: HTTPMethod,
        path: str,
        params: dict[str, str] | None = None,
        json: dict | None = None,
    ) -> Response:
        url = f"{self.base_url}{path}"
        resp = self.session.request(
            method=method,
            url=url,
            params=params,
            json=json,
        )
        if resp.status_code < HTTPStatus.BAD_REQUEST:
            return resp
        elif resp.status_code < HTTPStatus.INTERNAL_SERVER_ERROR:
            # A 4XX error happened
            print(
                f"""{method} {path}\n"""
                f"""{resp.request.body!r}\n\n"""
                f"""{resp.raw.headers}\n"""
                f"""{resp.text}""",
                file=sys.stderr,
            )
            todo = "TODO: Add error reporting"
            raise NotImplementedError(todo)
        else:
            # A 5XX error happened
            print(
                f"""{method} {path}\n"""
                f"""{resp.request.body!r}\n\n"""
                f"""{resp.raw.headers}\n"""
                f"""{resp.text}""",
                file=sys.stderr,
            )
            todo = "TODO: Add error reporting"
            raise NotImplementedError(todo)
        return resp

    def get(self, path: str, params: dict[str, Any] | None = None) -> Response:
        return self.request(method=HTTPMethod.GET, path=path, params=params)

    def post(self, path: str, json: dict[Any, Any] | None = None) -> Response:
        return self.request(method=HTTPMethod.POST, path=path, json=json)

    def __del__(self) -> None:
        self.session.close()
