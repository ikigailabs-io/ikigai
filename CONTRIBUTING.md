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
hatch run cov
```

It might take some time when you first run this command,
hatch will setup the testing environment and install any required dependencies as specified in the `pyproject.toml` file.

If everything went well, you will see something like:

```txt
cmd [1] | coverage run -m pytest tests
======================== test session starts =========================
platform linux -- Python 3.12.7, pytest-8.3.3, pluggy-1.5.0
configfile: pyproject.toml
collected 2 items

tests/test_ikigai.py ..                                        [100%]

========================= 2 passed in 2.26s ==========================
cmd [2] | - coverage combine
cmd [3] | coverage report
Name                                Stmts   Miss Branch BrPart  Cover
---------------------------------------------------------------------
src/ikigai/__init__.py                  2      0      0      0   100%
src/ikigai/client/__init__.py           1      0      0      0   100%
src/ikigai/client/session.py           25      6      6      1    65%
src/ikigai/components/__init__.py       2      0      0      0   100%
src/ikigai/components/app.py           19      0      0      0   100%
src/ikigai/ikigai.py                   19      0      0      0   100%
tests/__init__.py                       0      0      0      0   100%
tests/conftest.py                       4      0      0      0   100%
tests/test_ikigai.py                    9      0      0      0   100%
---------------------------------------------------------------------
TOTAL                                  81      6      6      1    87%
```

## Tips and Tricks
