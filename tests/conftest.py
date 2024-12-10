# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

import random
import pytest


@pytest.fixture(
    params=[
        dict(
            user_email="harsh@ikigailabs.io",
            api_key="2gnVFartBD9i2XDt7AhAsAo8WY7",
            base_url="https://dev-api.ikigailabs.io",
        )
    ],
    ids=["dev-api"],
)
def cred(request) -> dict[str, str]:
    return request.param


ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789-"


@pytest.fixture
def random_name() -> str:
    name_length = int(random.triangular(low=5, high=20, mode=20))
    return "".join(random.choices(ALPHABET, k=name_length))
