# SPDX-FileCopyrightText: 2025-present Harsh Parekh <harsh@ikigailabs.io>
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


def test_flow_editing(
    ikigai: Ikigai,
    app_name: str,
    flow_name: str,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)

    flow = app.flow.new(name=flow_name).build()
    cleanup.callback(flow.delete)
    # TODO: Update test once we can nicely create pipeline definitions

    flow.rename(f"updated {flow_name}")

    flow_after_edit = app.flows().get_id(flow.flow_id)

    assert flow_after_edit.name == flow.name
    assert flow_after_edit.name == f"updated {flow_name}"


def test_flow_status(
    ikigai: Ikigai,
    app_name: str,
    flow_name: str,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)

    flow = app.flow.new(name=flow_name).build()
    cleanup.callback(flow.delete)

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
    cleanup.callback(dataset.delete)

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
    cleanup.callback(flow.delete)

    cloned_flow = (
        app.flow.new(name=f"clone of {flow_name}").definition(definition=flow).build()
    )
    cleanup.callback(cloned_flow.delete)

    flows = app.flows()

    # TODO: Add more assert to check that the cloning did happen
    assert flows[flow.name]
    assert flows[cloned_flow.name]


def test_flow_run_success(
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
    cleanup.callback(dataset.delete)

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
    cleanup.callback(flow.delete)

    log = flow.run()
    assert log.status == FlowStatus.SUCCESS
    assert log.erroneous_facet_id is None
    assert not log.data


def test_flow_run_fail(
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
    cleanup.callback(dataset.delete)

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
                        "facet_id": "failing",
                        "name": "failing",
                        "facet_uid": "M_000",  # Python Code
                        "arguments": {
                            "script": (
                                "import pandas as pd\n"
                                "df = data\n"
                                "raise ValueError('Expected Error')\n"
                                "result = df\n"
                            ),
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
                        "destination": "failing",
                    },
                    {
                        "arguments": {},
                        "source": "failing",
                        "destination": "output",
                    },
                ],
            }
        )
        .build()
    )
    cleanup.callback(flow.delete)

    log = flow.run()
    assert log.status == FlowStatus.FAILED
    assert log.erroneous_facet_id == "failing"
    assert log.data


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
    cleanup.callback(flow.delete)
    assert len(nested_flow_directory.flows()) == 1
    assert len(flow_directory.flows()) == 0


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
    cleanup.callback(flow.delete)

    flow_directory = app.flow_directory.new(name=flow_directory_name_1).build()
    cloned_flow = (
        app.flow.new(name=f"cloned-{flow_name}")
        .directory(flow_directory)
        .definition(flow)
        .build()
    )
    cleanup.callback(cloned_flow.delete)

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
