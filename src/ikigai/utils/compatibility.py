# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import sys

# Multiple python version compatible import for Self
if sys.version_info >= (3, 11):
    from typing import Self  # noqa: F401
else:
    from typing_extensions import Self  # noqa: F401

# Multiple python version compatible import for HTTPMethod
if sys.version_info >= (3, 11):
    from http import HTTPMethod
else:
    from types import SimpleNamespace

    HTTPMethod = SimpleNamespace(
        CONNECT="CONNECT",
        DELETE="DELETE",
        GET="GET",
        HEAD="HEAD",
        OPTIONS="OPTIONS",
        PATCH="PATCH",
        POST="POST",
        PUT="PUT",
        TRACE="TRACE",
    )
