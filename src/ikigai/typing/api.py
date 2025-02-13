# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TypedDict


class GetDatasetMultipartUploadUrlsResponse(TypedDict):
    upload_id: str
    content_type: str
    urls: dict[int, str]
