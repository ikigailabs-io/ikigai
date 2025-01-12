# SPDX-FileCopyrightText: 2025-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT


from contextlib import ExitStack

from ikigai import Ikigai
from ikigai.components import FlowStatus


def test_flow_get(ikigai: Ikigai, app_name: str, cleanup: ExitStack) -> None:
    # TODO: Update test once we can create pipelines
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)

    flows = app.flows()
    assert len(flows) == 0


def test_flow_status(ikigai: Ikigai) -> None:
    # TODO: Update test once we can create pipelines
    app = ikigai.apps()["PCT (Shared)"]
    flow = app.flows().get_id("2r5dKDGQ2QVpqbQAsaBlCWOEVgY")

    status_report = flow.status()
    assert status_report.status == FlowStatus.IDLE
    assert status_report.progress is None
    assert not status_report.message


def test_flow_run_success(ikigai: Ikigai) -> None:
    # TODO: Update test once we can create pipelines
    app = ikigai.apps()["PCT (Shared)"]
    flow = app.flows().get_id("2r5dKDGQ2QVpqbQAsaBlCWOEVgY")

    log = flow.run()
    assert log.status == FlowStatus.SUCCESS
    assert log.erroneous_facet_id is None
    assert not log.data


def test_flow_run_fail(ikigai: Ikigai) -> None:
    # TODO: Update test once we can create pipelines
    app = ikigai.apps()["PCT (Shared)"]
    flow = app.flows()["Failing Flow"]

    log = flow.run()
    assert log.status == FlowStatus.FAILED
    assert log.erroneous_facet_id is not None
    assert log.data
