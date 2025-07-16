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
    facet_types = ikigai.facet_types
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

    r"""
    Flow:
    Import -> Count -> Export
    """
    facet_types = ikigai.facet_types
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
    assert log.status == FlowStatus.SUCCESS, log.data


def test_flow_definition_multiple_parent_facets(
    ikigai: Ikigai,
    app_name: str,
    dataset_name: str,
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    flow_name: str,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)

    dataset1 = app.dataset.new(name=f"{dataset_name}-1").df(df1).build()
    cleanup.callback(dataset1.delete)

    dataset2 = app.dataset.new(name=f"{dataset_name}-2").df(df2).build()
    cleanup.callback(dataset2.delete)

    r"""
    Flow:
    Import-1 -\
               >-> Union -> Export
    Import-2 -/
    """
    facet_types = ikigai.facet_types
    builder = ikigai.builder
    imported_facet_1 = builder.facet(
        facet_type=facet_types.INPUT.IMPORTED, name="imported-facet-1"
    ).arguments(
        dataset_id=dataset1.dataset_id,
        file_type="csv",
        header=True,
        use_raw_file=False,
    )
    imported_facet_2 = builder.facet(
        facet_type=facet_types.INPUT.IMPORTED, name="imported-facet-2"
    ).arguments(
        dataset_id=dataset2.dataset_id,
        file_type="csv",
        header=True,
        use_raw_file=False,
    )
    flow_definition = (
        builder.facet(facet_type=facet_types.MID.UNION, name="union")
        .add_arrow(imported_facet_1, table_side="top")
        .add_arrow(imported_facet_2, table_side="bottom")
        .arguments(option="full")
        .facet(facet_type=facet_types.OUTPUT.EXPORTED)
        .arguments(dataset_name=f"output-{flow_name}", file_type="csv", header=True)
        .build()
    )
    flow = app.flow.new(name=flow_name).definition(flow_definition).build()
    cleanup.callback(flow.delete)

    log = flow.run()
    assert log.status == FlowStatus.SUCCESS, log.data


def test_flow_definition_multiple_child_facets(
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

    r"""
    Flow:
                     /-> Count -> Export
    Import -> Copy -<
                     \-> Export
    """
    facet_types = ikigai.facet_types
    builder = ikigai.builder
    source_data = (
        builder.facet(facet_type=facet_types.INPUT.IMPORTED, name="imported-facet")
        .arguments(
            dataset_id=dataset.dataset_id,
            file_type="csv",
            header=True,
            use_raw_file=False,
        )
        .facet(facet_type=facet_types.MID.COPY)
    )
    (
        source_data.facet(facet_type=facet_types.MID.COUNT)
        .arguments(target_columns=df1.columns.tolist()[:-2])
        .facet(facet_type=facet_types.OUTPUT.EXPORTED)
        .arguments(
            dataset_name=f"output-{flow_name}-count", file_type="csv", header=True
        )
    )
    source_data.facet(facet_type=facet_types.OUTPUT.EXPORTED).arguments(
        dataset_name=f"output-{flow_name}", file_type="csv", header=True
    )

    flow_definition = builder.build()
    flow = app.flow.new(name=flow_name).definition(flow_definition).build()
    cleanup.callback(flow.delete)

    log = flow.run()
    assert log.status == FlowStatus.SUCCESS, log.data


def test_flow_definition_simple_ml_facet(
    ikigai: Ikigai,
    app_name: str,
    dataset_name: str,
    df_ml_regression1: pd.DataFrame,
    model_name: str,
    flow_name: str,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)

    dataset = app.dataset.new(name=dataset_name).df(df_ml_regression1).build()
    cleanup.callback(dataset.delete)

    model_types = ikigai.model_types
    model = (
        app.model.new(model_name)
        .model_type(model_type=model_types["Linear"]["Lasso"])
        .build()
    )
    cleanup.callback(model.delete)

    facet_types = ikigai.facet_types
    flow_definition = (
        ikigai.builder.facet(facet_type=facet_types.INPUT.IMPORTED)
        .arguments(
            dataset_id=dataset.dataset_id,
            file_type="csv",
            header=True,
            use_raw_file=False,
        )
        .model_facet(
            facet_type=facet_types.MID.PREDICT,
            model_type=model_types["Linear"]["Lasso"],
        )
        .arguments(
            model_name=model.name,
            version="initial-train",
        )
        .hyperparameters(alpha=0.1, fit_intercept=True)
        .parameters(
            target_column="target",
        )
        .facet(facet_type=facet_types.OUTPUT.EXPORTED)
        .arguments(dataset_name=f"output-{flow_name}", file_type="csv", header=True)
        .build()
    )
    flow = app.flow.new(name=flow_name).definition(flow_definition).build()
    cleanup.callback(flow.delete)

    log = flow.run()
    assert log.status == FlowStatus.SUCCESS, log.data
