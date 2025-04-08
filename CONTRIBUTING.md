# ikigai

**Table of Contents**

- [Types of Contributions](#types-of-contributions)
- [Getting Started](#getting-started)
- [Tips and Tricks](#tips-and-tricks)

## Types of Contributions

Currently we are accepting limited external contribution but as we feel more
confident in the direction of the library we will open up more avenue for contribution.

### Report Bugs

Report bugs by dropping an email to [harsh](mailto:harsh@ikigailabs.io) or [jae](mailto:simjae@ikigailabs.io).

If you are reporting a bug, please include:

- Your installed ikigai package version, operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug including any relevant code snippets or setup on the ikigai platform.
- Any tracebacks that were encountered and the expected outcome.

### Submit Feedback

If you would like to request some feature or QOL improvements to the library you can send us an email requesting the feature.

When proposing a feature please:

- Explain in detail how you would like it to work; what usecase does it enable or simplify?
- Try to keep the scope as detailed and narrow as possible to improve turn-around times.

## Getting Started

Ready to contribute to the library? Here's the steps to get you started with developing the library and testing it locally.
We use [hatch](https://hatch.pypa.io/latest/) as the project manager that handles the development environment, tests, and builds for the project.

To install hatch follow the instructions provided for your system [here](https://hatch.pypa.io/latest/install/).

To verify that you have hatch install correctly run:

```sh
$ hatch --version
Hatch, version 1.X.X
```

Next you should clone the repo locally with:

```sh
git clone git@bitbucket.org:ikigailabs/ikigai_client.git
cd ikigai_client
```

Let's get a quick run-down of the structure of the project:

```txt
.
├── LICENSE.txt          // Licensing info for the package
├── CONTRIBUTING.md      // <-- You are here!
├── README.md
├── pyproject.toml       // Configuration file for the package
├── src/ikigai           // Source code of the package
│   ├── __about__.py     // Package metadata such as version, ...
│   ├── __init__.py
│   ├── components
│   └── ikigai.py        // File containing the main Ikigai client class
└── tests                // Folder containing tests for the package
    ├── __init__.py
    ├── conftest.py      // Fixtures & config for all tests
    ├── components
    └── test_ikigai.py
```

Now, let's setup the pre-commit hooks to automatically format the code and run linters when you commit changes.
Install the pre-commit tool by following the [official instructions](https://pre-commit.com/#install).
After installing pre-commit, run the following command to install the hooks:

```sh
pre-commit install
pre-commit run --all-files
```

Next let's setup your `test-env.toml`.
Get your api key by logging in on [ikigai](https://app.ikigailabs.io) > Profile > Keys
Fill in your email id and api key into the following command and run it.

```sh
cat > ./test-env.toml <<'/EOF'
[credentials.users.test-user]
user_email="<YOUR-REGISTERED-EMAIL>"
api_key="<YOUR-API-KEY>"
base_url="https://api.ikigailabs.io"
/EOF
```

With that you are set to contribute to this project.
Let try to run the tests and see coverage statistics to validate that setup was a success.

```sh
hatch test --cover
```

It might take some time when you first run this command,
hatch will setup the testing environment and install any required dependencies as specified in the `pyproject.toml` file.

If everything went well, you will see something like:

```txt
======================== test session starts =========================
platform darwin -- Python 3.13.1, pytest-8.3.4, pluggy-1.5.0
rootdir: ./ikigai
configfile: pyproject.toml
collected 9 items

tests/components/test_app.py ...                               [ 33%]
tests/components/test_dataset.py ...                           [ 66%]
tests/test_ikigai.py ...                                       [100%]

========================= 9 passed in 46.26s =========================
Combined data file
Name                                Stmts   Miss Branch BrPart  Cover
---------------------------------------------------------------------
src/ikigai/__init__.py                  2      0      0      0   100%
src/ikigai/client/__init__.py           1      0      0      0   100%
src/ikigai/client/session.py           29      5      6      1    71%
src/ikigai/components/__init__.py       3      0      0      0   100%
src/ikigai/components/app.py           81      3      2      1    95%
src/ikigai/components/dataset.py      142     31     16      5    75%
src/ikigai/ikigai.py                   23      0      0      0   100%
src/ikigai/utils/__init__.py            1      0      0      0   100%
src/ikigai/utils/compatibility.py       6      2      2      1    62%
src/ikigai/utils/named_mapping.py      20      4      4      1    71%
src/ikigai/utils/protocols.py           6      0      0      0   100%
tests/__init__.py                       0      0      0      0   100%
tests/components/__init__.py            0      0      0      0   100%
tests/components/conftest.py           40      0      4      0   100%
tests/components/test_app.py           41      0      0      0   100%
tests/components/test_dataset.py       38      0      0      0   100%
tests/conftest.py                      27      1      2      1    93%
tests/test_ikigai.py                   15      0      0      0   100%
---------------------------------------------------------------------
TOTAL                                 475     46     36     10    87%
```

## Tips and Tricks

### Releasing new version

To release new version first and foremost you need to bump the version. `hatch` makes it quite smooth.

```sh
$ hatch version micro
Old: 0.0.2
New: 0.0.3
```

After this commit any files hatch changed when updating the version. Create a tag to go along with the commit.
For consistency use the following template for commit message and tag:

```txt
$ git commit -m "Bump version to v$(hatch version)"
[main XXXXXXX] Bump version to v0.0.3
 1 file changed, 1 insertions(+), 1 deletions(-)

$ git tag "v$(hatch version)"
```

Push the commit and tag

```sh
git push && git push --tags
```

Then create a new release on
[github-releases](https://github.com/ikigailabs-io/ikigai/releases/new) using the tag you just created.

### Profiling tests

We bundle the command `test-prof` to profile the execution of the tests.
To vizualize the results of profiling we use `graphviz`, install it by
following the official [graphviz page](https://graphviz.org/download/).

Then run:

```sh
hatch test --profile --profile-svg
```

If you don't want to install graphviz then drop the `--profile-svg` flag from the command.
