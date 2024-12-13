# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

import random
import sys
from contextlib import ExitStack
from pathlib import Path
from typing import Any, Generator
import pytest

# Multiple python version compatible import for reading toml
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def read_credentials(env_file: Path) -> dict[str, Any]:
    with env_file.open("rb") as env:
        users: dict[str, dict[str, str]] = tomllib.load(env)["credentials"]["users"]
    return {"ids": users.keys(), "params": users.values()}


@pytest.fixture(**read_credentials(Path("./test-env.toml")))
def cred(request) -> dict[str, str]:
    return request.param


ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789-"


@pytest.fixture
def random_name() -> str:
    name_length = int(random.triangular(low=5, high=20, mode=20))
    return "".join(random.choices(ALPHABET, k=name_length))


@pytest.fixture
def cleanup() -> Generator[ExitStack, None, None]:
    exit_stack = ExitStack()
    try:
        yield exit_stack
    finally:
        exit_stack.close()
