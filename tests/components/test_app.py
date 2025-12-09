# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
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

    assert "charts" in components
    assert components["charts"] == []

    assert "connectors" in components
    assert components["connectors"] == []

    assert "dashboards" in components
    assert components["dashboards"] == []

    assert "datasets" in components
    assert components["datasets"] == []

    assert "databases" in components
    assert components["databases"] == []

    assert "pipelines" in components
    assert components["pipelines"] == []

    assert "models" in components
    assert components["models"] == []

    assert "external_resources" in components
    assert components["external_resources"] == []


def test_app_directory(
    ikigai: Ikigai, app_directory_name: str, cleanup: ExitStack
) -> None:
    app_directory = ikigai.app_directory.new(name=app_directory_name).build()
    cleanup.callback(app_directory.delete)

    app_directories = ikigai.directories()

    assert len(app_directories) >= 1
    assert app_directory_name in app_directories
    fetched_app_directory = app_directories[app_directory_name]
    assert fetched_app_directory.directory_id == app_directory.directory_id


def test_app_browser_1(ikigai: Ikigai, app_name: str, cleanup: ExitStack) -> None:
    app = ikigai.app.new(name=app_name).description("Get by name").build()
    cleanup.callback(app.delete)

    fetched_app = ikigai.apps[app_name]
    assert fetched_app.app_id == app.app_id
    assert fetched_app.name == app_name


def test_app_browser_search_1(
    ikigai: Ikigai, app_name: str, cleanup: ExitStack
) -> None:
    app = ikigai.app.new(name=app_name).description("Get by name").build()
    cleanup.callback(app.delete)

    app_name_substr = app_name.split("-", maxsplit=1)[1]
    fetched_apps = ikigai.apps.search(app_name_substr)

    assert app_name in fetched_apps
    fetched_app = fetched_apps[app_name]

    assert fetched_app.app_id == app.app_id
    assert fetched_app.name == app.name == app_name
