# SPDX-FileCopyrightText: 2026-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT


from contextlib import ExitStack

import pandas as pd
import pytest

from ikigai import FlowStatus, Ikigai


def test_custom_facet_creation(
    ikigai: Ikigai,
    custom_facet_name: str,
    cleanup: ExitStack,
) -> None:
    with pytest.raises(RuntimeError, match="Custom facet was not found"):
        ikigai.custom_facets[custom_facet_name]

    facet_types = ikigai.facet_types
    custom_facet = (
        ikigai.custom_facet.new(
            name=custom_facet_name, facet_type=facet_types.INPUT.CUSTOM_FACET
        )
        .script(script="result = data  # no-op", arguments={"input": "input-1"})
        .build()
    )
    cleanup.callback(custom_facet.delete)

    custom_facet = ikigai.custom_facets[custom_facet_name]
    assert custom_facet is not None
    assert custom_facet.name == custom_facet_name
    assert custom_facet.facet_type == facet_types.INPUT.CUSTOM_FACET
    assert custom_facet.arguments
    assert len(custom_facet.arguments) == 1
    assert "input" in custom_facet.arguments
    input_argument = custom_facet.arguments["input"]
    assert input_argument.name == "input"
    assert input_argument.argument_type == "str"
    assert input_argument.value == "input-1"


def test_custom_facet_editing(
    ikigai: Ikigai,
    custom_facet_name: str,
    cleanup: ExitStack,
) -> None:
    facet_types = ikigai.facet_types
    custom_facet = (
        ikigai.custom_facet.new(
            name=custom_facet_name, facet_type=facet_types.INPUT.CUSTOM_FACET
        )
        .script(script="result = data  # no-op", arguments={"input": "input-1"})
        .build()
    )
    cleanup.callback(custom_facet.delete)

    custom_facet.rename(name=f"updated-{custom_facet_name}")
    custom_facet.update_description(description="An updated test custom facet")
    custom_facet.update_script(
        script="result = data  # no-op",
        arguments={"updated-input": "input-2"},
    )

    # Check the custom facet after editing -- we should get the same custom facet back
    # and the values are correctly updated
    custom_facet_after_edit = ikigai.custom_facets[f"updated-{custom_facet_name}"]
    assert custom_facet_after_edit.custom_facet_id == custom_facet.custom_facet_id
    assert (
        custom_facet_after_edit.name
        == custom_facet.name
        == f"updated-{custom_facet_name}"
    )
    assert (
        custom_facet_after_edit.description
        == custom_facet.description
        == "An updated test custom facet"
    )
    assert (
        custom_facet_after_edit.facet_type
        == custom_facet.facet_type
        == facet_types.INPUT.CUSTOM_FACET
    )

    assert custom_facet_after_edit.arguments == custom_facet.arguments
    assert len(custom_facet_after_edit.arguments) == 1
    assert "updated-input" in custom_facet_after_edit.arguments
    assert custom_facet_after_edit.arguments["updated-input"].value == "input-2"


def test_custom_facet_unpinned_version_run(
    ikigai: Ikigai,
    custom_facet_name: str,
    app_name: str,
    flow_name: str,
    dataset_name: str,
    df1: pd.DataFrame,
    cleanup: ExitStack,
) -> None:
    app = (
        ikigai.app.new(name=app_name)
        .description("App to test custom facet unpinned version run")
        .build()
    )
    cleanup.callback(app.delete)

    facet_types = ikigai.facet_types
    custom_facet = (
        ikigai.custom_facet.new(
            name=custom_facet_name, facet_type=facet_types.INPUT.CUSTOM_FACET
        )
        .script(
            script="""
            import numpy as np
            import pandas as pd

            # Create a dummy dataframe
            df = pd.DataFrame({
                "col1": np.arange(10),
                "col2": [my_input] * 10,
            })

            # Output the dummy dataframe
            result = df
            """,
            arguments={"my_input": 1},
        )
        .build()
    )
    cleanup.callback(custom_facet.delete)

    # Create a flow with the custom facet
    flow_definition = (
        ikigai.builder.custom_facet(custom_facet_version=custom_facet.unpinned())
        .arguments(my_input=2)
        .facet(facet_type=facet_types.OUTPUT.EXPORTED, name="output")
        .arguments(dataset_name=f"output-{flow_name}", file_type="csv", header=True)
        .build()
    )
    flow = app.flow.new(name=flow_name).definition(definition=flow_definition).build()

    # Run the flow
    log = flow.run()
    assert log.status == FlowStatus.SUCCESS, log.data
    assert log.erroneous_facet_id is None, log
    assert not log.data

    # Check the output dataset
    output_dataset = app.datasets[f"output-{flow_name}"]
    assert output_dataset is not None
    assert output_dataset.name == f"output-{flow_name}"

    output_data = output_dataset.df()
    assert output_data is not None
    assert len(output_data) > 1
    assert output_data["col1"].tolist() == list(range(10))
    assert output_data["col2"].tolist() == [2] * 10
