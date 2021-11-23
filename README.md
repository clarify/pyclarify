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
- [Clarify Developer documentation](https://docs.clarify.io/reference/http)
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

PyClarify provides a fast and easy way to write data into Clarify, create or update the signal metadata and get item data, by using the `APIClient` class.
This class takes as an argument the path of your credentials in string format, which should always be the first step when starting to interact with PyClarify.

For information about the Clarify Developer documentation
click [her](https://docs.clarify.io/reference).

# Add Signal metadata

To add or update the signal's metadata, use the `save_signals` method.

Step 1 : Create a `SignalInfo` model.

Step 2 : Use the `save_signals` method.

**Example: Add Signal metadata**

    >>> from pyclarify import APIClient, SignalInfo

    >>> client = APIClient("./clarify-credentials.json")

    >>> signal_1 = SignalInfo(
    >>>    name="Home temperature",
    >>>    description="Temperature in the bedroom",
    >>>    labels={"data-source": ["Raspberry Pi"], "location": ["Home"]},
    >>> )

    >>> signal_2 = SignalInfo(
    >>>    name="Home humidity",
    >>>    description="Humidity in the living room",
    >>>    labels={"data-source": ["Raspberry Pi"], "location": ["Home"]},
    >>> )

    >>> response = client.save_signals(
    >>>     params={"inputs": {"id1": signal_1, "id2": signal_2}, "createOnly": False}
    >>> )
    >>> print(response.json())

# Write data into Clarify

Step 1: Create a `DataFrame` model.

Step 2: Use the `insert` method which takes as an argument the DataFrame model.

**Example: Write data into Clarify**

    >>> from pyclarify import DataFrame, APIClient

    >>> client = APIClient("./clarify-credentials.json")
    >>> data = DataFrame(
    >>>     series={"id1": [1, 2, 3, None], "id2": [3, 4, None, 5]},
    >>>     times=[
    >>>         "2021-11-09T21:50:06Z",
    >>>         "2021-11-10T21:50:06Z",
    >>>         "2021-11-12T21:50:06Z",
    >>>         "2021-11-12T21:50:06Z",
    >>>     ],
    >>> )
    >>> response = client.insert(data)
    >>> print(response.json())

# Get Signal meta-data

This call retrieves signal meta-data and/or exposed items.
This call is a recommend step before doing a publishSignals call. For more information click [here](https://docs.clarify.io/v1.1/reference/adminselectsignals).

Step 1: Create the params dictionary.

Step 2: Call the `select_signals` method.

**Example: Get Signal meta-data**

    >>> from pyclarify import APIClient

    >>> client = APIClient("./clarify-credentials.json")

    >>> response = client.select_signals(
    >>>     params={
    >>>         "signals": {
    >>>             "include": True,
    >>>             "filter": {"id": {"$in": ["<signal_id>"]}},
    >>>         },
    >>>         "items": {
    >>>             "include": True,
    >>>         },
    >>>     }
    >>> )
    >>> print(response.json())

# Publish signals

Publish one or more Signals by providing the SignalInfo, which will add metadata to your created Item.

**Example: Publish signals**

    >>> from pyclarify import APIClient, SignalInfo

    >>> client = APIClient("./clarify-credentials.json")

    >>> response = client.publish_signals(
    >>>     params={
    >>>         "itemsBySignal": {"<signal_id>": SignalInfo(name="<item_name>")},
    >>>         "createOnly": False,
    >>>     }
    >>> )
    >>> print(response.json())

# Get Item data

To get the data from an item, you must first have an integration with reading access.
Once reading access is enabled, use the `select_items` method.

Step 1: Create the params dictionary.

Step 2: Call the `select_items` method.

**Example: Get Item data**

    >>> from pyclarify import APIClient

    >>> client = APIClient("./clarify-credentials.json")

    >>> response = client.select_items(
    >>>    params={
    >>>        "items": {"include": True, "filter": {"id": {"$in": ["<item_id>"]}}},
    >>>        "data": {"include": True},
    >>>     }
    >>> )
    >>> print(response.json())

# Changelog

Wondering about upcoming or previous changes to the SDK? Take a look at the [CHANGELOG](https://github.com/clarify/pyclarify/blob/main/CHANGELOG.md).

# Contributing

Want to contribute? Check out [CONTRIBUTING](https://github.com/clarify/pyclarify/blob/main/CONTRIBUTING.md).
