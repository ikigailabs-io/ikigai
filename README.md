# ikigai

[![PyPI - Version](https://img.shields.io/pypi/v/ikigai.svg)](https://pypi.org/project/ikigai)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ikigai.svg)](https://pypi.org/project/ikigai)
[![Checks](https://github.com/ikigailabs-io/ikigai/actions/workflows/checks.yml/badge.svg)](https://github.com/ikigailabs-io/ikigai/actions/workflows/checks.yml)

-----

## Table of Contents

- [Ikigai Platform Overview](#ikigai-platform-overview)
- [Getting an API Key](#getting-an-api-key)
- [Requirements](#requirements)
- [Installation](#installation)
- [Creating an Ikigai Client](#creating-an-ikigai-client)
- [Examples](#examples)
- [Apps](#apps)
- [Listing All Apps](#listing-all-apps)
- [Showing Details of an App](#showing-details-of-an-app)
- [Datasets](#datasets)
- [Finding a Dataset from an App](#finding-a-dataset-from-an-app)
- [Showing Details of a Dataset](#showing-details-of-a-dataset)
- [Downloading Your Existing Dataset](#downloading-your-existing-dataset)
- [Creating a New Dataset](#creating-a-new-dataset)
- [Updating a Dataset](#updating-a-dataset)
- [Flows](#flows)
- [Models](#models)
- [Listing All Models](#listing-all-models)
- [Showing Details of a Model](#showing-details-of-a-model)
- [Listing All Versions of a Model](#listing-all-versions-of-a-model)
- [Showing Details of a Model Version](#showing-details-of-a-model-version)
- [Model Types](#model-types)
- [Getting Help with Model Types](#getting-help-with-model-types)
- [Creating a New Model](#creating-a-new-model)
- [Flows](#flows)
- [Facet Types](#facet-types)
- [Getting Help with Facet Types](#getting-help-with-facet-types)
- [Building a Flow Definition](#building-a-flow-definition)
- [Adding and Configuring a Model Facet](#adding-and-configuring-a-model-facet)
- [Flow Builder and Facet Builder Objects](#flow-builder-and-facet-builder-objects)
- [Adding and Configuring a Facet](#adding-and-configuring-a-facet)
- [Chaining Facets](#chaining-facets)
- [Creating a Branch in the Flow](#creating-a-branch-in-the-flow)
- [Creating a New Flow](#creating-a-new-flow)
- [Running a Flow](#running-a-flow)
- [Finding a Flow from an App](#finding-a-flow-from-an-app)
- [Running a Flow](#running-a-flow)
- [Getting the Status of a Flow](#getting-the-status-of-a-flow)
- [License](#license)

## Ikigai Platform Overview

The Ikigai Python library provides access to
[Ikigai's Platform API](https://docs.ikigailabs.io/api/platform-api)
for applications written in the Python language.

Ikigai enables you to build artificial intelligence apps, or AI apps,
that support business intelligence, machine learning and operational actions.

Apps are the basic organizational units in Ikigai. Apps are much like folders
and they contain all the components that work together to produce your desired
output. An app includes Connectors, Datasets, Flows, Dashboards, and Models.
You begin by creating an app, and then connecting to data. The data can exist
in a variety of forms, such as records in a database, information in a
spreadsheet or data in an application. To connect to different sources
of data, you use connectors.

Once you can access data, you create flows, which are pipelines that process and
transform data. In each flow you can add pre-built building-blocks that
perform operations on your data and generate insights using machine learning
models. These building-blocks are called facets. With flows, you can store rules
which restrict who can access data, define how data should appear in a
standardized form and transform data so it’s easier to analyze. Flows are
reusable, which means you or others can define them once and apply them to other
apps.

## Getting an API Key

The library needs to be configured with your account's API key which is
available by logging into the Ikigai platform. To generate your API key
follow the steps below.

1. Once logged in, go to your account, under
**Profile** > **Account**.

1. Select the **Keys** option.

1. Click **Generate API Key** to generate a unique API key.

1. Click the **Eye icon** to reveal the API key. Save this key in a
secure place and do not share it with anyone else. You will need this
API key to use Ikigai's Python client library in the next sections.

## Requirements

You should have the latest stable version of Python installed in your
environment (~3.12) to use Ikigai's Python client library. Ikigai will
support Python version 3.9 until it's
[EOL (October 31, 2025)](https://endoflife.date/python).

## Installation

Use the [Python Package Index (PyPI)](https://pypi.org/) to install the Ikigai
client library with the following command:

```sh
pip install ikigai
```

### Creating an Ikigai Client

In this section, you create the Ikigai client. The code snippet first imports
the Ikigai library. Then, a new `Ikigai()` object is created. This object
requires your **user email** and the **API key** that you generated in the previous
section.

```py
from ikigai import Ikigai

ikigai = Ikigai(user_email="bob@example.com", api_key="my-ikigai-api-key")
```

## Examples

Once you have initiated the Ikigai client, you have access to all Ikigai
components that are exposed by the Python library. The sections below provide
examples for each component and common actions you might perform with each one.

### Apps

Apps are the basic organizational units in Ikigai. Apps contain all the
components that will work together to produce your desired output.

#### Listing All Apps

The code snippet below gets all the apps that are accessible by your account and
stores them in the `apps` variable. Then, it uses a loop to print each app.

```py
apps = ikigai.apps()       # Get all apps accessible by you
for app in apps.values():  # Print each app
    print(app)
```

The output resembles the following example:

```py
Start Here (Tutorial)
Example Project
proj-1234
```

#### Showing Details of an App

The code snippet below gets all the Apps that your account can access and stores
them in the `apps` variable. Then, it gets the app named `my app` and stores it
in the `app` variable. Finally, it prints details about the app, using the
`describe()` method.

```py
apps = ikigai.apps()
app = apps["my app"]       # Get the app named "my app"
print(app.describe())      # Print the details of my app
```

The output resembles the following example:

```py
{
    'app': {
        'app_id': '12345678abcdef',
        'name': 'Start Here (Tutorial)',
        'owner': 'bob@example.com',
        'description': '',
        'created_at': datetime.datetime(
            2024, 12, 13, 20, 0, 52, tzinfo=TzInfo(UTC)
        ),
        'modified_at': datetime.datetime(
            2024, 12, 13, 20, 0, 52, tzinfo=TzInfo(UTC)
        ),
        'last_used_at': datetime.datetime(
            2025, 1, 23, 18, 30, 7, tzinfo=TzInfo(UTC)
        )
    },
    'components': {
        'charts': [
            {
                'chart_id': '88888888fffffff',
                'name': 'Dataset: Sample Chart',
                'project_id': 'abcdefg123456',
                'dataset_id': '4444444bbbbbbb',
                'superset_chart_id': '40929',
                'data_types': {}
            },
            {
                'chart_id': '9999999ggggggg',
                'name': 'Dataset: New Dataset',
                'project_id': 'abcdefg123456',
                'dataset_id': '987654zyxwvu',
                'superset_chart_id': '40932',
                'data_types': {}
            }
        ]
    }
}

...
  'dataset_directories': [{'directory_id': '33333333iiiiiiii',
    'name': '[OUTPUT]',
    'type': 'DATASET',
    'project_id': 'abcdefg123456',
    'parent_id': '',
    'size': '0'},
   {'directory_id': '7777777ggggggg',
    'name': '[INPUT]',
    'type': 'DATASET',
    'project_id': 'abcdefg123456',
    'parent_id': '',
    'size': '0'}],
  'database_directories': [],
  'pipeline_directories': [],
  'model_directories': [],
  'external_resource_directories': []}}
```

### Datasets

Datasets are any data files stored in the Ikigai platform. You can upload your
files to Ikigai to create a dataset. Ikigai supports various file types such as
CSV, and Pandas DataFrame.

#### Finding a Dataset from an App

The code snippet below gets all the apps that your account can access and stores
them in the `apps` variable. Then, it gets the app named `my app` and stores it
in the `app` variable. You can now access all datasets that are associated with
`my-app`. The code stores all the datasets in the `datasets` variable. Next, it
access the dataset named `my-dataset` and stores it in the `dataset` variable
and prints its contents.

```py
apps = ikigai.apps()
app = apps["my app"]              # Get the app named "my app"
datasets = app.datasets()         # Get all datasets in my app
dataset = datasets["my dataset"]  # Get dataset named "my dataset"
print(dataset)
```

The output resembles the following example:

```py
Dataset(
    app_id='12345678abcdef',
    dataset_id='4444444bbbbbbb',
    name='Dataset: New Dataset',
    filename='example.csv',
    file_extension='csv',
    data_types={
        'Channel/Location': ColumnDataType(
            data_type=<DataType.CATEGORICAL: 'CATEGORICAL'>,
            data_formats={}
        ),
        'Product (name/description)': ColumnDataType(
            data_type=<DataType.TEXT: 'TEXT'>,
            data_formats={}
        ),
        'Quantity': ColumnDataType(
            data_type=<DataType.NUMERIC: 'NUMERIC'>,
            data_formats={}
        ),
        'SKU/Unique Item ID': ColumnDataType(
            data_type=<DataType.TEXT: 'TEXT'>,
            data_formats={}
        )
    },
    size=311,
    created_at=datetime.datetime(2024, 1, 1, 20, 0, 55, tzinfo=TzInfo(UTC)),
    modified_at=datetime.datetime(2024, 1, 1, 22, 0, 55, tzinfo=TzInfo(UTC))
)
```

#### Showing Details of a Dataset

The example snippet shows you how to display details related to a dataset.
First, get all datasets stored in a particular app. The example stores all
datasets in the `datasets` variable. Next, store the dataset in a variable. The
example stores the `[INPUT]` dataset in the `dataset` variable. Next, use the
`.describe()` method to view a dictionary containing all the dataset's details.

```py
datasets = app.datasets()             # Get all datasets in the app
dataset = datasets["[INPUT]"]         # Get dataset named "[INPUT]"
dataset.describe()
```

The output resembles the following example:

```py
{
    'dataset_id': '4444444bbbbbbb',
    'name': 'Start Here (Tutorial)',
    'project_id': 'abcdefg123456',
    'filename': 'example.csv',
    'data_types': {
        'Channel/Location': {
            'data_type': 'CATEGORICAL',
            'data_formats': {}
        },
        'Product (name/description)': {
            'data_type': 'TEXT',
            'data_formats': {}
        },
        'Quantity': {
            'data_type': 'NUMERIC',
            'data_formats': {}
        },
        'SKU/Unique Item ID': {
            'data_type': 'TEXT',
            'data_formats': {}
        }
    },
    'directory': {
        'directory_id': '33333333iiiiiiii',
        'name': '',
        'type': 'DATASET',
        'project_id': ''
    },
}

```

#### Downloading Your Existing Dataset

The example snippet shows you how to download an existing dataset. First, get
all datasets stored in a particular app. The example stores all datasets in the
`datasets` variable. Next, store the dataset in a variable. The example stores
the `[INPUT]` dataset in the `dataset` variable. Then, download the dataset to
a Pandas DataFrame. You can pass an argument to the `.head()` method to
designate how many rows of the dataset to display (i.e. `df.head(10)`). By
default, the method displays the first 5 rows of the dataset.

```py
datasets = app.datasets()             # Get all datasets in the app
dataset = datasets["[INPUT]"]         # Get dataset named "[INPUT]"
df = dataset.df()                     # Download dataset as a pandas dataframe

df.head()
```

The output resembles the following example:

| Product (name/description) | SKU/Unique Item ID    | Channel/Location | Qty |
|----------------------------|-----------------------|------------------|-----|
| Chocolate Chip Cookie      | Chocolate_C123_Am     | Amazon           | 166 |
| Snickerdoodle Cookie       | Snickerdoodle_C123_Am | Amazon           | 428 |
| Ginger Cookie              | Ginger_C123_Am        | Amazon           | 271 |
| Sugar Cookie               | Sugar_C123_Am         | Amazon           | 421 |
| Double Chocolate Cookie    | Double_C123_Am        | Amazon           | 342 |

#### Creating a New Dataset

The example snippet shows you how to create a new dataset using a Panda's
DataFrame. First, create a new DataFrame object. The example stores the new
DataFrame object in the `df` variable. Next, build a new dataset named
`New Dataset` using the data stored in the `df` variable. Calling the
`new_dataset` variable returns details about the dataset.

```py
df = pd.DataFrame({"Name": ["Alice", "Bob"], "Age": [25, 30]})
# Build a new dataset named "New Dataset" with data df
new_dataset = app.dataset.new("New Dataset").df(df).build()

new_dataset
```

The output resembles the following example:

```py

Dataset(
    app_id='12345678abcdef',
    dataset_id='3232323yyyyyyy',
    name='New Dataset',
    filename='new-example.csv',
    file_extension='csv',
    data_types={
        'Channel/Location': ColumnDataType(
            data_type=<DataType.CATEGORICAL: 'CATEGORICAL'>,
            data_formats={}
        ),
        'Product (name/description)': ColumnDataType(
            data_type=<DataType.TEXT: 'TEXT'>,
            data_formats={}
        ),
        'Quantity': ColumnDataType(
            data_type=<DataType.NUMERIC: 'NUMERIC'>,
            data_formats={'numeric_format': 'INTEGER'}
        ),
        'SKU/Unique Item ID': ColumnDataType(
            data_type=<DataType.TEXT: 'TEXT'>,
            data_formats={}
        )
    },
    size=305,
    created_at=datetime.datetime(2025, 1, 23, 18, 22, 2, tzinfo=TzInfo(UTC)),
    modified_at=datetime.datetime(2025, 1, 23, 18, 22, 9, tzinfo=TzInfo(UTC))
)

```

#### Updating a Dataset

The example snippet shows you how to update an existing dataset. First, get all
datasets stored in a particular app. The example stores all datasets in the
`datasets` variable. Next, store the dataset in a variable. The example stores
the `[INPUT]` dataset in the `dataset` variable. Then, download the dataset as
a Pandas DataFrame. The code stores the DataFrame in the `df` variable. Now, you
can update the DataFrame using the `.columns()` method. The example uses the
`.columns()` method to drop the last column in the DataFrame. It stores the
updated DataFrame in a new variable named `new_dataset`. Finally, update the
dataset with the new data using the `.edit_data()` method. To complete this pass
in the DateFrame `df_updated` as an argument of the `.edit_data()` method.
Display the data in the new dataset using the `.head()` method.

```py
datasets = app.datasets()             # Get all datasets in Start the app
dataset = datasets["[INPUT]"]         # Get dataset named "[INPUT]"
df = dataset.df()                     # Download dataset as a a pandas dataframe
df_updated = df[df.columns[:-1]]      # New dataframe (by dropping last column)
dataset.edit_data(df_updated)         # Update the dataset

dataset.df().head()
```

The output resembles the following example:

| Product (name/description) | SKU/Unique Item ID     | Channel/Location |
|----------------------------|------------------------|------------------|
| Chocolate Chip Cookie      | Chocolate_C123_Am      | Amazon           |
| Snickerdoodle Cookie       | Snickerdoodle_C123_Am  | Amazon           |
| Ginger Cookie              | Ginger_C123_Am         | Amazon           |
| Sugar Cookie               | Sugar_C123_Am          | Amazon           |
| Double Chocolate Cookie    | Double_C123_Am         | Amazon           |

## Models

Ikigai's machine learning models help you understand your datasets and generate
insights from them. Some of the available models are aiMatch for data
reconciliation, aiCast for forecasting, and aiPlan for scenario planning.
Several other commonly used general models are also available, like Clustering,
Decision Trees, Dimensionality Reduction, etc.

The following sections show you how to retrieve information about all models
available on the platform, create a model, and view model version information.

**Note**: Once a model is created, you can add it to a flow definition and
configure its parameters and settings. See the [Flows](#flows) section for more
details.

### Listing All Models

To list all the models associated with an app, you can call the `.models()`
method on the app.

```py
models = app.models()
for model in models.values():
    print(model)
```

The `.models()` method returns information like the model's name, associated
app id, and the model type.

```py
Model(app_id='aB3k9QeL',
      model_id='Z7x4KpQ2',
      name='example_1',
      model_type='Ai Match',
      sub_model_type='Supervised',
      description='',
      created_at='1715274391',
      modified_at='1715274434')

Model(app_id='T5rLm2Nx',
      model_id='gQ81FvBz',
      name='example_2',
      model_type='Time Series',
      sub_model_type='Additive',
      description='',
      created_at='1665850269',
      modified_at='1695397961')

Model(app_id='H3w9UdCy',
      model_id='pKo4vB2W',
      name='example_3',
      model_type='Ai Match',
      sub_model_type='Supervised',
      description='',
      created_at='1697750506',
      modified_at='1732137362')

Model(app_id='N8zGyV5d',
      model_id='La2fKv9M',
      name='example_4',
      model_type='Ai Match',
      sub_model_type='Unsupervised',
      description='',
      created_at='1709310584',
      modified_at='1709310584')
...
```

### Showing Details of a Model

To view a model's details, use the model object's `.describe()` method.

```py
model = app.models()["example_1"]
print(model.describe())
```

The model object's `.describe()` method returns details, like when the model was
created, directory information, model type, and more.

```py
{'created_at': '1715274391',
 'description': 'example 1',
 'directory': {'directory_id': '',
               'name': '',
               'parent_id': '',
               'project_id': '',
               'size': '0',
               'type': 'MODEL'},
 'latest_version_id': '2E3CDzWf',
 'model_id': 'Z7x4KpQ2',
 'model_type': 'Linear',
 'modified_at': '1661814764',
 'name': 'iris_demo',
 'project_id': 'xP7aL2qZ',
 'sub_model_type': 'Base'}
```

### Listing All Versions of a Model

When you last run a flow, a snapshot of the model is created. This preserves all
of the insights generated by the model and the parameters that generated those
insights. To view all of a model object's versions, use the `.versions()`
method.

```py
versions = model.versions()
for version in versions.values():
    print(version)
```

The `.versions()` method returns information like the version ID, the
hyperparameters that were used when the version was created, the metrics
generated by the model, and several other details.

```py
ModelVersion(
    app_id='X9b2LpQw',
    model_id='M4Nz8VxY',
    version_id='Rt5HsJ2K',
    version='Demo',
    hyperparameters={
        'C': 1,
        'class_weight': None,
        'dual': False,
        'fit_intercept': True,
        'intercept_scaling': 1,
        'l1_ratio': None,
        'max_iter': 100,
        'multi_class': 'auto',
        'n_jobs': None,
        'penalty': 'l2',
        'random_state': None,
        'solver': 'lbfgs',
        'tol': 0.0001,
        'verbose': 0,
        'warm_start': False
    },
    metrics={
        'feature_importance': {},
        'performance': {
            'accuracy': {
                'average_test': 0.96,
                'average_train': 0.9666666666666667
            }
        }
    },
    created_at='1661814764',
    modified_at='1690303863'
)
```

### Showing Details of a Model Version

To view a model version's details, call the `ModelVersion` object's
`.describe()` method.

```py
model_version = model.versions()["Demo"]
print(model_version.describe())
```

The `.describe()` method returns all of the details associated with the specific
model version.

```py
{
    'created_at': '1661814764',
    'hyperparameters': {
        'C': 1,
        'class_weight': None,
        'dual': False,
        'fit_intercept': True,
        'intercept_scaling': 1,
        'l1_ratio': None,
        'max_iter': 100,
        'multi_class': 'auto',
        'n_jobs': None,
        'penalty': 'l2',
        'random_state': None,
        'solver': 'lbfgs',
        'tol': 0.0001,
        'verbose': 0,
        'warm_start': False
    },
    'metrics': {
        'feature_importance': {},
        'performance': {
            'accuracy': {
                'average_test': 0.96,
                'average_train': 0.9666666666666667
            }
        }
    },
    'model_id': 'M4Nz8VxY',
    'modified_at': '1690303863',
    'version': 'Demo',
    'version_id': 'Rt5HsJ2K'
}
```

### Model Types

Before creating a new model, you may want to view a list of available models in
the Ikigai Python library. Use the `types` property of `model_types` to see the
names of the available models.

```py
model_types = ikigai.model_types
print(model_types.types)
```

The `types` property returns a list of all available Ikigai models.

```py
['Ai Cast',
 'Ai Llm',
 'Ai Match',
 'Ai Predict',
 'Anomaly Detection',
 'Change Point Detection',
 'Clustering',
 'Decision Trees',
 'Decomposition',
 'Dimensionality Reduction',
 'Embedding',
 'Estimators',
 'Gaussian Process',
 'Imputation',
 'Linear',
 'Llms',
 'Matrix Completion',
 'Naive Bayes',
 'Nearest Neighbors',
 'Reconciliation',
 'Supply Chain',
 'Svm',
 'Time Series',
 'Vectorizer']
```

#### Getting Help with Model Types

Each model supports a variety of parameters and hyperparameters that
influence its behavior and performance. These settings allow you to control a
model’s processing behavior, evaluation metrics, sub-model configuration, and
fine-tuning process. Consult a model's help text prior to creating a
new model instance.

To view the help text for all models in the Ikigai Python library, call the
`.help()` method on the `ModelTypes` object.

```py
# Help on all model types
print(model_types.help())
```

The `.help()` method returns text showing the information for every model
available in the Ikigai Python library. The example output is shortened for
brevity.

```py
Ai Cast:
  keywords: ['AI', 'cast', 'time series', 'auto', 'ML', 'AiCast']
  sub-model types:
    Base:
      keywords: ['base']
      metrics:
        feature_importance: {}
        performance: {
            '0': {
                'name': 'weighted_mean_absolute_percentage_error',
                'parameters': {
                    '0': {
                        'default_value': 0.5,
                        'have_options': False,
                        'is_deprecated': False,
                        'is_hidden': False,
                        'is_list': False,
                        'name': 'overforecast_weight',
                        'options': [],
                        'parameter_type': 'NUMBER'
                    }
                },
                'target_column_data_types': ['NUMERIC', 'TIME']
            },
            '1': {
                'name': 'mean_absolute_percentage_error',
                'parameters': {
                    '0': {
                        'default_value': 0.5,
                        'have_options': False,
                        'is_deprecated': False,
                        'is_hidden': False,
                        'is_list': False,
                        'name': 'overforecast_weight',
                        'options': [],
                        'parameter_type': 'NUMBER'
                    }
                },
                'target_column_data_types': ['NUMERIC', 'TIME']
            },
            ...
        }
      parameters:
        time_column: TEXT
        identifier_columns: list[TEXT]
        value_column: TEXT
        mode: TEXT = 'train'
          options=[train|fine_tune|inference|retrain_inference]
      hyperparameters:
        type: TEXT = 'base'  options=[base|hierarchical]
        hierarchical_type: TEXT = 'bottom_up'
          options=[
            bottom_up|
            top_down|
            spatio_temporal_hierarchical|
            spatio_temporal_grouped|
            spatio_hierarchical|
            spatio_grouped
          ]
        models_to_include: list[TEXT] = ['Additive', 'Lgmt1', 'Sma', 'Sarimax']
          options=[
            Additive|
            Sma|Deepar|
            Lgmt1|
            Last_Interval|
            Lgm-S|Lgbm|
            Random_Forest|
            Lasso|
            Holt_Winters|
            Croston|
            Sarimax
          ]
        eval_method: TEXT = 'cv'  options=[cv|holdout]
        time_budget: NUMBER = 100
        computation_budget: NUMBER = 100
        enable_parallel_processing: BOOLEAN = False
        best_model_only: BOOLEAN = True
        confidence: NUMBER = 0.7
        fine_tune: list[MAP] = {
          filter: list[TEXT] = ''
          growth: NUMBER = 0
          hyperparameters: MAP = {}
          scaling: NUMBER = 1
          sub_model_type: TEXT = ''
            options=[
                Additive|
                Sma|
                Deepar|
                Lgmt1|
                Last_Interval|
                Lgm-S|Lgbm|
                Random_Forest|
                Lasso|
                Holt_Winters|
                Croston|
                Sarimax
            ]
        }
        experiment_selection: MAP = {}
        return_all_levels: BOOLEAN = False
        fill_missing_values: TEXT = 'forward_fill'
          options=[
            forward_fill|
            mean|
            linear|
            zero
          ]
        drop_threshold: NUMBER = 0.9
        include_reals: BOOLEAN = True
        nonnegative: BOOLEAN = False
        interval_to_predict: NUMBER = 10
        metric: TEXT = 'mean_absolute_percentage_error'
          options=[
            mean_absolute_percentage_error|
            mean_absolute_error|
            mean_squared_error|
            weighted_mean_absolute_percentage_error
          ]
Ai Llm:
  keywords: ['ai', 'llm', 'predict']
  sub-model types:
    Classification:
      keywords: ['classification']
      metrics:
        feature_importance: {}
        performance: {}
      parameters:
        target_column: TEXT
      hyperparameters:
        No hyperparameters
    Regression:
      keywords: ['Regression']
      metrics:
        feature_importance: {}
        performance: {}
      parameters:
        target_column: TEXT
      hyperparameters:
        No hyperparameters
    Question Answer:
      keywords: ['Question Answer']
      metrics:
        feature_importance: {}
        performance: {}
      parameters:
        No parameters
      hyperparameters:
        No hyperparameters
    Custom:
      keywords: ['custom']
      metrics:
        feature_importance: {}
        performance: {}
      parameters:
        No parameters
      hyperparameters:
        nearest_neighbors: BOOLEAN = True
        is_json: BOOLEAN = False
        system_context_template: TEXT = ''
        train_unique_output_options_column: TEXT = ''
        query_unique_output_options_column: TEXT = ''
        prompt_template: TEXT = ''
        nearest_neighbor_input_columns: list[TEXT] = ''
        nearest_neighbor_output_column: TEXT = ''
        predict_input_columns: list[TEXT] = ''
    Chat:
      keywords: ['Chat']
      metrics:
        feature_importance: {}
        performance: {}
      parameters:
        No parameters
      hyperparameters:
        new_chat: BOOLEAN = False
        instructions: TEXT = 'You are a friendly chatbot that answers questions'
    Summary:
      keywords: ['Summary']
      metrics:
        feature_importance: {}
        performance: {}
      parameters:
        No parameters
      hyperparameters:
        instructions: TEXT = 'Summarize the information given'
    Generate:
      keywords: ['Generate']
      metrics:
        feature_importance: {}
        performance: {}
      parameters:
        No parameters
      hyperparameters:
        instructions: TEXT = 'Follow instructions to generate information'
        reference_scope: TEXT = 'nearest_neighbors'
          options=[
            nearest_neighbors|
            entire_dataset
          ]
        output_json: BOOLEAN = False
        number_of_generations: NUMBER = 1
        add_ranking: BOOLEAN = False
        temperature: NUMBER = 0
    Flow Search:
      keywords: ['Flow Search', 'Flow to Description']
      metrics:
        feature_importance: {}
        performance: {}
      parameters:
        No parameters
      hyperparameters:
        No hyperparameters
...
```

View the help text for a specific model type by calling its `.help()` method.

```py
# Help for a specific model type
print(model_types.AI_CAST.help())
```

The code returns aiCast's help text including its associated keywords, sub-model
types, settings, parameters, and hyperparameters. The example help text is
clipped for brevity.

```py
Ai Cast:
    keywords: ['AI', 'cast', 'time series', 'auto', 'ML', 'AiCast']
    sub-model types:
      Base:
        keywords: ['base']
        metrics:
          feature_importance: {}
          performance: {
            '0': {
              'name': 'weighted_mean_absolute_percentage_error',
              'parameters': {
                '0': {
                  'default_value': 0.5,
                  'have_options': False,
                  'is_deprecated': False,
                  'is_hidden': False,
                  'is_list': False,
                  'name': 'overforecast_weight',
                  'options': [],
                  'parameter_type': 'NUMBER'
                }
              },
              'target_column_data_types': ['NUMERIC', 'TIME']
            },
...
```

You can also view help text for a specific sub-model type by calling its
`.help()` method.

```py
# Help for a specific sub-model type
print(model_types.Linear.Lasso.help())
```

The `.help()` method in the example snippet returns the help text for the
`Lasso` sub-model.

```py
Lasso:
  keywords: ['lasso', 'linear']
  metrics:
    feature_importance:
      {
        '0': {'name': 'shapley'},
        '1': {'name': 'permutation'},
        '2': {'name': 'linear_base'}
      }
    performance:
      {
        '0': {
          'name': 'r2',
          'parameters': {},
          'target_column_data_types': ['NUMERIC', 'TIME']
        },
        '1': {
          'name': 'neg_mean_absolute_error',
          'parameters': {},
          'target_column_data_types': ['NUMERIC', 'TIME']
        },
        '2': {
          'name': 'neg_mean_squared_error',
          'parameters': {},
          'target_column_data_types': ['NUMERIC', 'TIME']
        },
        '3': {
          'name': 'accuracy',
          'parameters': {},
          'target_column_data_types': ['TEXT', 'CATEGORICAL']
        },
        '4': {
          'name': 'balanced_accuracy',
          'parameters': {},
          'target_column_data_types': ['TEXT', 'CATEGORICAL']
        }
      }
  parameters:
    target_column: TEXT
  hyperparameters:
    alpha: NUMBER = 1
```

### Creating a New Model

To create a new model call the Model class' `.new()` method, specify the model
type using the `.model_type()` method, and then build the model using the
`.build()` method.

```py
model = (
    app.model.new("Simple Linear Regression with Lasso")
    .model_type(model_type=model_types.Linear.Lasso)
    .build()
)
```

After you've built the model it is ready to be used in a flow.

## Flows

A *Flow* is a component in an app that enables you to perform analysis or
computation. Each Flow contains a *Flow Definition* that specifies the
sequence of *Facet Types* that perform actions like ingesting data, transforming
data, machine learning with models, and outputting data. When you have assembled
your flow definition, use the `FlowBuilder` class to build it. After building,
you attach the flow definition to a Flow and run it to execute all of the
defined actions.

### Facet Types

The Ikigai Python library provides several facet types for importing,
outputting, and transforming datasets.

The `INPUT` attribute of the `FacetType` class groups facets that are related to
importing data.

The `MID` attribute of the `FacetType` class groups facets that are related to
transforming data.

The `OUTPUT` attribute of the `FacetType` class groups facets that are related
to exporting data.

Before creating a flow definition, you may want to review the list of all
available facet types in each group. The example code uses the `types` property
to display all facet types for each group.

```py
facet_types = ikigai.facet_types

print(facet_types.INPUT.types)
print(facet_types.MID.types)
print(facet_types.OUTPUT.types)
```

The code returns three lists containing the names of each facet type
available on the Ikigai platform.

```py
['HANA', 'IMPORTED', 'LOAD', 'CUSTOM_FACET', 'INPUT_CONNECTOR', 'PYTHON', 'S3']
['ADD_PRIMARY_KEY',
 'COUNT',
 'CROSS_TAB',
 'DEDUPLICATE',
 'DESCRIBE',
 'DROP_COLUMNS',
 'DROP_MISSING_VALUES',
 'FILL_MISSING_VALUES',
 'FILTER',
 'FIND_REPLACE',
 'FREE_FORM_SQL',
 'INTERPOLATE',
 'KEEP_HEADERS_ONLY',
 'MELT',
 ...
 'S3',
 'SLACK']
```

### Getting Help with Facet Types

Before building a flow definition, you may want to review the help text for the
facet types that you plan to use. The help text displays a facet type's
supported arguments, expected data types, and default values.

In the example, the `.help()` method is called to display the help text for the
`Imported` facet type.

```py
# Help for a specific facet type
print(facet_types.INPUT.Imported.help())
```

The method returns the Imported facet type's help text.

```py
Imported:
  facet_arguments:
    dataset_id: TEXT | None
    use_raw_file: BOOLEAN | None
    script: TEXT
    libraries: list[TEXT]
    file_type: TEXT  options=[csv|xlsx|xls]
    header: BOOLEAN = True
    column_names: list[TEXT]
    header_row_number: NUMBER
    sheet_name: TEXT
    data_types: list[MAP] = [{
      column_name: TEXT | None
      data_formats: list[MAP] = [{
        key: TEXT | None
        value: TEXT | None
      }]
      data_type: TEXT | None  options=[CATEGORICAL|NUMERIC|TEXT|TIME]
    }]
```

### Building a Flow Definition

The flow definition is where you add and configure facet types and model facets.
Once you have created a flow definition, you can build the definition using the
`FlowBuilder` class.

At a high-level, the process for creating a flow definition is the following:

1. Create a new instance of the `FlowBuilder` class.
1. Add facets to the instance of the `FlowBuilder` class.
1. Configure the facets.
1. Build the flow definition.

The following sections describe different ways to create and build flow
definitions.

### Adding and Configuring a Model Facet

A model facet must be created before it can be added to a flow definition. If
you have not created a model, see [Creating a New Model](#creating-a-new-model)
for instructions.

The example code in this section builds the same flow definition shown
in the image below:

![Add model facet example.](add_model_facet.png)

First, create an instance of the `FlowBuilder` class. Then, call the
`.model_facet()` method on a `FacetBuilder` object to configure the model's
arguments, parameters, and hyperparemeters.

In the example, the `Imported` and `Output` facet types are added and their
settings are configured. Each facet is explicitly *chained* to the next. The
chaining order generates the sequence of steps followed by a flow definition

After adding all your facets, build the flow definition by calling the
`.build()` method on any of the `FacetBuilder` objects that you created.

**Note**: The next section demonstrates a less verbose way to create and build a
flow definition. This approach is particularly useful when
[creating a branch in a flow](#creating-a-branch-in-the-flow).

```py
# To add a model facet to the flow, use the `model_facet` method on the facet
# builder. This gives you a ModelFacetBuilder object, which is a subclass of
# FacetBuilder.

flow_builder = ikigai.builder

facet_1 = (
    flow_builder.facet(facet_type=facet_types.INPUT.Imported)
    .arguments(dataset_id="my-input-dataset-id")
    .arguments(
        file_type="csv",
        header=True,
        use_raw_file=False
    )
)

model_facet = (
    facet_1.model_facet(
        facet_type=facet_types.MID.PREDICT,
        model_type=model_types.Linear.Lasso
    )
    .arguments(
        # Refer to the facet type help for list of arguments
        model_name="my-model-name",  # Name of existing model in the app
        model_version="initial"     # Model version to use or train
    )
    .hyperparameters(
        # Refer to the model type help for list of hyperparameters
        alpha=0.1,
        fit_intercept=True
    )
    .parameters(
        # Refer to the model type help for list of model parameters
        target_column="target_column_name"
    )
)

facet_3 = model_facet.facet(
    facet_type=facet_types.OUTPUT.EXPORTED
).arguments(
    dataset_name="my-output-dataset-name",
    file_type="csv",
    header=True
)

# Build the flow definition from any of the facet builders
flow_definition = facet_3.build()

print("Flow Definition:")
print(flow_definition.model_dump(), sort_dicts=False)
```

The `.model_dump()` method returns a dictionary representation of the
flow definition that was built in the code example.

```py
{
    'facets': [
        {
            'facet_id': '513d3056',
            'facet_uid': 'I_005',
            'name': '',
            'arguments': {
                'dataset_id': 'my-input-dataset-id',
                'file_type': 'csv',
                'header': True,
                'use_raw_file': False
            }
        },
        {
            'facet_id': '9146ad13',
            'facet_uid': 'M_016',
            'name': '',
            'arguments': {
                'model_name': 'my-model-name',
                'model_version': 'initial',
                'hyperparameters': {
                    'alpha': 0.1,
                    'fit_intercept': True
                },
                'parameters': {
                    'target_column': 'target_column_name'
                }
            }
        },
        {
            'facet_id': 'ae68b1b3',
            'facet_uid': 'O_005',
            'name': '',
            'arguments': {
                'dataset_name': 'my-output-dataset-name',
                'file_type': 'csv',
                'header': True
            }
        }
    ],
    'arrows': [
        {
            'source': '513d3056',
            'destination': '9146ad13',
            'arguments': {}
        },
        {
            'source': '9146ad13',
            'destination': 'ae68b1b3',
            'arguments': {}
        }
    ],
    'arguments': {},
    'variables': {},
    'model_variables': {}
}
```

### Flow Builder and Facet Builder Objects

The example code instantiates a new `FlowBuilder` object and then
*implicitly chains* three different facets to each other, configures the facets,
and builds the flow definition.

**Note**: Implicitly chaining facets provides a less verbose way to build a flow
definition. For more complex flows, such as those with
[branching](#creating-a-branch-in-the-flow), you may prefer explicit chaining,
as shown in the
[Adding and Configuring a Model Facet](#adding-and-configuring-a-model-facet)
section.

```py
flow_builder = (
    ikigai.builder
)  # Get a new flow builder instance, used to build flow definition

"""
The approach to building a flow is: instantiate a flow builder,
use it to add facets, configure them, and then finally build the flow
definition.
"""
flow_definition = (
    flow_builder
    .facet(
        facet_type=facet_types.INPUT.Imported
    )  # Adds a facet of type Imported
    .arguments(
        dataset_id="my-input-dataset-id",  # Specify the dataset ID to import
        file_type="csv",
        header=True,
        use_raw_file=False,
    )
    .facet(
        facet_type=facet_types.MID.COUNT
    )  # Adds a COUNT facet attached to the previous facet
    .arguments(
        output_column_name="count",
        sort=True,
        target_columns=[  # Specify the columns to count on
            "col1",
            "col2",
        ],
    )
    .facet(
        facet_type=facet_types.OUTPUT.EXPORTED
    )  # Adds an EXPORTED facet to the COUNT facet
    .arguments(
        dataset_name="my-output-dataset-name",  # Name of the output dataset
        file_type="csv",
        header=True,
    )
    .build()
)

print(flow_definition.model_dump(), sort_dicts=False)
```

Calling the `.model_dump()` method returns a dictionary representation of the
flow definition that was built in the code example.

```py
{'facets': [{'facet_id': 'e64b5624',
             'facet_uid': 'I_005',
             'name': '',
             'arguments': {'dataset_id': 'my-input-dataset-id',
                           'file_type': 'csv',
                           'header': True,
                           'use_raw_file': False}},
            {'facet_id': '31376ee2',
             'facet_uid': 'M_003',
             'name': '',
             'arguments': {'output_column_name': 'count',
                           'sort': True,
                           'target_columns': ['col1', 'col2']}},
            {'facet_id': '142d53f3',
             'facet_uid': 'O_005',
             'name': '',
             'arguments': {'dataset_name': 'my-output-dataset-name',
                           'file_type': 'csv',
                           'header': True}}],
 'arrows': [{'source': 'e64b5624', 'destination': '31376ee2', 'arguments': {}},
            {'source': '31376ee2', 'destination': '142d53f3', 'arguments': {}}],
 'arguments': {},
 'variables': {},
 'model_variables': {}}
```

### Adding and Configuring a Facet

To add and configure a facet in a flow definition, first instantiate a new
`FlowBuilder` object. Then use its `.facet()` method to begin adding and
configuring a facet type. You may want to view a facet type’s help text before
adding facets, as demonstrated in the example. Note that the example configures
a few facet arguments at a time.

```py
flow_builder = (
    ikigai.builder
)  # Get a new flow builder instance, used to build a flow definition

# Printing help for the Imported facet type to check supported arguments
print(facet_types.INPUT.Imported.help())

imported_dataset_facet_builder = (
    flow_builder
    .facet(
        facet_type=facet_types.INPUT.Imported  # Add facet of type Imported
    )
    .arguments(  # Specify all required arguments
        dataset_id="my-input-dataset-id",
        file_type="csv",
        header=True,
        use_raw_file=False,
    )
)

# A facet can also be configured by specifying a few arguments at a time
imported_dataset_facet_builder = (
    flow_builder
    .facet(facet_type=facet_types.INPUT.Imported)
    .arguments(dataset_id="my-input-dataset-id")
    .arguments(
        file_type="csv",
        header=True,
        use_raw_file=False
    )
)
```

The example output shows the help text printed by
`print(facet_types.INPUT.Imported.help())`. This output lists all arguments
supported by the `Imported` facet type, helping you determine which ones to set.

```py
Imported:
  facet_arguments:
    dataset_id: TEXT | None
    use_raw_file: BOOLEAN | None
    script: TEXT
    libraries: list[TEXT]
    file_type: TEXT  options=[csv|xlsx|xls]
    header: BOOLEAN = True
    column_names: list[TEXT]
    header_row_number: NUMBER
    sheet_name: TEXT
    data_types: list[MAP] = [{
      column_name: TEXT | None
      data_formats: list[MAP] = [{
        key: TEXT | None
        value: TEXT | None
      }]
      data_type: TEXT | None  options=[CATEGORICAL|NUMERIC|TEXT|TIME]
    }]
```

### Chaining Facets

*Explicitly* chaining facets in your flow definition attaches facets to each
other and generates the sequence of steps followed by a flow definition. The
code below demonstrates explicit facet chaining. This differs from previous
examples that *implicitly* chained facets together. Explicit chaining is
especially useful for more complex flow definitions, like the one demonstrated
in the [Creating a Branch in a Flow](#creating-a-branch-in-the-flow) section.

```py
flow_builder = ikigai.builder

facet_1 = flow_builder.facet(
    facet_type=facet_types.INPUT.Imported
).arguments(
    dataset_id="my-input-dataset-id",
    file_type="csv",
    header=True,
    use_raw_file=False
)

facet_2 = facet_1.facet(
    # Adds a COUNT facet attached to the imported facet (facet_1)
    facet_type=facet_types.MID.COUNT
).arguments(
    output_column_name="count",
    sort=True,
    target_columns=["col1", "col2"]  # Specify the columns to count on
)

facet_3 = facet_2.facet(
    # Adds an EXPORTED facet attached to the previous COUNT facet (facet_2)
    facet_type=facet_types.OUTPUT.EXPORTED
).arguments(
    dataset_name="my-output-dataset-name",  # Name of the output dataset
    file_type="csv",
    header=True
)

# Finally, build the flow definition from either the flow builder or any facet
flow_definition = flow_builder.build()

print("Flow Definition:")
print(flow_definition.model_dump(), sort_dicts=False)
```

Calling the `.model_dump()` method returns a dictionary representation of the
flow definition that was built in the code example.

```py
Flow Definition:
{'facets': [{'facet_id': '873e0503',
             'facet_uid': 'I_005',
             'name': '',
             'arguments': {'dataset_id': 'my-input-dataset-id',
                           'file_type': 'csv',
                           'header': True,
                           'use_raw_file': False}},
            {'facet_id': '857ed9ba',
             'facet_uid': 'M_003',
             'name': '',
             'arguments': {'output_column_name': 'count',
                           'sort': True,
                           'target_columns': ['col1', 'col2']}},
            {'facet_id': '8c05d268',
             'facet_uid': 'O_005',
             'name': '',
             'arguments': {'dataset_name': 'my-output-dataset-name',
                           'file_type': 'csv',
                           'header': True}}],
 'arrows': [{'source': '873e0503', 'destination': '857ed9ba', 'arguments': {}},
            {'source': '857ed9ba', 'destination': '8c05d268', 'arguments': {}}],
 'arguments': {},
 'variables': {},
 'model_variables': {}}
```

### Creating a Branch in the Flow

To create branching in a flow, use the `.add_arrow()` method of the
`FacetBuilder` class. This method connects two different facets
to another single facet. The image below shows an example of branching.

![Add arrows example.](add_arrows_example.png)

The example code recreates the flow definition shown in the image using the
the Ikigai Python library. Notice that the `.add_arrow()` method's `table_side`
argument determines the position of a facet. Explicit facet chaining is required
when a flow includes branching.

```py
flow_builder = ikigai.builder

import_1 = flow_builder.facet(
    facet_type=facet_types.INPUT.Imported
).arguments(
    dataset_id="my-input-dataset-id",
    file_type="csv",
    header=True,
    use_raw_file=False
)  # The first import facet

import_2 = import_1.facet(
    facet_type=facet_types.INPUT.Imported
).arguments(
    dataset_id="my-input-dataset-id-2",
    file_type="csv",
    header=True,
    use_raw_file=False
)  # The second import facet

union_facet = (
    flow_builder.facet(
        facet_type=facet_types.MID.UNION,
        name="union"
    )
    .add_arrow(
        import_1,
        table_side="top"
    )
    .add_arrow(
        import_2,
        table_side="bottom"
    )
    .arguments(
        option="full"
    )
)

flow_definition = (
    union_facet.facet(
        facet_type=facet_types.OUTPUT.EXPORTED
    )
    .arguments(
        dataset_name="my-output-dataset-name",
        file_type="csv",
        header=True
    )
    .build()
)

print("Flow Definition")
print(flow_definition.model_dump(), sort_dicts=False)
```

Calling the `.model_dump()` method returns a dictionary representation of the
flow definition that was built in the code example.

```py
Flow Definition
{'facets': [{'facet_id': '98f5843e',
             'facet_uid': 'I_005',
             'name': '',
             'arguments': {'dataset_id': 'my-input-dataset-id',
                           'file_type': 'csv',
                           'header': True,
                           'use_raw_file': False}},
            {'facet_id': '9177369b',
             'facet_uid': 'I_005',
             'name': '',
             'arguments': {'dataset_id': 'my-input-dataset-id-2',
                           'file_type': 'csv',
                           'header': True,
                           'use_raw_file': False}},
            {'facet_id': '1dd973cc',
             'facet_uid': 'M_019',
             'name': 'union',
             'arguments': {'option': 'full'}},
            {'facet_id': 'c75cfd22',
             'facet_uid': 'O_005',
             'name': '',
             'arguments': {'dataset_name': 'my-output-dataset-name',
                           'file_type': 'csv',
                           'header': True}}],
...
            {'source': '1dd973cc', 'destination': 'c75cfd22', 'arguments': {}}],
 'arguments': {},
 'variables': {},
 'model_variables': {}}
```

### Creating a New Flow

A Flow serves as the container for a flow definition and allows you to execute
its contents. The example creates a new Flow, attaches a flow definition, and
then builds the Flow.

**Note**: Once a Flow is created and built, you can run it on the Ikigai
platform.

```py
now = str(int(time.time()))[-3:]
flow_name = f"Flow Definition Example {now}"

flow = app1.flow.new(name=flow_name).definition(flow_definition).build()
print(flow.model_dump(), sort_dicts=False)

# Visit the flow on the platform
```

The output shows the details of the Flow created in the example code.

```py
{'app_id': '2zYsSJBtkgSVRo8T8uYQIOzhjko',
 'flow_id': '2zYsSUBejbnHMqoOd4Vp6cyR9s7',
 'name': 'Flow Definition Example 340',
 'created_at': datetime.datetime(2025, 7, 7, 20, 15, 40, tzinfo=TzInfo(UTC)),
 'modified_at': datetime.datetime(2025, 7, 7, 20, 15, 40, tzinfo=TzInfo(UTC))}
```

### Running a Flow

To run a flow call the `.run()` method on the flow object that you want to run.

```py
flows = app.flows()        # Get all flows in the app
flow = flows["new flow"]   # Get flow named "new flow"

flow.run()                 # Run the flow
```

When the Flow runs successfully, it returns output similar to the example below.

```py
RunLog(
    log_id='4545454lllllll',
    status=SUCCESS,
    user='bob@example.com',
    erroneous_facet_id=None,
    data='',
    timestamp=datetime.datetime(2025, 1, 1, 11, 0, 5, tzinfo=TzInfo(UTC))
)
```

### Finding a Flow from an App

The example snippet below shows you how to find a specific flow from an existing
app. First, access the app. The example gets the `Start Here (Tutorial)` app and
stores it in a variable named `app`. Next, get all the flows that belong to the
app. The example uses the `flows()` method to get all the app's flows and stores
it in the `flows` variable. Now, retrieve the specific flow. The example gets
the flow named `new flow` and stores it in the `flow` variable. Calling the
`flow` variable prints out details about the flow.

```py
app = apps["Start Here (Tutorial)"]     # Get app named "Start Here (Tutorial)"
flows = app.flows()                     # Get all flows in the app
flow = flows["new flow"]                # Get flow named "new flow"

flow
```

The output resembles the following example:

```py
Flow(
    app_id='12345678abcdef',
    flow_id='6666666hhhhhhh',
    name='new flow',
    created_at=datetime.datetime(2025, 1, 1, 10, 0, 30, tzinfo=TzInfo(UTC)),
    modified_at=datetime.datetime(2025, 1, 1, 11, 0, 30, tzinfo=TzInfo(UTC))
)
```

### Getting the Status of a Flow

The example snippet shows you how to view the status of an existing flow. First,
get all the flows that belong to the app. The example uses the `flows()` method
to get all the flows stored in the `app` variable and stores them in a variable
named `flows`. Now, retrieve the specific flow. The example gets the flow named
`new flow` and stores it in the `flow` variable. To view the flow's status use
the `status()` method.

```py
flows = app.flows()         # Get all flows in the app
flow = flows["new flow"]    # Get flow named "new flow"

flow.status()               # Get the status of the flow
                            #(IDLE: currently the flow is not running)
```

When the flow is NOT running, you should see a similar output:

```py
FlowStatusReport(
    status=IDLE,
    progress=None,
    message=''
)
```

## Troubleshooting

If you receive the following error message related to your authentication token,
you may need to restart your Python Kernel:

```py
{"message":"Missing Authentication Token"}
```

Press **Ctrl+D** or type **exit** to exit IPython, then run it again:

```bash
ipython
```

For JupyterLab:

- Navigate to the **Kernel menu**, select **Restart Kernel**, and confirm the
  restart if prompted.

For Google Colab:

- Navigate to the **Runtime menu** and select **Restart session**.

Others Python interpreters:

- Refer to the documentation of your Python Notebook software.

## License

- `ikigai` is distributed under the terms of the
  [MIT](https://spdx.org/licenses/MIT.html) license.
