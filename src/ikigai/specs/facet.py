# SPDX-FileCopyrightText: 2026-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from collections import ChainMap
from collections.abc import Generator, Mapping
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    RootModel,
    field_validator,
    model_validator,
)

from ikigai.client.datax import FacetSpecsDict
from ikigai.typing.helpful import Helpful
from ikigai.utils.compatibility import Self, override
from ikigai.utils.custom_validators import LowercaseStr
from ikigai.utils.enums import FacetArgumentType
from ikigai.utils.missing import MISSING, MissingType


class FacetRequirementSpec(BaseModel):
    max_child_count: int
    min_child_count: int
    max_parent_count: int
    min_parent_count: int


class ArgumentSpec(BaseModel, Helpful):
    name: str
    argument_type: FacetArgumentType
    default_value: Any | None = None
    children: dict[str, ArgumentSpec]
    have_sub_arguments: bool
    is_deprecated: bool
    is_hidden: bool
    is_list: bool
    is_required: bool
    options: list | None = None

    model_config = ConfigDict(frozen=True)

    def __validation_error_message(
        self, facet, expectation, actuals: MissingType | Any = MISSING
    ) -> str:
        if actuals is MISSING:
            actuals_str = ""
        elif actuals is None:
            actuals_str = ", got 'None'"
        elif isinstance(actuals, type):
            actuals_str = f", got type '{actuals.__name__}'"
        else:
            actuals_str = f", got {actuals.__class__.__name__}({actuals!r})"

        return f"Argument '{self.name}' for facet '{facet}' {expectation}{actuals_str}"

    def validate_value(self, facet: str, value: Any) -> None:
        if value is None:
            if self.is_required:
                error_msg = self.__validation_error_message(facet, "is required", value)
                raise ValueError(error_msg)
            return None  # No further validation for None values

        # Value is not None, perform type checking
        if self.is_list:
            return self.__validate_list_value(facet, value)

        if self.argument_type == FacetArgumentType.MAP:
            return self.__validate_dict_value(facet, value)

        # Not a dict or list, so it must be a scalar value
        return self.__validate_scalar_value(facet, value)

    def __validate_list_value(self, facet: str, value: Any) -> None:
        if not isinstance(value, list):
            error_msg = self.__validation_error_message(facet, "must be list", value)
            raise TypeError(error_msg)

        scalar_argument_spec = self.model_copy(update={"is_list": False})
        for item in value:
            scalar_argument_spec.validate_value(facet, item)
        return None  # All items validated

    def __validate_dict_value(self, facet: str, value: Any) -> None:
        if not isinstance(value, Mapping):
            error_msg = self.__validation_error_message(facet, "must be mapping", value)
            raise TypeError(error_msg)

        for name, child_value in value.items():
            if name not in self.children:
                error_msg = self.__validation_error_message(
                    facet, f"provided with unexpected child argument '{name}'"
                )
                raise KeyError(error_msg)
            child_spec = self.children[name]
            child_spec.validate_value(facet=f"{facet}:{self.name}", value=child_value)
        return None  # All child arguments validated

    def __validate_scalar_value(self, facet: str, value: Any) -> None:
        # Basic type checking based on argument_type

        if self.options and value not in self.options:
            error_msg = self.__validation_error_message(
                facet, f"must be one of {self.options}", value
            )
            raise ValueError(error_msg)

        if self.argument_type == FacetArgumentType.BOOLEAN and not isinstance(
            value, bool
        ):
            error_msg = self.__validation_error_message(facet, "must be boolean", value)
            raise TypeError(error_msg)

        if self.argument_type == FacetArgumentType.TEXT and not isinstance(value, str):
            error_msg = self.__validation_error_message(facet, "must be string", value)
            raise TypeError(error_msg)

        if self.argument_type == FacetArgumentType.NUMBER and not isinstance(
            value, int | float
        ):
            error_msg = self.__validation_error_message(facet, "must be numeric", value)
            raise TypeError(error_msg)

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
            yield f"{self.name}: {argument_type}{argument_value}" + (
                f"  options=[{'|'.join(self.options)}]" if self.options else ""
            )

        if self.children:
            start_brackets, end_brackets = ("[{", "}]") if self.is_list else ("{", "}")
            yield f"{self.name}: {argument_type} = " + start_brackets
            for child in self.children.values():
                if child.is_hidden:
                    continue
                yield from (f"  {child_help}" for child_help in child._help())
            yield end_brackets


