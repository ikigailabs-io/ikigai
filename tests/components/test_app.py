# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from contextlib import ExitStack

import pytest
from ikigai import Ikigai


def test_app_creation(ikigai: Ikigai, app_name: str, cleanup: ExitStack) -> None:
    apps = ikigai.apps()
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)

    app_dict = app.to_dict()
    apps_after_creation = ikigai.apps()

    with pytest.raises(KeyError):
        apps.get_id(app.app_id)
    assert app_dict["name"] == app_name
    assert app_dict["description"] == "A test app"
    assert apps_after_creation.get_id(app.app_id) is not None


def test_app_editing(ikigai: Ikigai, app_name: str, cleanup: ExitStack) -> None:
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)

    app.rename(f"updated {app_name}")
    app.update_description("An updated test app")

    app_after_edit = ikigai.apps().get_id(id=app.app_id)

    assert app_after_edit.name == app.name
    assert app_after_edit.description == app.description
    assert app_after_edit.name == f"updated {app_name}"
    assert app_after_edit.description == "An updated test app"


def test_app_describe_1(ikigai: Ikigai, app_name: str, cleanup: ExitStack) -> None:
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)

    description = app.describe()
    assert description is not None
    assert "app" in description
    assert description["app"]["name"] == app_name
    assert "components" in description
    components = description["components"]
    assert "charts" in components and components["charts"] == []
    assert "connectors" in components and components["connectors"] == []
    assert "dashboards" in components and components["dashboards"] == []
    assert "datasets" in components and components["datasets"] == []
    assert "databases" in components and components["databases"] == []
    assert "pipelines" in components and components["pipelines"] == []
    assert "models" in components and components["models"] == []
    assert "external_resources" in components and components["external_resources"] == []


def test_app_directory(ikigai: Ikigai) -> None:
    app_directories = ikigai.directories()

    # TODO: Update test when creating app directories is available
    assert len(app_directories) == 0
