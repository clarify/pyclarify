<a href="https://www.clarify.io">
    <img src="https://raw.githubusercontent.com/clarify/data-science-tutorials/main/media/logo_dark.png" alt="Clarify logo" title="Clarify" align="right" height="80" />
</a>

# PyClarify

[![PyPI package](https://img.shields.io/badge/pip%20install-pyclarify-brightgreen)](https://pypi.org/project/pyclarify/)
[![Version number](https://img.shields.io/pypi/v/pyclarify?color=green&label=version)](https://pypi.org/project/pyclarify/)
[![Downloads](https://static.pepy.tech/badge/pyclarify)](https://pepy.tech/project/pyclarify)
[![Downloads](https://static.pepy.tech/personalized-badge/pyclarify?period=month&units=none&left_color=grey&right_color=blue&left_text=downloads/month)](https://pepy.tech/project/pyclarify)
[![Actions Status](https://github.com/clarify/pyclarify/workflows/Build%20status/badge.svg)](https://github.com/clarify/pyclarify/actions)
[![License](https://img.shields.io/github/license/clarify/pyclarify)](https://github.com/clarify/pyclarify/blob/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

<hr/>

```python
from pyclarify import Client

data = {
    "times": ["2022-10-10T00:00:00"],
    "series": {
        "temperature": [19],
        "pressure": [1025]
    }
}

client = Client("credentials.json")
client.insert(data)
```

PyClarify helps users of Clarify to easily read, write and manipulate data in Clarify.

- Data scientists can easily filter data, convert it to `pandas` with our built in methods, and write results back.
- System integrators can set up pipelines for automatic streaming of data, and update labels on the fly.

# Useful tutorials and documentation

- [PyClarify SDK](https://pypi.org/project/pyclarify/)
- [PyClarify documentation](https://clarify.github.io/pyclarify/)
- [Clarify Developer documentation](https://docs.clarify.io/developers/welcome)
- [Basic tutorial on using Python with Clarify](https://colab.research.google.com/github/clarify/data-science-tutorials/blob/main/tutorials/Introduction.ipynb)

# Prerequisites

In order to start using the Python SDK, you need

- To know a bit of Python. For a refresher, see the [Official Python tutorial](https://docs.python.org/tutorial/).
- Python3 (>= 3.7) and pip.
- Credentials from a Clarify integration. See the [introduction notebook](https://colab.research.google.com/github/clarify/data-science-tutorials/blob/main/tutorials/Introduction.ipynb) for a complete introduction.

## Where to get it

The source code is currently hosted on GitHub at: https://github.com/clarify/pyclarify

Binary installers for the latest released version are available at the [Python
Package Index (PyPI)](https://pypi.org/project/pyclarify).

```sh
# PyPI install
pip install pyclarify
```

## Dependencies

- [requests](https://requests.readthedocs.io/en/latest/) - The most used (and trusted) HTTP library.
- [Pydantic](https://pydantic-docs.helpmanual.io) - Allowing for strict typing and data validation.
- [Typing Extensions](https://typing.readthedocs.io) - Brings the typing use of new type system features on older Python versions, allowing us to support python 3.7+.

# Interact with Clarify

PyClarify provides a fast and easy way to interact with Clarify.
The `Client` class takes as an argument the path of your credentials in string format, which should always be the first step when starting to interact with PyClarify.

For information about the Clarify Developer documentation
click [here](https://docs.clarify.io/developers/welcome).

## Quickstart

We recommend using Google Colab to quickly learn how to interact with Clarify using Python. We have created an interactive introduction tutorial where you will learn all the basics to get you started.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/clarify/data-science-tutorials/blob/main/tutorials/Introduction.ipynb)

### Access you data with the _ClarifyClient_

```python
from pyclarify import Client

client = Client("clarify-credentials.json")
```

### Create new _Signals_

```python
from pyclarify import Signal

signal = Signal(
    name = "Home temperature",
    description = "Temperature in the bedroom",
    labels = {"data-source": ["Raspberry Pi"], "location": ["Home"]}
)

response = client.save_signals(
    input_ids=["INPUT_ID"],
    signals=[signal],
    create_only=False
)
```

### Populate your signals using _DataFrames_

```python
from pyclarify import DataFrame

data = DataFrame(
    series={"INPUT_ID_1": [1, None], "INPUT_ID_2": [None, 5]},
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

### Publish them as _Items_

```python
from pyclarify import Item

client = Client("./clarify-credentials.json")

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

### Get the data and include relationships

```python
response = client.data_frame(
    filter=only_raspberries,
    include=["item"]
)
```

### Look at our reference!

[<img src="./docs/source/reference.png" width="150" />](https://clarify.github.io/pyclarify/)

# Changelog

Wondering about upcoming or previous changes to the SDK? Take a look at the [CHANGELOG](https://github.com/clarify/pyclarify/blob/main/CHANGELOG.md).

# Contributing

Want to contribute? Check out [CONTRIBUTING](https://github.com/clarify/pyclarify/blob/main/CONTRIBUTING.md).
