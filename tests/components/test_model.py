# SPDX-FileCopyrightText: 2025-present ikigailabs.io <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

from contextlib import ExitStack

import pytest

from ikigai import Ikigai


def test_model_types(
    ikigai: Ikigai,
    app_name: str,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)

    model_types = ikigai.model_types
    assert model_types is not None
    assert len(model_types) > 0
    lasso = model_types["Linear"]["Lasso"]

    assert lasso is not None
    assert lasso.model_type == "Linear"
    assert lasso.sub_model_type == "Lasso"


def test_model_creation(
    ikigai: Ikigai,
    app_name: str,
    model_name: str,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)

    models = app.models()
    assert len(models) == 0

    model_types = ikigai.model_types
    model = (
        app.model.new(model_name)
        .model_type(model_type=model_types["Linear"]["Lasso"])
        .build()
    )

    models_after_creation = app.models()
    assert len(models_after_creation) == 1
    assert models_after_creation[model.name]

    model.delete()
    models_after_deletion = app.models()
    assert len(models_after_deletion) == 0

    with pytest.raises(KeyError):
        models_after_deletion[model.name]
    assert model.model_id not in models_after_deletion


def test_model_editing(
    ikigai: Ikigai,
    app_name: str,
    model_name: str,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)

    model_types = ikigai.model_types
    model = (
        app.model.new(model_name)
        .model_type(model_type=model_types["Linear"]["Lasso"])
        .build()
    )

    model.rename(f"updated {model_name}")
    model.update_description("updated description")

    model_after_edit = app.models().get_id(model.model_id)
    assert model_after_edit.name == model.name
    assert model_after_edit.name == f"updated {model_name}"
    assert model_after_edit.description == model.description
    assert model_after_edit.description == "updated description"
    assert model_after_edit.model_type == model.model_type
    assert model_after_edit.model_type == "Linear"
    assert model_after_edit.sub_model_type == model.sub_model_type
    assert model_after_edit.sub_model_type == "Lasso"


def test_model_describe(
    ikigai: Ikigai,
    app_name: str,
    model_name: str,
    cleanup: ExitStack,
) -> None:
    app = ikigai.app.new(name=app_name).description("A test app").build()
    cleanup.callback(app.delete)

    model_types = ikigai.model_types
    model = (
        app.model.new(model_name)
        .model_type(model_type=model_types["Linear"]["Lasso"])
        .build()
    )

    model_description = model.describe()
    assert model_description is not None
    assert model_description["name"] == model.name
    assert model_description["description"] == model.description


def test_model_browser_1(
    ikigai: Ikigai, app_name: str, model_name: str, cleanup: ExitStack
) -> None:
    app = ikigai.app.new(name=app_name).description("Test to get model by name").build()
    cleanup.callback(app.delete)

    model_types = ikigai.model_types
    model = (
        app.model.new(name=model_name)
        .model_type(model_type=model_types["Linear"]["Lasso"])
        .build()
    )

    fetched_model = app.models[model_name]
    assert fetched_model.model_id == model.model_id
    assert fetched_model.name == model_name


def test_model_browser_search_1(
    ikigai: Ikigai, app_name: str, model_name: str, cleanup: ExitStack
) -> None:
    app = ikigai.app.new(name=app_name).description("Test to get model by name").build()
    cleanup.callback(app.delete)

    model_types = ikigai.model_types
    model = (
        app.model.new(name=model_name)
        .model_type(model_type=model_types["Linear"]["Lasso"])
        .build()
    )

    model_name_substr = model_name.split("-", maxsplit=1)[1]
    fetched_models = app.models.search(model_name_substr)

    assert model_name in fetched_models
    fetched_model = fetched_models[model_name]

    assert fetched_model.model_id == model.model_id


def test_model_builder_hyperparameter_groups(
    ikigai: Ikigai,
) -> None:
    flow_builder = ikigai.builder
    facet_types = ikigai.facet_types
    model_types = ikigai.model_types
    expected_model_facet_args = {
        "model_name": "test_model_name_1",
        "parameters": {
            "time_column": "WEEK_END_DT",
            "identifier_columns": ["forecast_identifier"],
            "value_column": "MEASURE_QTY",
            "mode": "train",
        },
        "processing": {
            "type": "base",
            "return_all_levels": False,
            "fill_missing_values": "zero",
            "drop_threshold": 0.9,
            "include_reals": True,
            "nonnegative": True,
        },
        "model_selection": {
            "models_to_include": ["Additive", "Sma", "Tsfm0"],
            "eval_method": "holdout",
            "time_budget": 100,
            "enable_parallel_processing": True,
            "best_model_only": True,
            "confidence": 0.7,
            "enable_conformal_interval": False,
        },
        "metrics": [
            {
                "interval_to_predict": 10,
                "holdout_period": 10,
                "metric": "weighted_mean_absolute_percentage_error",
            }
        ],
    }
    aicast_facet = (
        flow_builder.model_facet(
            facet_type=facet_types.MID.AI_CAST, model_type=model_types.AI_CAST.base
        )
        .arguments(
            model_name="test_model_name_1",
        )
        .parameters(
            time_column="WEEK_END_DT",
            identifier_columns=["forecast_identifier"],
            value_column="MEASURE_QTY",
            mode="train",
        )
        .hyperparameters(
            type="base",
            models_to_include=["Additive", "Sma", "Tsfm0"],
            eval_method="holdout",
            time_budget=100,
            enable_parallel_processing=True,
            best_model_only=True,
            confidence=0.7,
        )
        .hyperparameters(
            enable_conformal_interval=False,
            return_all_levels=False,
            fill_missing_values="zero",
            drop_threshold=0.9,
            include_reals=True,
            nonnegative=True,
            interval_to_predict=10,
            holdout_period=10,
            metric="weighted_mean_absolute_percentage_error",
        )
    ).build()
    assert aicast_facet.facets[0].arguments == expected_model_facet_args
