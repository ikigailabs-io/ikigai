# SPDX-FileCopyrightText: 2025-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT


from ikigai import Ikigai


def test_facet_types_property_access(ikigai: Ikigai) -> None:
    facet_types = ikigai.facet_types
    assert facet_types

    assert hasattr(facet_types, "INPUT")
    assert hasattr(facet_types, "MID")
    assert hasattr(facet_types, "OUTPUT")


"""
Regression Testing

- Each regression test should be of the format:
    f"test_{ticket_number}_{short_desc}"
"""


def test_iplt_10504_multi_word_facet_type_access(ikigai: Ikigai) -> None:
    facet_types = ikigai.facet_types

    # Check that various casings and formats for Custom Facet work
    assert "Custom Facet" in facet_types.INPUT
    assert "CUSTOM FACET" in facet_types.INPUT
    assert "custom_facet" in facet_types.INPUT
    assert "CUSTOM_FACET" in facet_types.INPUT

    assert facet_types.INPUT.CUSTOM_FACET
    assert facet_types.INPUT.custom_facet
    assert facet_types.INPUT.CustomFacet
    assert facet_types.INPUT["Custom Facet"]

    # Check that various casings and formats for Drop Columns work
    assert "Drop Columns" in facet_types.MID
    assert "DROP COLUMNS" in facet_types.MID
    assert "drop_columns" in facet_types.MID
    assert "DROP_COLUMNS" in facet_types.MID

    assert facet_types.MID.DROP_COLUMNS
    assert facet_types.MID.drop_columns
    assert facet_types.MID.DropColumns
    assert facet_types.MID["Drop Columns"]
