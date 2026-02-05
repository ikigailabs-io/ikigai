# SPDX-FileCopyrightText: 2024-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from contextlib import ExitStack
from logging import Logger

import pandas as pd
import pytest

from ikigai import FlowStatus, Ikigai
from ikigai.components.dataset import _get_dataset_download_url
from ikigai.utils import DatasetDownloadStatus


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

    round_trip_df1 = dataset.df()
    assert len(df1) == len(round_trip_df1)
    assert df1.columns.equals(round_trip_df1.columns)

    # v. helpful debug message when the test fails
    logger.info(
        ("df1.dtypes:\n%r\n%r\n\nround_trip_df1.dtypes:\n%r\n%r\n\n"),
        df1.dtypes,
        df1.head(),
        round_trip_df1.dtypes,
        round_trip_df1.head(),
    )

    pd.testing.assert_frame_equal(
        df1, round_trip_df1, check_dtype=False, check_exact=False
    )


def test_dataset_async_download(
    ikigai: Ikigai,
    app_name: str,
    dataset_name: str,
    df1: pd.DataFrame,
    cleanup: ExitStack,
    logger: Logger,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Test async dataset download by running a high volume flow.

    This test creates a high volume pipeline with a simple imported->exported
    structure. The output dataset will require async download processing,
    which tests the DatasetDownloadStatus.IN_PROGRESS handling.
    """
    app = (
        ikigai.app.new(name=app_name).description("Test async dataset download").build()
    )
    cleanup.callback(app.delete)

    # Create a small input dataset
    input_dataset = app.dataset.new(name=dataset_name).df(df1).build()

    # Create a high volume flow with imported->exported structure
    facet_types = ikigai.facet_types
    output_dataset_name = f"output-{dataset_name}"
    flow_definition = (
        ikigai.builder.facet(
            facet_type=facet_types.INPUT.IMPORTED, name=input_dataset.name
        )
        .arguments(
            dataset_id=input_dataset.dataset_id,
            file_type="csv",
            header=True,
            use_raw_file=False,
        )
        .facet(facet_type=facet_types.OUTPUT.EXPORTED, name="output")
        .arguments(
            dataset_name=output_dataset_name,
            file_type="csv",
            header=True,
        )
        .build()
    )

    # Build flow with high volume preference enabled
    flow = (
        app.flow.new(name=f"flow-{dataset_name}")
        .definition(flow_definition)
        .high_volume_preference(optimize=True)
        .build()
    )

    # Run the flow - this should create an output dataset
    logger.info("Running high volume flow to generate output dataset")
    run_log = flow.run()

    # Verify the flow succeeded
    assert run_log.status == FlowStatus.SUCCESS, run_log.data

    # Get the output dataset
    output_dataset = app.datasets[output_dataset_name]

    # Track whether IN_PROGRESS status was encountered
    in_progress_encountered = False

    # Wrap the original function to track IN_PROGRESS status
    original_get_url = _get_dataset_download_url

    def tracked_get_dataset_download_url(client, app_id, dataset_id):
        nonlocal in_progress_encountered
        # Call initialize_dataset_download to check initial status
        response = client.component.initialize_dataset_download(
            app_id=app_id,
            dataset_id=dataset_id,
        )

        # Track if we got IN_PROGRESS
        if response["status"] == DatasetDownloadStatus.IN_PROGRESS:
            in_progress_encountered = True
            logger.info("✓ Async download triggered: IN_PROGRESS status detected")

        # Delegate to original implementation
        return original_get_url(client, app_id, dataset_id)

    monkeypatch.setattr(
        "ikigai.components.dataset._get_dataset_download_url",
        tracked_get_dataset_download_url,
    )

    # Download the dataset - this will test the async download logic
    logger.info("Attempting to download output dataset (should trigger async download)")
    downloaded_df = output_dataset.df()

    # Verify that IN_PROGRESS status was encountered
    assert in_progress_encountered, (
        "Expected IN_PROGRESS status to be returned during async download, "
        "but it was not encountered"
    )

    # Verify the downloaded data matches the input
    assert len(downloaded_df) == len(df1)
    assert downloaded_df.columns.equals(df1.columns)

    logger.info(
        ("Input df1:\n%r\n%r\n\nDownloaded df:\n%r\n%r\n\n"),
        df1.dtypes,
        df1.head(),
        downloaded_df.dtypes,
        downloaded_df.head(),
    )

    pd.testing.assert_frame_equal(
        df1, downloaded_df, check_dtype=False, check_exact=False
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
    nested_directory_datasets = nested_dataset_directory.datasets()
    assert len(nested_directory_datasets) == 1
    assert dataset_name in nested_directory_datasets
    assert nested_directory_datasets[dataset_name].dataset_id == dataset.dataset_id

    assert len(dataset_directory.datasets()) == 0


def test_dataset_browser_1(
    ikigai: Ikigai,
    app_name: str,
    dataset_name: str,
    df1: pd.DataFrame,
    cleanup: ExitStack,
) -> None:
    app = (
        ikigai.app.new(name=app_name).description("Test to get dataset by name").build()
    )
    cleanup.callback(app.delete)

    dataset = app.dataset.new(name=dataset_name).df(df1).build()

    fetched_dataset = app.datasets[dataset_name]
    assert fetched_dataset.dataset_id == dataset.dataset_id
    assert fetched_dataset.name == dataset_name


def test_dataset_browser_search_1(
    ikigai: Ikigai,
    app_name: str,
    dataset_name: str,
    df1: pd.DataFrame,
    cleanup: ExitStack,
) -> None:
    app = (
        ikigai.app.new(name=app_name).description("Test to get dataset by name").build()
    )
    cleanup.callback(app.delete)

    dataset = app.dataset.new(name=dataset_name).df(df1).build()

    dataset_name_substr = dataset_name.split("-", maxsplit=1)[1]
    fetched_datasets = app.datasets.search(dataset_name_substr)

    assert dataset_name in fetched_datasets
    fetched_dataset = fetched_datasets[dataset_name]

    assert fetched_dataset.dataset_id == dataset.dataset_id


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
        .description("To test that app.datasets gets all datasets")
        .build()
    )
    cleanup.callback(app.delete)

    dataset_1 = app.dataset.new(name=dataset_name).df(df1).build()

    dataset_directory = app.dataset_directory.new(name=dataset_directory_name_1).build()
    dataset_2 = (
        app.dataset.new(name=f"cloned-{dataset_name}")
        .directory(dataset_directory)
        .df(df1)
        .build()
    )

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
