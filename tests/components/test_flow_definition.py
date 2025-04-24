# SPDX-FileCopyrightText: 2025-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT


from contextlib import ExitStack

import pandas as pd
from ikigai import Ikigai
from ikigai.components import FlowStatus


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


def test_flow_definition_simple(
    ikigai: Ikigai,
    app_name: str,
    dataset_name: str,
    df1: pd.DataFrame,
    flow_name: str,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)

    dataset = app.dataset.new(name=dataset_name).df(df1).build()
    cleanup.callback(dataset.delete)

    facet_types = ikigai.builder.facet_types
    flow_definition = (
        ikigai.builder.facet(facet_type=facet_types.INPUT.IMPORTED)
        .arguments(
            dataset_id=dataset.dataset_id,
            file_type="csv",
            header=True,
            use_raw_file=False,
        )
        .facet(facet_type=facet_types.MID.COUNT)
        .arguments(
            output_column_name="count",
            sort=True,
            target_columns=df1.columns.tolist()[:-2],
        )
        .facet(facet_type=facet_types.OUTPUT.EXPORTED)
        .arguments(dataset_name=f"output-{flow_name}", file_type="csv", header=True)
        .build()
    )
    flow = app.flow.new(name=flow_name).definition(flow_definition).build()
    cleanup.callback(flow.delete)

    log = flow.run()
    assert log.status == FlowStatus.SUCCESS
