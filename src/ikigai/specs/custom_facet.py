# SPDX-FileCopyrightText: 2026-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel

from ikigai.specs.facet import ArgumentSpec, FacetType
from ikigai.typing import NamedMapping
from ikigai.utils import CustomFacetArgumentType
from ikigai.utils.compatibility import Self

logger = logging.getLogger("ikigai.specs")


class CustomFacetArgumentSpec(BaseModel):
    name: str
    argument_type: CustomFacetArgumentType
    value: Any


class CustomFacetType(FacetType):
    custom_facet_id: str
    version_id: str
    custom_facet_arguments: dict[str, ArgumentSpec]

    @classmethod
    def from_facet_type(
        cls,
        facet_type: FacetType,
        custom_facet_id: str,
        version_id: str,
        custom_facet_argument_specs: NamedMapping[CustomFacetArgumentSpec],
    ) -> Self:
        return cls.model_validate(
            {
                "facet_info": facet_type.facet_info,
                "is_deprecated": facet_type.is_deprecated,
                "is_hidden": facet_type.is_hidden,
                "facet_requirement": facet_type.facet_requirement,
                "facet_arguments": {
                    **facet_type.facet_arguments,
                    "custom_facet_id": (
                        facet_type.facet_arguments["custom_facet_id"].model_copy(
                            update={"options": [custom_facet_id]}
                        )
                    ),
                    "version_id": (
                        facet_type.facet_arguments["version_id"].model_copy(
                            update={"options": [version_id]}
                        )
                    ),
                },
                "custom_facet_id": custom_facet_id,
                "version_id": version_id,
                "custom_facet_arguments": {
                    name: ArgumentSpec(
                        name=name,
                        argument_type=argument_spec.argument_type.to_facet_argument_type(),
                        default_value=argument_spec.value,
                        children={},
                        have_sub_arguments=False,
                        is_deprecated=False,
                        is_hidden=False,
                        is_list=False,
                        is_required=True,
                        options=None,
                    )
                    for name, argument_spec in custom_facet_argument_specs.items()
                },
                "in_arrow_arguments": facet_type.in_arrow_arguments,
                "out_arrow_arguments": facet_type.out_arrow_arguments,
            }
        )
