# ikigai

[![PyPI - Version](https://img.shields.io/pypi/v/ikigai.svg)](https://pypi.org/project/ikigai)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ikigai.svg)](https://pypi.org/project/ikigai)
[![Python Tests](https://github.com/ikigailabs-io/ikigai/actions/workflows/python-package.yml/badge.svg?branch=main)](https://github.com/ikigailabs-io/ikigai/actions/workflows/python-package.yml)

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
- [Finding a Flow from an App](#finding-a-flow-from-an-app)
- [Running a Flow](#running-a-flow)
- [Getting the Status of a Flow](#getting-the-status-of-a-flow)
- [License](#license)

## Ikigai Platform Overview

The Ikigai Python library provides access to
[Ikigai's Platform API](https://docs.ikigailabs.io/api/platform-api)
from applications written in the Python language.

Ikigai enables you to build artificial intelligence apps, or AI apps,
that support business intelligence, machine learning and operational actions.

Apps are the basic organizational units in Ikigai. Apps are much like folders
and they contain all the components that work together to produce your desired
output. An app includes Connectors, Datasets, Flows, Dashboards, and Models.
You begin by creating an app, and then connecting to data. The data can exist
in a variety of forms, such as records in a database, information in a
spreadsheet or data in an application. To connect to different sources
of data, you use connectors.

Once you can access data, you create flows, which are pipelines to process and
transform the data. In each flow you can add pre-built building-blocks that
perform operations on your data. These building-blocks are called facets.
With flows, you can store rules which restrict who can access data, define
how data should appear in a standardized form and transform data so it’s easier
to analyze. Flows are reusable, which means you or others can define them once
and apply them to other apps.

## Getting an API Key

The library needs to be configured with your account's API key which is
available by logging into the Ikigai platform. To generate your API key
follow the steps below.

1. Once logged in, go to your account, under
**Profile** > **Account**.

1. Select the Keys option.

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
requires your user email and the API key that you generated in the previous
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
example stores the `[INPUT]` dataset in the `datasaet` variable. Next, use the
`describe()` method to view a dictionary containing all the dataset's details.

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
the `[INPUT]` dataset in the `datasaet` variable. Then, download the dataset to
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
the `[INPUT]` dataset in the `datasaet` variable. Then, download the dataset as
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

### Flows

Flows are data automations that you can build by connecting elements known as
facets. Flows ingest data, transform data, and then output data. Flows can do
anything from data cleaning to forecasting, scenario analysis, optimizing
decisions, creating alerts, and more. This is where all of our data cleaning,
prepping, and processing happen.

#### Finding a Flow from an App

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

#### Running a Flow

The example snippet shows you how to run a flow that is used by your app.
First, get all the flows that belong to the app. The example uses the `flows()`
method to retrieve all the flows that are stored in the `app` variable and
stores them in a variable named `flows`. The example uses the `flows()` method
to get all the flows stored in the `app` variable and stores them in a variable
named `flows`. Now, retrieve the specific flow. The example gets the flow named
`new flow` and stores it in the `flow` variable. Finally, run the flow by
calling the `.run()` method.

```py
flows = app.flows()        # Get all flows in the app
flow = flows["new flow"]   # Get flow named "new flow"

flow.run()                 # Run the flow
```

When the run is successful, the output resembles the following example:

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

#### Getting the Status of a Flow

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
