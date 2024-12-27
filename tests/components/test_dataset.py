# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from contextlib import ExitStack

import pandas as pd
import pytest
from ikigai.ikigai import Ikigai


def test_dataset_creation(
    ikigai: Ikigai,
    app_name: str,
    dataset_name: str,
    df1: pd.DataFrame,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)

    datasets = app.datasets()
    assert len(datasets) == 0

    dataset = app.dataset.new(name=dataset_name).df(df1).build()
    cleanup.callback(dataset.delete)

    with pytest.raises(KeyError):
        datasets.get_id(dataset.dataset_id)

    datasets_after_creation = app.datasets()
    assert len(datasets_after_creation) == 1

    dataset_dict = dataset.to_dict()
    assert dataset_dict["name"] == dataset_name


def test_dataset_editing(
    ikigai: Ikigai,
    app_name: str,
    dataset_name: str,
    df1: pd.DataFrame,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)
    dataset = app.dataset.new(name=dataset_name).df(df1).build()
    cleanup.callback(dataset.delete)

    dataset.rename(f"updated {dataset_name}")

    dataset_after_edit = app.datasets().get_id(dataset.dataset_id)
    assert dataset_after_edit.name == dataset.name
    assert dataset_after_edit.name == f"updated {dataset_name}"


def test_dataset_describe(
    ikigai: Ikigai,
    app_name: str,
    dataset_name: str,
    df1: pd.DataFrame,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)
    dataset = app.dataset.new(name=dataset_name).df(df1).build()
    cleanup.callback(dataset.delete)

    description = dataset.describe()
    assert description is not None
    assert "dataset" in description
    assert description["dataset"]["name"] == dataset_name
    assert description["dataset"]["project_id"] == app.app_id
    assert description["dataset"]["directory"] is not None
    assert description["dataset"]["directory"]["type"] == "DATASET"
