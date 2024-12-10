# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

import pytest
from ikigai import Ikigai


def test_project_creation(ikigai: Ikigai, project_name: str) -> None:
    projects = ikigai.projects()
    project = (
        ikigai.project.new(name=project_name).description("A test project").build()
    )
    projects_after_creation = ikigai.projects()

    project.delete()
    with pytest.raises(KeyError):
        projects.get_id(project.project_id)

    assert projects_after_creation.get_id(project.project_id) is not None
