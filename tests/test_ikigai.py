# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from typing import Any

import pytest
from pydantic import ValidationError

from ikigai import Ikigai


def test_client_init(cred: dict[str, Any]) -> None:
    ikigai = Ikigai(**cred)
    assert ikigai


def test_client_init_bad_base_url(cred: dict[str, Any], random_name: str) -> None:
    bad_cred = {
        **cred,
        "base_url": f"https://{random_name}.ikigailabs.io",
    }
    with pytest.raises(ValidationError):
        Ikigai(**bad_cred)


def test_client_apps(cred: dict[str, Any]) -> None:
    ikigai = Ikigai(**cred)
    apps = ikigai.apps()
    assert len(apps) > 0


def test_client_app_get_item(cred: dict[str, Any], random_name: str) -> None:
    ikigai = Ikigai(**cred)
    apps = ikigai.apps()
    with pytest.raises(KeyError):
        apps[random_name]


"""
Regression Testing

- Each regression test should be of the format:
    f"test_{ticket_number}_{short_desc}"
"""


@pytest.mark.skip(
    "TODO: Update test after creating app directory is available in the client"
)
def test_iplt_7641_apps(cred: dict[str, Any]) -> None:
    # TODO: update test after creating app directory is available in the client
    pass
