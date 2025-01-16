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
    cleanup.callback(flow.delete)

    with pytest.raises(KeyError):
        flows.get_id(flow.flow_id)

    flows_after_creation = app.flows()
    assert len(flows_after_creation) == 1

    flow_dict = flow.to_dict()
    assert flow_dict["name"] == flow_name


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


def test_flow_status(ikigai: Ikigai) -> None:
    # TODO: Update test once we can create pipelines
    app = ikigai.apps()["PCT (Shared)"]
    flow = app.flows().get_id("2r5dKDGQ2QVpqbQAsaBlCWOEVgY")

    status_report = flow.status()
    assert status_report.status == FlowStatus.IDLE
    assert status_report.progress is None
    assert not status_report.message


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
                        "children": ["count"],
                        "parents": [],
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
                        "children": ["output"],
                        "parents": ["input"],
                    },
                    {
                        "facet_id": "output",
                        "name": "output",
                        "facet_uid": "O_005",  # Exported dataset
                        "arguments": {
                            "dataset_name": f"output-{flow_name}",
                            "file_type": "csv",
                            "header": True,
                            "user_email": "harsh@ikigailabs.io",
                        },
                        "children": [],
                        "parents": ["count"],
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
                        "children": ["failing"],
                        "parents": [],
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
                        "children": ["output"],
                        "parents": ["input"],
                    },
                    {
                        "facet_id": "output",
                        "name": "output",
                        "facet_uid": "O_005",  # Exported dataset
                        "arguments": {
                            "dataset_name": f"output-{flow_name}",
                            "file_type": "csv",
                            "header": True,
                            "user_email": "harsh@ikigailabs.io",
                        },
                        "children": [],
                        "parents": ["failing"],
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
