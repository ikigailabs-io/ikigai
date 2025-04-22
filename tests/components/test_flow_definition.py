# SPDX-FileCopyrightText: 2025-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT


from contextlib import ExitStack

from ikigai import Ikigai


def test_flow_definition_builder_facet_types(
    ikigai: Ikigai,
) -> None:
    facet_types = ikigai.builder.facet_types
    assert facet_types.INPUT
    assert facet_types.MID
    assert facet_types.OUTPUT

    # Assorted facet types tests
    assert "PYTHON" in facet_types.INPUT
    assert "PYTHON" in facet_types.MID
    assert "PYTHON" in facet_types.OUTPUT

    assert "IMPORTED" in facet_types.INPUT
    assert "IMPORTED" not in facet_types.MID
    assert "IMPORTED" not in facet_types.OUTPUT

    assert "EXPORTED" not in facet_types.INPUT
    assert "EXPORTED" not in facet_types.MID
    assert "EXPORTED" in facet_types.OUTPUT


def test_flow_definition_empty(
    ikigai: Ikigai,
    app_name: str,
    flow_name: str,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)

    flows = app.flows()
    assert len(flows) == 0

    flow = app.flow.new(name=flow_name).definition(ikigai.builder.build()).build()
    cleanup.callback(flow.delete)
