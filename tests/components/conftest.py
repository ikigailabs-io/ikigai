# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from typing import Any
import pytest
from ikigai import Ikigai


@pytest.fixture
def ikigai(cred: dict[str, Any]) -> Ikigai:
    return Ikigai(**cred)


@pytest.fixture
def app_name(random_name: str) -> str:
    return f"proj-{random_name}"
