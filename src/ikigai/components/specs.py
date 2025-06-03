# SPDX-FileCopyrightText: 2025-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from collections import ChainMap
from collections.abc import Generator
from typing import Any, override

from pydantic import AliasPath, BaseModel, ConfigDict, Field, RootModel

from ikigai.typing.protocol import (
    FacetSpecsDict,
)
from ikigai.utils.compatibility import Self
from ikigai.utils.custom_validators import LowercaseStr
from ikigai.utils.helpful import Helpful

logger = logging.getLogger("ikigai.components")


class FacetRequirementSpec(BaseModel):
    max_child_count: int
    min_child_count: int
    max_parent_count: int
    min_parent_count: int


class ArgumentSpec(BaseModel, Helpful):
    name: str
    argument_type: str
    default_value: Any | None = None
    children: dict[str, ArgumentSpec]
    have_sub_arguments: bool
    is_deprecated: bool
    is_hidden: bool
    is_list: bool
    is_required: bool
    options: list | None = None

    model_config = ConfigDict(frozen=True)

    @override
    def _help(self) -> Generator[str]:
        argument_type = (
            f"{self.argument_type}"
            if not self.is_list
            else f"list[{self.argument_type}]"
        )
        if self.is_required:
            argument_type += " | None"
        if not self.children:
            argument_value = f" = {self.default_value!r}" if self.default_value else ""
            yield f"{self.name}: {argument_type}{argument_value}"

        if self.children:
            yield f"{self.name}: {argument_type} = " "{"
            for child in self.children.values():
                if child.is_hidden:
                    continue
                yield from (f"  {child_help}" for child_help in child._help())
            yield "}"


class FacetSpec(BaseModel, Helpful):
    facet_uid: str = Field(validation_alias=AliasPath("facet_info", "facet_uid"))
    name: str = Field(validation_alias=AliasPath("facet_info", "facet_type"))
    is_deprecated: bool
    is_hidden: bool
    facet_requirement: FacetRequirementSpec
    facet_arguments: list[ArgumentSpec]
    in_arrow_arguments: list[ArgumentSpec]
    out_arrow_arguments: list[ArgumentSpec]

    model_config = ConfigDict(frozen=True)

    @override
    def _help(self) -> Generator[str]:
        # Facet name
        yield f"{self.name.title()}:"
        # Facet Arguments
        visible_facet_arguments = [
            argument for argument in self.facet_arguments if not argument.is_hidden
        ]
        if not visible_facet_arguments:
            yield "  No arguments"
            return

        for argument in visible_facet_arguments:
            yield from (f"  {argument_help}" for argument_help in argument._help())

    def check_arguments(self, arguments: dict) -> None: ...


class FacetTypes(BaseModel, Helpful):
    class ChainGroup(RootModel, Helpful):
        root: dict[LowercaseStr, FacetSpec]

        def __post_init__(self) -> None:
            self.root = {
                facet_type.lower(): facet_spec
                for facet_type, facet_spec in self.root.items()
            }

        def __contains__(self, name: str) -> bool:
            return name.lower() in self.root

        def __getitem__(self, name: str) -> FacetSpec:
            if name not in self:
                error_msg = f"{name.title()} facet does not exist"
                raise AttributeError(error_msg)
            return self.root[name.lower()]

        def __getattr__(self, name: str) -> FacetSpec:
            return self[name]

        def __repr__(self) -> str:
            keys = list(self.root.keys())
            return f"ChainGroup({keys})"

        def __dir__(self) -> list[str]:
            # Default dir() will return the attributes of the class
            attributes = list(super().__dir__())

            # Add the keys from the chain group
            attributes.extend([key.upper() for key in self.root])
            return attributes

        @override
        def _help(self) -> Generator[str]:
            for facet_spec in self.root.values():
                yield from (f"  {facet_help}" for facet_help in facet_spec._help())

    INPUT: ChainGroup
    MID: ChainGroup
    OUTPUT: ChainGroup

    model_config = ConfigDict(frozen=True)

    @classmethod
    def from_dict(cls, data: FacetSpecsDict) -> Self:
        logger.debug("Creating %s from %s", cls.__name__, data)
        flattened_data = {
            "INPUT": ChainMap(*data["INPUT"].values()),
            "MID": ChainMap(*data["MID"].values()),
            "OUTPUT": ChainMap(*data["OUTPUT"].values()),
        }
        self = cls.model_validate(flattened_data)

        return self

    @override
    def _help(self) -> Generator[str]:
        # INPUT Chain
        yield "INPUT"
        yield from (f"  {chain_help}" for chain_help in self.INPUT._help())
        # MID Chain
        yield "MID"
        yield from (f"  {chain_help}" for chain_help in self.MID._help())
        # OUTPUT Chain
        yield "OUTPUT"
        yield from (f"  {chain_help}" for chain_help in self.OUTPUT._help())
