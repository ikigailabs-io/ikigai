# SPDX-FileCopyrightText: 2025-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from ikigai.typing.protocol.flow import FacetDict, FlowDict


def flow_versioning_shim(flow: FlowDict, facet_specs: dict) -> FlowDict:
    """
    Shim to improve compatibility with older Flow Definitions
    and migrate them to the latest format

    Args:
        flow (FlowDict): The flow to shim
        facet_specs (dict): The facet specifications to use for shimming

    Returns:
        FlowDict: The shimed flow
    """
    facets = flow["definition"].get("facets", [])
    flow["definition"]["facets"] = [
        _flow_facet_shim(
            facet=facet, facet_spec=__search_facet_spec(facet_specs, facet["facet_uid"])
        )
        for facet in facets
    ]

    return flow


def _flow_facet_shim(facet: FacetDict, facet_spec: dict | None) -> FacetDict:
    """
    Shim to improve compatibility with older Flow Definitions
    Fix the facet structure to match the expected format

    Args:
        facet (FacetDict): The facet to shim

    Returns:
        FacetDict: The shimed facet
    """
    # Initial cleaning of facet args
    facet_args = facet.get("arguments", {})
    if "submodel_type" in facet_args:
        facet_args["sub_model_type"] = facet_args["submodel_type"]
        del facet_args["submodel_type"]

    facet["arguments"] = facet_args.copy()

    if facet_spec is None:
        # If no facet specification is found, return the facet as is
        return facet

    # Normalize the facet arguments based on the facet specification
    for key, value in facet["arguments"].items():
        argument_spec = next(
            (
                arg_spec
                for arg_spec in facet_spec["facet_arguments"]
                if arg_spec["name"] == key
            ),
            None,
        )
        if not argument_spec:
            # If the argument is not specified in the facet spec, skip it
            del facet_args[key]
            continue

        normalization_is_required: bool = (
            isinstance(value, list)
            and not argument_spec.get("is_list", False)
            and argument_spec["argument_type"] == "MAP"
        )
        if normalization_is_required:
            facet_args[key] = value[0] if value else {}

        if "experiment_selection" in facet_args:
            del facet_args["experiment_selection"]

    # Update the facet arguments with the normalized values
    facet["arguments"] = facet_args
    return facet


def __search_facet_spec(facet_specs: dict, facet_uid: str) -> dict | None:
    """
    Search for a facet specification by facet UID

    Args:
        facet_specs (dict): The facet specifications to search
        facet_uid (str): The UID of the facet to search for

    Returns:
        dict | None: The facet specification if found, otherwise None
    """
    for chain_group in facet_specs.values():
        for facet_group in chain_group.values():
            for facet_type in facet_group.values():
                if facet_type["facet_info"]["facet_uid"] == facet_uid:
                    return facet_type

    # Facet specification with facet_uid not found in facet specifications
    return None
