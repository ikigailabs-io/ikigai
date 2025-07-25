# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import sys

# Multiple python version compatible import for typing.override
if sys.version_info >= (3, 12):
    from typing import override  # noqa: F401
else:
    from typing_extensions import override  # noqa: F401

# Multiple python version compatible import for Self
if sys.version_info >= (3, 11):
    from typing import Self  # noqa: F401
else:
    from typing_extensions import Self  # noqa: F401

# Multiple python version compatible import for StrEnum
if sys.version_info >= (3, 11):
    from enum import StrEnum  # noqa: F401
else:
    from backports.strenum import StrEnum  # noqa: F401

# Multiple python version compatible import for HTTPMethod
if sys.version_info >= (3, 11):
    from http import HTTPMethod
else:

    class HTTPMethod(StrEnum):
        CONNECT = "CONNECT"
        DELETE = "DELETE"
        GET = "GET"
        HEAD = "HEAD"
        OPTIONS = "OPTIONS"
        PATCH = "PATCH"
        POST = "POST"
        PUT = "PUT"
        TRACE = "TRACE"


# Multiple python version compatible import for datetime.UTC
if sys.version_info >= (3, 11):
    from datetime import UTC  # noqa: F401
else:
    from datetime import timezone

    UTC = timezone.utc  # noqa: F401

# Multiple python version compatible import for typing.NotRequired
if sys.version_info >= (3, 11):
    from typing import NotRequired  # noqa: F401
else:
    from typing_extensions import NotRequired  # noqa: F401
