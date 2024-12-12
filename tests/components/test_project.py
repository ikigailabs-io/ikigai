# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from contextlib import ExitStack
import pytest
from ikigai import Ikigai


def test_project_creation(
    ikigai: Ikigai, project_name: str, cleanup: ExitStack
) -> None:
    projects = ikigai.projects()
    project = (
        ikigai.project.new(name=project_name).description("A test project").build()
    )
    cleanup.callback(project.delete)

    project_dict = project.to_dict()
    projects_after_creation = ikigai.projects()

    with pytest.raises(KeyError):
        projects.get_id(project.project_id)
    assert project_dict["name"] == project_name
    assert project_dict["description"] == "A test project"
    assert projects_after_creation.get_id(project.project_id) is not None


def test_project_editing(ikigai: Ikigai, project_name: str, cleanup: ExitStack) -> None:
    project = (
        ikigai.project.new(name=project_name).description("A test project").build()
    )
    cleanup.callback(project.delete)

    project.rename(f"updated {project_name}")
    project.update_description("An updated test project")

    project_after_edit = ikigai.projects().get_id(id=project.project_id)

    assert project_after_edit.name == project.name
    assert project_after_edit.description == project.description
    assert project_after_edit.name == f"updated {project_name}"
    assert project_after_edit.description == "An updated test project"


def test_project_describe_1(
    ikigai: Ikigai, project_name: str, cleanup: ExitStack
) -> None:
    project = (
        ikigai.project.new(name=project_name).description("A test project").build()
    )
    cleanup.callback(project.delete)

    description = project.describe()
    assert description is not None
    assert "project" in description
    assert description["project"]["name"] == project_name
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
