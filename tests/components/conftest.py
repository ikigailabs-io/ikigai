# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

import math
import random
from collections.abc import Callable
from typing import Any

import pandas as pd
import pytest
from faker import Faker
from ikigai import Ikigai

_ColumnNames = list[str]
_ColumnGenerator = Callable[[], Any]
_ColumnGenerators = list[_ColumnGenerator]
_TableGenerator = tuple[_ColumnNames, _ColumnGenerators]


def _create_table_generator(fake: Faker, k: int) -> _TableGenerator:
    """
    Return a table generator that generates a table with randomly selected columns
    where, k <= number of columns <= 2k
    """
    available_column_generators: list[list[tuple[str, _ColumnGenerator]]] = [
        [("name", fake.name), ("age", lambda: random.randint(20, 90))],
        [("ssn", fake.ssn)],
        [
            ("lat", lambda: float(fake.latitude())),
            ("lon", lambda: float(fake.longitude())),
        ],
        [("date", lambda: str(fake.date_time()))],
        [("email", fake.free_email)],
        [("work_email", fake.company_email)],
        [("job", fake.job), ("salary", fake.pricetag)],
    ]

    column_generators_selection = random.choices(available_column_generators, k=k)

    table_column_names: _ColumnNames = []
    table_column_generators: _ColumnGenerators = []
    for idx, column_generators in enumerate(column_generators_selection, start=1):
        for column_name, column_generator in column_generators:
            table_column_names.append(f"{column_name}-{idx}")
            table_column_generators.append(column_generator)
    return table_column_names, table_column_generators


@pytest.fixture
def ikigai(cred: dict[str, Any]) -> Ikigai:
    return Ikigai(**cred)


@pytest.fixture
def app_name(random_name: str) -> str:
    return f"proj-{random_name}"


def _generate_df(table_generator: _TableGenerator, num_rows: int) -> pd.DataFrame:
    column_names, column_generators = table_generator
    rows = [[gen() for gen in column_generators] for _ in range(num_rows)]
    return pd.DataFrame(data=rows, columns=column_names)


@pytest.fixture
def df1(faker: Faker) -> pd.DataFrame:
    num_generator_selections = random.randint(1, 10)
    num_rows = math.ceil(random.triangular(1, 100))
    table_generator = _create_table_generator(faker, num_generator_selections)
    return _generate_df(table_generator=table_generator, num_rows=num_rows)


@pytest.fixture
def df2(faker: Faker) -> pd.DataFrame:
    num_generator_selections = random.randint(1, 10)
    num_rows = math.ceil(random.triangular(1, 100))
    table_generator = _create_table_generator(faker, num_generator_selections)
    return _generate_df(table_generator=table_generator, num_rows=num_rows)


@pytest.fixture
def df_ml_regression1(faker: Faker) -> pd.DataFrame:
    """
    Generate a DataFrame suitable for ML regression tasks
    """
    num_generator_selections = random.randint(3, 10)
    num_rows = math.ceil(random.triangular(100, 1000))
    table_generator = _create_table_generator(faker, num_generator_selections)
    # Add a target column for regression
    target_column_name = "target"
    generated_df = _generate_df(table_generator=table_generator, num_rows=num_rows)
    generated_df[target_column_name] = generated_df.apply(
        lambda _: random.uniform(0, 100), axis=1
    )
    return generated_df


@pytest.fixture
def df_ml_classification1(faker: Faker) -> pd.DataFrame:
    """
    Generate a DataFrame suitable for ML classification tasks
    """
    num_generator_selections = random.randint(3, 10)
    num_rows = math.ceil(random.triangular(100, 1000))
    num_classes = math.floor(random.triangular(2, num_rows / 3))
    table_generator = _create_table_generator(faker, num_generator_selections)
    # Add a target column for classification
    target_column_name = "target"
    generated_df = _generate_df(table_generator=table_generator, num_rows=num_rows)
    generated_df[target_column_name] = generated_df.apply(
        lambda _: random.choice([f"class-{i}" for i in range(1, num_classes + 1)]),
        axis=1,
    )
    return generated_df


@pytest.fixture
def dataset_name(random_name: str) -> str:
    return f"dats-{random_name}"


@pytest.fixture
def dataset_directory_name_1(random_name: str) -> str:
    return f"dats-dir-1-{random_name}"


@pytest.fixture
def dataset_directory_name_2(random_name: str) -> str:
    return f"dats-dir-2-{random_name}"


@pytest.fixture
def flow_name(random_name: str) -> str:
    return f"flow-{random_name}"


@pytest.fixture
def flow_directory_name_1(random_name: str) -> str:
    return f"flow-dir-1-{random_name}"


@pytest.fixture
def flow_directory_name_2(random_name: str) -> str:
    return f"flow-dir-2-{random_name}"


@pytest.fixture
def model_name(random_name: str) -> str:
    return f"model-{random_name}"
