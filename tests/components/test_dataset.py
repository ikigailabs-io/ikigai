# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from contextlib import ExitStack
from logging import Logger

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
    logger: Logger,
) -> None:
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)
    dataset = app.dataset.new(name=dataset_name).df(df1).build()
    cleanup.callback(dataset.delete)

    round_trip_df1 = dataset.df()
    assert len(df1) == len(round_trip_df1)
    assert df1.columns.equals(round_trip_df1.columns)

    # v. helpful debug message when the test fails
    logger.info(
        "df1.dtypes:\n%r\n" "%r\n\n" "round_trip_df1.dtypes:\n%r\n" "%r\n\n",
        df1.dtypes,
        df1.head(),
        round_trip_df1.dtypes,
        round_trip_df1.head(),
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
    assert description["name"] == dataset_name
    assert description["project_id"] == app.app_id
    assert description["directory"] is not None
    assert description["directory"]["type"] == "DATASET"


def test_dataset_directories_creation(
    ikigai: Ikigai,
    app_name: str,
    dataset_directory_name_1: str,
    dataset_directory_name_2: str,
    dataset_name: str,
    df1: pd.DataFrame,
    cleanup: ExitStack,
) -> None:
    app = (
        ikigai.app.new(name=app_name)
        .description("App to test dataset directory creation")
        .build()
    )
    cleanup.callback(app.delete)

    assert len(app.dataset_directories()) == 0

    dataset_directory = app.dataset_directory.new(name=dataset_directory_name_1).build()
    assert len(app.dataset_directories()) == 1
    assert len(dataset_directory.directories()) == 0

    nested_dataset_directory = (
        app.dataset_directory.new(name=dataset_directory_name_2)
        .parent(dataset_directory)
        .build()
    )
    assert len(dataset_directory.directories()) == 1
    assert len(nested_dataset_directory.datasets()) == 0

    dataset_directories = app.dataset_directories()
    assert dataset_directories[dataset_directory_name_1]
    assert dataset_directories[dataset_directory_name_2]

    dataset = (
        app.dataset.new(name=dataset_name)
        .directory(directory=nested_dataset_directory)
        .df(df1)
        .build()
    )
    cleanup.callback(dataset.delete)
    assert len(nested_dataset_directory.datasets()) == 1
    assert len(dataset_directory.datasets()) == 0


"""
Regression Testing

- Each regression test should be of the format:
    f"test_{ticket_number}_{short_desc}"
"""


def test_iplt_7641_datasets(
    ikigai: Ikigai,
    app_name: str,
    dataset_directory_name_1: str,
    dataset_name: str,
    df1: pd.DataFrame,
    cleanup: ExitStack,
) -> None:
    app = (
        ikigai.app.new(name=app_name)
        .description("An app to test that app.flows gets all flows")
        .build()
    )
    cleanup.callback(app.delete)

    dataset_1 = app.dataset.new(name=dataset_name).df(df1).build()
    cleanup.callback(dataset_1.delete)

    dataset_directory = app.dataset_directory.new(name=dataset_directory_name_1).build()
    dataset_2 = (
        app.dataset.new(name=f"cloned-{dataset_name}")
        .directory(dataset_directory)
        .df(df1)
        .build()
    )
    cleanup.callback(dataset_2.delete)

    datasets = app.datasets()
    directory_datasets = dataset_directory.datasets()
    assert datasets
    assert directory_datasets
    assert len(directory_datasets) == 1
    assert len(datasets) >= len(directory_datasets)
    assert datasets[dataset_1.name]
    assert datasets[dataset_2.name]
    with pytest.raises(KeyError):
        directory_datasets[dataset_1.name]
    assert directory_datasets[dataset_2.name]
