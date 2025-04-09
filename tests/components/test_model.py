# SPDX-FileCopyrightText: 2025-present Harsh Parekh <harsh@ikigailabs.io>
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

    model_types = app.model.model_types
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

    model_types = app.model.model_types
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
