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

PyClarify provides a fast and easy way to interact with Clarify.
The `ClarifyClient` class takes as an argument the path of your credentials in string format, which should always be the first step when starting to interact with PyClarify.

For information about the Clarify Developer documentation
click [here](https://docs.clarify.io/developers/welcome).

## **Using Python with Clarify**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/clarify/data-science-tutorials/blob/main/tutorials/Introduction.ipynb)

Use colab to learn fast end easy how to interact with Clarify using Python. In this introduction tutorial you will learn all the basics to get you started.

## Quickstart

### Access you data with the _ClarifyClient_

```python
from pyclarify import ClarifyClient

client = ClarifyClient("clarify-credentials.json")
```

### Create new Signals with meta data

```python
from pyclarify import Signal

signal = Signal(
    name = "Home temperature",
    description = "Temperature in the bedroom",
    labels = {"data-source": ["Raspberry Pi"], "location": ["Home"]}
)

response = client.save_signals(
    input_ids=["<INPUT_ID>"],
    signals=[signal],
    create_only=False
)
```

### Populate your signals with data

```python
from pyclarify import DataFrame

data = DataFrame(
    series={"<INPUT_ID_1>": [1, None], "<INPUT_ID_2>": [None, 5]},
    times = ["2021-11-01T21:50:06Z",  "2021-11-02T21:50:06Z"],
)

response = client.insert(data)
```

### Query your stored signals

```python
response = client.select_signals(
    skip=10,
    limit=50,
    sort=["-id"]
)
```

### Publish them as items

```python
from pyclarify import Item

client = ClarifyClient("./clarify-credentials.json")

item = Item(
    name = "Home temperature",
    description = "Temperature in the bedroom",
    labels = {"data-source": ["Raspberry Pi"], "location": ["Home"]},
    visible=True
)
response = client.publish_signals(
    signal_ids=['<SIGNAL_ID>'],
    items=[item],
    create_only=False
)
```

### Use filters to get a specific selection

```python
from pyclarify.query import Filter, Regex

only_raspberries = Filter(
    fields={
        "labels.unit-type": Regex(value="Raspberry")
    }
)

response = client.select_items(
    filter=only_raspberries
)
```

### Include relationships on queries

```python

response = client.dataframe(
    filter=only_raspberries,
    include=["item"]
)

```

# Changelog

Wondering about upcoming or previous changes to the SDK? Take a look at the [CHANGELOG](https://github.com/clarify/pyclarify/blob/main/CHANGELOG.md).

# Contributing

Want to contribute? Check out [CONTRIBUTING](https://github.com/clarify/pyclarify/blob/main/CONTRIBUTING.md).
