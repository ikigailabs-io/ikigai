# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from typing import Any

import pytest
from ikigai import Ikigai


def test_client_init(cred: dict[str, Any]) -> None:
    ikigai = Ikigai(**cred)
    assert ikigai


def test_client_apps(cred: dict[str, Any]) -> None:
    ikigai = Ikigai(**cred)
    apps = ikigai.apps()
    assert len(apps) > 0


def test_client_app_get_item(cred: dict[str, Any]) -> None:
    ikigai = Ikigai(**cred)
    apps = ikigai.apps()
    with pytest.raises(KeyError):
        apps["Testing"]