class FacetInfo(BaseModel):
    facet_uid: str
    facet_type: str
    facet_group: str


class FacetType(BaseModel, Helpful):
    facet_info: FacetInfo
    is_deprecated: bool
    is_hidden: bool
    facet_requirement: FacetRequirementSpec
    facet_arguments: dict[str, ArgumentSpec]
    in_arrow_arguments: dict[str, ArgumentSpec]
    out_arrow_arguments: dict[str, ArgumentSpec]

    model_config = ConfigDict(frozen=True)

    @field_validator(
        "facet_arguments", "in_arrow_arguments", "out_arrow_arguments", mode="before"
    )
    @classmethod
    def validate_arguments(cls, v: list[dict]) -> dict[str, ArgumentSpec]:
        if not isinstance(v, list):
            error_msg = "Expected a list of argument dictionaries"
            raise ValueError(error_msg)

        return {
            (spec := ArgumentSpec.model_validate(argument_dict)).name: spec
            for argument_dict in v
        }

    @property
    def facet_uid(self) -> str:
        return self.facet_info.facet_uid

    @property
    def name(self) -> str:
        return self.facet_info.facet_type

    @override
    def _help(self) -> Generator[str]:
        # Facet name
        yield f"{self.name.title()}:"
        # Facet Arguments
        visible_facet_arguments = [
            argument
            for argument in self.facet_arguments.values()
            if not argument.is_hidden
        ]
        if not visible_facet_arguments:
            yield "  No arguments"
            return

        if visible_facet_arguments:
            yield "  facet_arguments:"
            for argument in visible_facet_arguments:
                yield from (
                    f"    {argument_help}" for argument_help in argument._help()
                )

        # Arrow Arguments
        visible_in_arrow_arguments, out_arrow_arguments = (
            [
                argument
                for argument in self.in_arrow_arguments.values()
                if not argument.is_hidden
            ],
            [
                argument
                for argument in self.out_arrow_arguments.values()
                if not argument.is_hidden
            ],
        )

        # In Arrow Arguments
        if visible_in_arrow_arguments:
            yield "  in_arrow_arguments:"
            for argument in visible_in_arrow_arguments:
                yield from (
                    f"    {argument_help}" for argument_help in argument._help()
                )
        # Out Arrow Arguments
        if out_arrow_arguments:
            yield "  out_arrow_arguments:"
            for argument in out_arrow_arguments:
                yield from (
                    f"    {argument_help}" for argument_help in argument._help()
                )

    def is_ml_facet(self) -> bool:
        return self.facet_info.facet_group.upper() == "MACHINE_LEARNING"

    def check_arguments(self, arguments: dict) -> None:
        # TODO: Add facet spec checking here,
        #  right now we let platform inform the user on create/edit
        ...


class FacetTypes(BaseModel, Helpful):
    class ChainGroup(RootModel, Helpful):
        root: dict[LowercaseStr, FacetType]

        @model_validator(mode="after")
        def validate_lowercase_keys(self) -> Self:
            self.root = {
                key.lower().replace("_", "").replace(" ", ""): value
                for key, value in self.root.items()
            }
            return self

        def __contains__(self, name: str) -> bool:
            key = name.lower().replace("_", "").replace(" ", "")
            return key in self.root

        def __getitem__(self, name: str) -> FacetType:
            if name not in self:
                error_msg = f"{name.title()} facet does not exist"
                raise AttributeError(error_msg)
            key = name.lower().replace("_", "").replace(" ", "")
            return self.root[key]

        def __getattr__(self, name: str) -> FacetType:
            return self[name]

        @property
        def types(self) -> list[str]:
            return [
                facet_type.name
                for facet_type in self.root.values()
                if not facet_type.is_hidden
            ]

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
        flattened_data = {
            "INPUT": ChainMap(*data["INPUT"].values()),
            "MID": ChainMap(*data["MID"].values()),
            "OUTPUT": ChainMap(*data["OUTPUT"].values()),
        }

        return cls.model_validate(flattened_data)

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
