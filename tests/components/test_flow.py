# SPDX-FileCopyrightText: 2025-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT


from contextlib import ExitStack

import pandas as pd
import pytest

from ikigai import Ikigai
from ikigai.components import FlowStatus


def test_flow_creation(
    ikigai: Ikigai,
    app_name: str,
    flow_name: str,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)

    flows = app.flows()
    assert len(flows) == 0

    flow = app.flow.new(name=flow_name).build()

    flow_dict = flow.to_dict()
    assert flow_dict["name"] == flow_name

    flows_after_creation = app.flows()
    assert len(flows_after_creation) == 1
    assert flows_after_creation[flow.name]

    flow.delete()
    flows_after_deletion = app.flows()
    assert len(flows_after_deletion) == 0
    with pytest.raises(KeyError):
        flows_after_deletion[flow.name]
    assert flow.flow_id not in flows_after_deletion


def test_flow_renaming(
    ikigai: Ikigai,
    app_name: str,
    flow_name: str,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)

    flow = app.flow.new(name=flow_name).build()

    flow.rename(f"updated {flow_name}")

    flow_after_edit = app.flows().get_id(flow.flow_id)

    assert flow_after_edit.name == flow.name
    assert flow_after_edit.name == f"updated {flow_name}"


def test_flow_definition_update(
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

    facet_types = ikigai.facet_types

    # Not a complete flow definition, should fail when run
    initial_flow_definition = (
        ikigai.builder.facet(facet_type=facet_types.INPUT.IMPORTED, name=dataset.name)
        .arguments(
            dataset_id=dataset.dataset_id,
            file_type="csv",
            header=True,
            use_raw_file=False,
        )
        .build()
    )

    flow = app.flow.new(name=flow_name).definition(initial_flow_definition).build()

    failure_log = flow.run()
    assert failure_log.status == FlowStatus.FAILED, failure_log.data

    # A complete flow definition, should succeed when run
    updated_flow_definition = (
        ikigai.builder.facet(facet_type=facet_types.INPUT.IMPORTED, name=dataset.name)
        .arguments(
            dataset_id=dataset.dataset_id,
            file_type="csv",
            header=True,
            use_raw_file=False,
        )
        .facet(facet_type=facet_types.OUTPUT.EXPORTED, name="output")
        .arguments(
            dataset_name=f"output-{flow_name}",
            file_type="csv",
            header=True,
        )
        .build()
    )

    flow.update_definition(updated_flow_definition)

    success_log = flow.run()
    assert success_log.status == FlowStatus.SUCCESS, success_log.data


def test_flow_status(
    ikigai: Ikigai,
    app_name: str,
    flow_name: str,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)

    flow = app.flow.new(name=flow_name).build()

    status_report = flow.status()
    assert status_report.status == FlowStatus.IDLE
    assert status_report.progress is None
    assert not status_report.message


def test_flow_clone(
    ikigai: Ikigai,
    app_name: str,
    dataset_name: str,
    df1: pd.DataFrame,
    flow_name: str,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("App to test flow run").build()
    cleanup.callback(app.delete)

    dataset = app.dataset.new(name=dataset_name).df(df1).build()

    # TODO: Update test once we can nicely create pipelines
    flow = (
        app.flow.new(name=flow_name)
        .definition(
            {
                "facets": [
                    {
                        "facet_id": "input",
                        "name": dataset.name,
                        "facet_uid": "I_005",  # Imported dataset
                        "arguments": {
                            "dataset_id": dataset.dataset_id,
                            "file_type": "csv",
                            "header": True,
                            "use_raw_file": False,
                        },
                    },
                    {
                        "facet_id": "count",
                        "name": "count",
                        "facet_uid": "M_003",  # Count
                        "arguments": {
                            "output_column_name": "count",
                            "sort": True,
                            "target_columns": df1.columns.to_list()[:-2],
                        },
                    },
                    {
                        "facet_id": "output",
                        "name": "output",
                        "facet_uid": "O_005",  # Exported dataset
                        "arguments": {
                            "dataset_name": f"output-{flow_name}",
                            "file_type": "csv",
                            "header": True,
                        },
                    },
                ],
                "arrows": [
                    {
                        "arguments": {},
                        "source": "input",
                        "destination": "count",
                    },
                    {
                        "arguments": {},
                        "source": "count",
                        "destination": "output",
                    },
                ],
            }
        )
        .build()
    )

    cloned_flow = (
        app.flow.new(name=f"clone of {flow_name}").definition(definition=flow).build()
    )

    flows = app.flows()

    # TODO: Add more assert to check that the cloning did happen
    assert flows[flow.name]
    assert flows[cloned_flow.name]


def test_flow_run_success_1(
    ikigai: Ikigai,
    app_name: str,
    dataset_name: str,
    df1: pd.DataFrame,
    flow_name: str,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("App to test flow run").build()
    cleanup.callback(app.delete)

    dataset = app.dataset.new(name=dataset_name).df(df1).build()

    facet_types = ikigai.facet_types
    flow_definition = (
        ikigai.builder.facet(facet_type=facet_types.INPUT.IMPORTED, name=dataset.name)
        .arguments(
            dataset_id=dataset.dataset_id,
            file_type="csv",
            header=True,
            use_raw_file=False,
        )
        .facet(facet_type=facet_types.MID.PYTHON, name="count")
        .arguments(script=("import pandas as pd\ndf = data\nresult = df\n"))
        .facet(facet_type=facet_types.OUTPUT.EXPORTED, name="output")
        .arguments(
            dataset_name=f"output-{flow_name}",
            file_type="csv",
            header=True,
        )
        .build()
    )

    flow = app.flow.new(name=flow_name).definition(definition=flow_definition).build()

    log = flow.run()
    assert log.status == FlowStatus.SUCCESS, log.data
    assert log.erroneous_facet_id is None, log
    assert not log.data


def test_flow_run_fail_1(
    ikigai: Ikigai,
    app_name: str,
    dataset_name: str,
    df1: pd.DataFrame,
    flow_name: str,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("App to test flow run").build()
    cleanup.callback(app.delete)

    dataset = app.dataset.new(name=dataset_name).df(df1).build()

    facet_types = ikigai.facet_types
    flow_definition = (
        ikigai.builder.facet(facet_type=facet_types.INPUT.IMPORTED, name=dataset.name)
        .arguments(
            dataset_id=dataset.dataset_id,
            file_type="csv",
            header=True,
            use_raw_file=False,
        )
        .facet(facet_type=facet_types.MID.PYTHON, name="failing")
        .arguments(
            script=(
                "import pandas as pd\n"
                "df = data\n"
                "raise ValueError('Expected Error')\n"
                "result = df\n"
            )
        )
        .facet(facet_type=facet_types.OUTPUT.EXPORTED, name="output")
        .arguments(
            dataset_name=f"output-{flow_name}",
            file_type="csv",
            header=True,
        )
        .build()
    )

    flow = app.flow.new(name=flow_name).definition(definition=flow_definition).build()

    log = flow.run()
    assert log.status == FlowStatus.FAILED, log.data
    assert log.erroneous_facet_id, log
    failing_facets = [
        facet
        for facet in flow_definition.facets
        if facet.facet_id == log.erroneous_facet_id
    ]
    assert len(failing_facets) == 1
    assert failing_facets[0].name == "failing"
    assert log.data, log


def test_flow_run_variables(
    ikigai: Ikigai,
    app_name: str,
    dataset_name: str,
    df1: pd.DataFrame,
    flow_name: str,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("App to test flow run").build()
    cleanup.callback(app.delete)

    dataset = app.dataset.new(name=dataset_name).df(df1).build()

    facet_types = ikigai.facet_types
    flow_definition = (
        ikigai.builder.facet(facet_type=facet_types.INPUT.IMPORTED, name=dataset.name)
        .arguments(
            dataset_id=dataset.dataset_id,
            file_type="csv",
            header=True,
            use_raw_file=False,
        )
        .facet(facet_type=facet_types.OUTPUT.EXPORTED, name="output")
        .arguments(dataset_name=f"output-{flow_name}", file_type="csv", header=True)
        .variables(output_dataset="dataset_name")
        .build()
    )

    flow = app.flow.new(name=flow_name).definition(definition=flow_definition).build()

    run_var_output_dataset = f"var-output-{flow_name}"
    log = flow.run(output_dataset=run_var_output_dataset)
    assert log.status == FlowStatus.SUCCESS, log.data
    assert log.erroneous_facet_id is None, log
    assert not log.data

    output_dataset = app.datasets[run_var_output_dataset]
    assert output_dataset


def test_flow_directories_creation(
    ikigai: Ikigai,
    app_name: str,
    flow_directory_name_1: str,
    flow_directory_name_2: str,
    flow_name: str,
    cleanup: ExitStack,
) -> None:
    app = (
        ikigai.app.new(name=app_name)
        .description("App to test flow directory creation")
        .build()
    )
    cleanup.callback(app.delete)

    assert len(app.flow_directories()) == 0

    flow_directory = app.flow_directory.new(name=flow_directory_name_1).build()
    assert len(app.flow_directories()) == 1
    assert len(flow_directory.directories()) == 0

    nested_flow_directory = (
        app.flow_directory.new(name=flow_directory_name_2)
        .parent(flow_directory)
        .build()
    )
    assert len(flow_directory.directories()) == 1
    assert len(nested_flow_directory.flows()) == 0

    flow_directories = app.flow_directories()
    assert flow_directories[flow_directory_name_1]
    assert flow_directories[flow_directory_name_2]

    flow = (
        app.flow.new(name=flow_name).directory(directory=nested_flow_directory).build()
    )
    nested_directory_flows = nested_flow_directory.flows()
    assert len(nested_directory_flows) == 1
    assert flow_name in nested_directory_flows
    assert nested_directory_flows[flow_name].flow_id == flow.flow_id

    assert len(flow_directory.flows()) == 0


def test_flow_browser_1(
    ikigai: Ikigai, app_name: str, flow_name: str, cleanup: ExitStack
) -> None:
    app = ikigai.app.new(name=app_name).description("Test to get flow by name").build()
    cleanup.callback(app.delete)

    flow = app.flow.new(name=flow_name).build()

    fetched_flow = app.flows[flow_name]
    assert fetched_flow.flow_id == flow.flow_id
    assert fetched_flow.name == flow_name


def test_flow_browser_search_1(
    ikigai: Ikigai, app_name: str, flow_name: str, cleanup: ExitStack
) -> None:
    app = ikigai.app.new(name=app_name).description("Test to get flow by name").build()
    cleanup.callback(app.delete)

    flow = app.flow.new(name=flow_name).build()

    flow_name_substr = flow_name.split("-", maxsplit=1)[1]
    fetched_flows = app.flows.search(flow_name_substr)

    assert flow_name in fetched_flows
    fetched_flow = fetched_flows[flow_name]

    assert fetched_flow.flow_id == flow.flow_id


def test_flow_high_volume_preference(
    ikigai: Ikigai,
    app_name: str,
    flow_name: str,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)

    flow = app.flow.new(name=flow_name).high_volume_preference(optimize=True).build()

    # Verify that the high volume preference is set correctly
    flow_details = flow.describe()
    assert flow_details["high_volume_preference"] is True, flow_details


def test_flow_high_volume_preference_update(
    ikigai: Ikigai,
    app_name: str,
    flow_name: str,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("App to test flow run").build()
    cleanup.callback(app.delete)

    facet_types = ikigai.facet_types
    flow_definition = (
        ikigai.builder.facet(facet_types.MID.Python)
        .arguments(
            script=(
                "import pandas as pd\n"
                "df = data\n"
                "raise ValueError('Expected Error')\n"
                "result = df\n"
            )
        )
        .build()
    )

    flow = (
        app.flow.new(name=flow_name)
        .definition(flow_definition)
        .high_volume_preference(optimize=False)
        .build()
    )

    flow_details = flow.describe()
    assert flow_details["high_volume_preference"] is False, flow_details
    assert flow_details["definition"]["facets"], flow_details["definition"]

    # Update the high volume preference
    flow.update_high_volume_preference(optimize=True)

    updated_flow_details = flow.describe()
    assert updated_flow_details["high_volume_preference"] is True, updated_flow_details
    assert updated_flow_details["definition"]["facets"], updated_flow_details[
        "definition"
    ]
    assert updated_flow_details["definition"] == flow_details["definition"]

    # Check that high volume preference persists after updating the definition
    new_flow_definition = ikigai.builder.build()
    flow.update_definition(definition=new_flow_definition)
    final_flow_details = flow.describe()

    assert final_flow_details["high_volume_preference"] is True, final_flow_details


"""
Regression Testing

- Each regression test should be of the format:
    f"test_{ticket_number}_{short_desc}"
"""


def test_iplt_7641_flows(
    ikigai: Ikigai,
    app_name: str,
    flow_directory_name_1: str,
    flow_name: str,
    cleanup: ExitStack,
) -> None:
    app = (
        ikigai.app.new(name=app_name)
        .description("An app to test that app.flows gets all flows")
        .build()
    )
    cleanup.callback(app.delete)

    flow = app.flow.new(name=flow_name).build()

    flow_directory = app.flow_directory.new(name=flow_directory_name_1).build()
    cloned_flow = (
        app.flow.new(name=f"cloned-{flow_name}")
        .directory(flow_directory)
        .definition(flow)
        .build()
    )

    flows = app.flows()
    directory_flows = flow_directory.flows()
    assert flows
    assert directory_flows
    assert len(directory_flows) == 1
    assert len(flows) >= len(directory_flows)
    assert flows[flow.name]
    assert flows[cloned_flow.name]
    with pytest.raises(KeyError):
        directory_flows[flow.name]
    assert directory_flows[cloned_flow.name]
