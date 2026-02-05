# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Protocol


class ModelType(Protocol):
    @property
    def model_type(self) -> str: ...

    @property
    def sub_model_type(self) -> str: ...
