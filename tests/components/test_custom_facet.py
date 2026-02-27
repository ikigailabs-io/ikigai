# SPDX-FileCopyrightText: 2026-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT


from contextlib import ExitStack
from pathlib import Path

import pytest

from ikigai import FlowStatus, Ikigai


def test_custom_facet_creation_1(
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


def test_custom_facet_creation_2(
    ikigai: Ikigai,
    custom_facet_name: str,
    tmp_path: Path,
    cleanup: ExitStack,
) -> None:
    requirements_file = tmp_path / "requirements.txt"
    requirements_file.write_text("ikigai\npandas==1.5.2\n")

    script_file = tmp_path / "script.py"
    script_file.write_text(
        """
        import ikigai

        result = data  # no-op
        """
    )

    # Also test system_access flag but only for pre-setup user
    system_access = ikigai.user_email == "harsh+github-ci@ikigailabs.io"

    facet_types = ikigai.facet_types
    custom_facet = (
        ikigai.custom_facet.new(
            name=custom_facet_name, facet_type=facet_types.MID.CUSTOM_FACET
        )
        .script(
            script_file, requirements=requirements_file, system_access=system_access
        )
        .description("A test custom facet")
        .build()
    )
    cleanup.callback(custom_facet.delete)

    assert custom_facet.name == custom_facet_name


def test_custom_facet_creation_browsing(
    ikigai: Ikigai,
    custom_facet_name: str,
    custom_facet_name_2: str,
    custom_facet_name_3: str,
    cleanup: ExitStack,
) -> None:
    facet_types = ikigai.facet_types
    custom_facet_1 = ikigai.custom_facet.new(
        name=custom_facet_name, facet_type=facet_types.MID.CUSTOM_FACET
    ).build()
    cleanup.callback(custom_facet_1.delete)

    custom_facet_2 = (
        ikigai.custom_facet.new(
            name=custom_facet_name_2, facet_type=facet_types.MID.CUSTOM_FACET
        )
        .script(script="result = data  # no-op")
        .build()
    )
    cleanup.callback(custom_facet_2.delete)

    custom_facet_3 = (
        ikigai.custom_facet.new(
            name=custom_facet_name_3, facet_type=facet_types.MID.CUSTOM_FACET
        )
        .script(script="result = data  # no-op")
        .build()
    )
    cleanup.callback(custom_facet_3.delete)

    assert custom_facet_1 in ikigai.custom_facets.search(custom_facet_name)
    assert custom_facet_2 in ikigai.custom_facets.search(custom_facet_name_2)
    assert custom_facet_3 in ikigai.custom_facets.search(custom_facet_name_3)


def test_custom_facet_editing(
    ikigai: Ikigai,
    custom_facet_name: str,
    cleanup: ExitStack,
) -> None:
    facet_types = ikigai.facet_types
    custom_facet = (
        ikigai.custom_facet.new(
            name=custom_facet_name, facet_type=facet_types.MID.CUSTOM_FACET
        )
        .script(script="result = data  # no-op", arguments={"input": "input-1"})
        .description("A custom facet for testing editing operations")
        .build()
    )
    cleanup.callback(custom_facet.delete)

    (
        custom_facet.rename(name=f"updated-{custom_facet_name}")
        .update_description(description="An updated test custom facet")
        .update_script(
            script="result = data  # no-op",
            arguments={"updated-input": "input-2"},
        )
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
        == facet_types.MID.CUSTOM_FACET
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


def test_custom_facet_version_creation(
    ikigai: Ikigai,
    custom_facet_name: str,
    app_name: str,
    flow_name: str,
    cleanup: ExitStack,
) -> None:
    app = (
        ikigai.app.new(name=app_name)
        .description("App to test custom facet version creation")
        .build()
    )
    cleanup.callback(app.delete)

    facet_types = ikigai.facet_types
    custom_facet = (
        ikigai.custom_facet.new(
            name=custom_facet_name, facet_type=facet_types.INPUT.CUSTOM_FACET
        )
        .script(script="data = data  # bad-script")
        .build()
    )
    cleanup.callback(custom_facet.delete)

    unpinned_version = custom_facet.unpinned()

    # Create a flow with the unpinned version, try running it to see if it fails
    flow_definition_unpinned = (
        ikigai.builder.custom_facet(custom_facet_version=unpinned_version)
        .facet(facet_type=facet_types.OUTPUT.EXPORTED, name="output")
        .arguments(
            dataset_name=f"output-{flow_name}-unpinned", file_type="csv", header=True
        )
        .build()
    )
    flow_unpinned = (
        app.flow.new(name=f"{flow_name}-unpinned")
        .definition(definition=flow_definition_unpinned)
        .build()
    )
    cleanup.callback(flow_unpinned.delete)

    log_unpinned_1 = flow_unpinned.run()
    assert log_unpinned_1.status == FlowStatus.FAILED, log_unpinned_1.data
    assert log_unpinned_1.erroneous_facet_id, log_unpinned_1
    assert log_unpinned_1.data, log_unpinned_1

    # Create a version 1 of the custom facet
    version_1 = custom_facet.create_version(name="version-1")

    # Create a flow with the version 1, try running it to see if it fails
    flow_definition_1 = (
        ikigai.builder.custom_facet(custom_facet_version=version_1)
        .facet(facet_type=facet_types.OUTPUT.EXPORTED, name="output")
        .arguments(dataset_name=f"output-{flow_name}-1", file_type="csv", header=True)
        .build()
    )
    flow_1 = (
        app.flow.new(name=f"{flow_name}-1")
        .definition(definition=flow_definition_1)
        .build()
    )

    log_1 = flow_1.run()
    assert log_1.status == FlowStatus.FAILED, log_1.data
    assert log_1.erroneous_facet_id, log_1
    assert log_1.data, log_1

    # Unpinned version should still fail
    log_unpinned_2 = flow_unpinned.run()
    assert log_unpinned_2.status == FlowStatus.FAILED, log_unpinned_2.data
    assert log_unpinned_2.erroneous_facet_id, log_unpinned_2
    assert log_unpinned_2.data, log_unpinned_2

    # Update the custom facet script to fix the error
    custom_facet.update_script(
        script="""
        import numpy as np
        import pandas as pd

        # Create a dummy dataframe
        df = pd.DataFrame({
            "col1": np.arange(10),
            "col2": [1] * 10,
        })

        # Output the dummy dataframe
        result = df
        """
    )

    # Unpinned version should still fail since latest version is still bad
    log_unpinned_3 = flow_unpinned.run()
    assert log_unpinned_3.status == FlowStatus.FAILED, log_unpinned_3.data
    assert log_unpinned_3.erroneous_facet_id, log_unpinned_3
    assert log_unpinned_3.data, log_unpinned_3

    # Create a version 2 of the custom facet
    version_2 = custom_facet.create_version(name="version-2")

    # Create a flow with the version 2, try running it to see if it succeeds
    flow_definition_2 = (
        ikigai.builder.custom_facet(custom_facet_version=version_2)
        .facet(facet_type=facet_types.OUTPUT.EXPORTED, name="output")
        .arguments(dataset_name=f"output-{flow_name}-2", file_type="csv", header=True)
        .build()
    )
    flow_2 = (
        app.flow.new(name=f"{flow_name}-2")
        .definition(definition=flow_definition_2)
        .build()
    )

    log_2 = flow_2.run()
    assert log_2.status == FlowStatus.SUCCESS, log_2.data
    assert log_2.erroneous_facet_id is None, log_2
    assert not log_2.data

    # Unpinned version should now succeed
    log_unpinned_4 = flow_unpinned.run()
    assert log_unpinned_4.status == FlowStatus.SUCCESS, log_unpinned_4.data
    assert log_unpinned_4.erroneous_facet_id is None, log_unpinned_4
    assert not log_unpinned_4.data


def test_custom_facet_version_browsing(
    ikigai: Ikigai,
    custom_facet_name: str,
    custom_facet_version_name_1: str,
    custom_facet_version_name_2: str,
    custom_facet_version_name_3: str,
    cleanup: ExitStack,
) -> None:
    facet_types = ikigai.facet_types
    custom_facet = (
        ikigai.custom_facet.new(
            name=custom_facet_name, facet_type=facet_types.MID.CUSTOM_FACET
        )
        .script(script="result = data  # no-op")
        .build()
    )
    cleanup.callback(custom_facet.delete)

    created_versions = {
        custom_facet_version_name_1: custom_facet.create_version(
            name=custom_facet_version_name_1
        ),
        custom_facet_version_name_2: custom_facet.create_version(
            name=custom_facet_version_name_2
        ),
        custom_facet_version_name_3: custom_facet.create_version(
            name=custom_facet_version_name_3
        ),
    }

    versions = custom_facet.versions()
    assert len(versions) == len(created_versions)

    assert all(
        created_version in versions for created_version in created_versions.values()
    )
