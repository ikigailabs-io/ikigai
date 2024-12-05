# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from typing import Any
import pytest
from ikigai import Ikigai


@pytest.fixture
def ikigai(cred: dict[str, Any]) -> Ikigai:
    return Ikigai(**cred)