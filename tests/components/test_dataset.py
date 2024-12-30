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
    df2: pd.DataFrame,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)
    dataset = app.dataset.new(name=dataset_name).df(df1).build()
    cleanup.callback(dataset.delete)

    dataset.rename(f"updated {dataset_name}")
    dataset.edit_data(df2)

    dataset_after_edit = app.datasets().get_id(dataset.dataset_id)
    round_trip_df2 = dataset_after_edit.df()

    assert dataset_after_edit.name == dataset.name
    assert dataset_after_edit.name == f"updated {dataset_name}"
    assert df2.columns.equals(round_trip_df2.columns)
    pd.testing.assert_frame_equal(
        df2, round_trip_df2, check_dtype=False, check_exact=False
    )


def test_dataset_download(
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

    round_trip_df1 = dataset.df()
    assert len(df1) == len(round_trip_df1)
    assert df1.columns.equals(round_trip_df1.columns)

    # v. helpful debug message when the test fails
    print(
        df1.dtypes, df1.head(), round_trip_df1.dtypes, round_trip_df1.head(), sep="\n"
    )

    pd.testing.assert_frame_equal(
        df1, round_trip_df1, check_dtype=False, check_exact=False
    )


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
