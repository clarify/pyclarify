<a href="https://www.clarify.io">
    <img src="https://raw.githubusercontent.com/clarify/data-science-tutorials/main/media/logo_dark.png" alt="Clarify logo" title="Clarify" align="right" height="80" />
</a>

# PyClarify

[![PyPI package](https://img.shields.io/badge/pip%20install-pyclarify-brightgreen)](https://pypi.org/project/pyclarify/)
[![version number](https://img.shields.io/pypi/v/pyclarify?color=green&label=version)](https://pypi.org/project/pyclarify/)
[![Actions Status](https://github.com/clarify/pyclarify/workflows/Build%20status/badge.svg)](https://github.com/clarify/pyclarify/actions)
[![License](https://img.shields.io/github/license/clarify/pyclarify)](https://github.com/clarify/pyclarify/blob/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# Useful tutorials and documentation

- [PyClarify SDK](https://pypi.org/project/pyclarify/)
- [PyClarify documentation](https://clarify.github.io/pyclarify/)
- [Clarify Developer documentation](https://docs.clarify.io/developers/welcome)
- [Basic tutorial on using Python with Clarify](https://colab.research.google.com/github/clarify/data-science-tutorials/blob/main/tutorials/Introduction.ipynb)
- [Clarify Forecast tutorial](https://colab.research.google.com/github/clarify/data-science-tutorials/blob/main/tutorials/Forecasting.ipynb)
- [Pattern Recognition tutorial](https://colab.research.google.com/github/clarify/data-science-tutorials/blob/main/tutorials/Pattern%20Recognition.ipynb)
- [Google Cloud Hosting tutorial](https://colab.research.google.com/github/clarify/data-science-tutorials/blob/main/tutorials/Google%20Cloud%20Hosting.ipynb)

# Prerequisites

In order to start using the Python SDK, you need

- To know a bit of Python. For a refresher, see the [Official Python tutorial](https://docs.python.org/tutorial/).
- Python3 (>= 3.7) and pip.
- Credentials from a Clarify integration. See the [introduction notebook](https://colab.research.google.com/github/clarify/data-science-tutorials/blob/main/tutorials/Introduction.ipynb) for a complete introduction.

# Install and import PyClarify

To install this package:

> $ pip install pyclarify
>
> import pyclarify

# Interact with Clarify

PyClarify provides a fast and easy way to interact with Clarify using the `APIClient` and `ClarifyClient` class.
This class takes as an argument the path of your credentials in string format, which should always be the first step when starting to interact with PyClarify.

The `APIClient` and `ClarifyClient` class can do the almost the same operations, but the `ClarifyClient` provides a more pythonic way.

For information about the Clarify Developer documentation
click [here](https://docs.clarify.io/developers/welcome).

## **Using Python with Clarify**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/clarify/data-science-tutorials/blob/main/tutorials/Introduction.ipynb)

Use colab to learn fast end easy how to interact with Clarify using Python. In this introduction tutorial you will learn all the basics to get you started.

## Quickstart

**Save signals**

**Example:**

    from pyclarify import ClarifyClient, SignalInfo

    client = ClarifyClient("./clarify-credentials.json")

    signal = SignalInfo(
       name = "Home temperature",
       description = "Temperature in the bedroom",
       labels = {"data-source": ["Raspberry Pi"], "location": ["Home"]}
    )

    response = client.save_signals(input_ids=["<INPUT_ID>"], signals=[signal], create_only=False)
    print(response.json())

**Insert data into a signal**

**Example:**

    from pyclarify import DataFrame, ClarifyClient

    client = APIClient("./clarify-credentials.json")

    date = ["2021-11-01T21:50:06Z",  "2021-11-02T21:50:06Z"]

    data = DataFrame(
        series={"<INPUT_ID_1>": [1, None], "<INPUT_ID_2>": [None, 5]},
        times = date,
    )

    response = client.insert(data)
    print(response.json())

**Get metadata from signals and/or items**

**Example:**

    from pyclarify import ClarifyClient

    client = ClarifyClient("./clarify-credentials.json")

    response = client.select_signals(
                    ids = ['<SIGNAL_ID>'],
                    name = "Electricity",
                    labels = {"city": "Trondheim"},
                    limit = 10,
                    skip = 0,
                    include_items = False
    )
    print(response.json())

**Publish signals**

**Example:**

    from pyclarify import ClarifyClient, Item

    client = ClarifyClient("./clarify-credentials.json")

    item = Item(
       name = "Home temperature",
       description = "Temperature in the bedroom",
       labels = {"data-source": ["Raspberry Pi"], "location": ["Home"]},
       visible=True
    )
    response = client.publish_signals(signal_ids=['<SIGNAL_ID>'], items=[item], create_only=False)
    print(response.json())

**Get Item data**

**Example:**

    from pyclarify import ClarifyClient

    client = ClarifyClient("./clarify-credentials.json")

    response = client.select_items_data(
        ids = ['<ITEM_ID>'],
        limit = 10,
        skip = 0,
        not_before = "2021-10-01T12:00:00Z",
        before = "2021-11-10T12:00:00Z",
        rollup = "P1DT"
    )
    print(response.json())

**Get Item metadata**

**Example:**

    from pyclarify import ClarifyClient

    client = ClarifyClient("./clarify-credentials.json")

    response = client.select_items_metadata(
        ids = ['<ITEM_ID>'],
        name = "Electricity",
        labels = {"city": "Trondheim"},
        limit = 10,
        skip = 0
    )
    print(response.json())

# Changelog

Wondering about upcoming or previous changes to the SDK? Take a look at the [CHANGELOG](https://github.com/clarify/pyclarify/blob/main/CHANGELOG.md).

# Contributing

Want to contribute? Check out [CONTRIBUTING](https://github.com/clarify/pyclarify/blob/main/CONTRIBUTING.md).
