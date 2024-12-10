# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from typing import Any

import pytest
from ikigai import Ikigai


def test_client_init(cred: dict[str, Any]) -> None:
    ikigai = Ikigai(**cred)
    assert ikigai


def test_client_projects(cred: dict[str, Any]) -> None:
    ikigai = Ikigai(**cred)
    projects = ikigai.projects()
    assert len(projects) > 0


def test_client_project_get_item(cred: dict[str, Any]) -> None:
    ikigai = Ikigai(**cred)
    projects = ikigai.projects()
    with pytest.raises(KeyError):
        projects["Testing"]
