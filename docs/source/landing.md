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
    "times": ["2023-10-27T00:00:00+02:00"],
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

The source code is currently hosted on GitHub at: [https://github.com/clarify/pyclarify](https://github.com/clarify/pyclarify)

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
