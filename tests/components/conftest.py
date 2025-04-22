# SPDX-FileCopyrightText: 2024-present Harsh Parekh <harsh@ikigailabs.io>
#
# SPDX-License-Identifier: MIT

import math
import random
from typing import Any, Callable

import pandas as pd
import pytest
from faker import Faker
from ikigai import Ikigai

ColumnNames = list[str]
ColumnGenerator = Callable[[], Any]
ColumnGenerators = list[ColumnGenerator]
TableGenerator = tuple[ColumnNames, ColumnGenerators]


def create_table_generator(fake: Faker, k: int) -> TableGenerator:
    """
    Return a table generator that generates a table with randomly selected columns
    where, k <= number of columns <= 2k
    """
    available_column_generators: list[list[tuple[str, ColumnGenerator]]] = [
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

    table_column_names: ColumnNames = []
    table_column_generators: ColumnGenerators = []
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


def generate_df(table_generator: TableGenerator, num_rows: int) -> pd.DataFrame:
    column_names, column_generators = table_generator
    rows = [[gen() for gen in column_generators] for _ in range(num_rows)]
    return pd.DataFrame(data=rows, columns=column_names)


@pytest.fixture
def df1(faker: Faker) -> pd.DataFrame:
    num_generator_selections = random.randint(1, 10)
    num_rows = math.ceil(random.triangular(1, 100))
    table_generator = create_table_generator(faker, num_generator_selections)
    return generate_df(table_generator=table_generator, num_rows=num_rows)


@pytest.fixture
def df2(faker: Faker) -> pd.DataFrame:
    num_generator_selections = random.randint(1, 10)
    num_rows = math.ceil(random.triangular(1, 100))
    table_generator = create_table_generator(faker, num_generator_selections)
    return generate_df(table_generator=table_generator, num_rows=num_rows)


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
