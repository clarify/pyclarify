PyClarify logging
=================

Logging levels can be specified by accessing `pyclarify.client.logging`.

An example
^^^^^^^^^^

.. code-block:: python

    >>> import logging

    >>> logging.basicConfig(filename="client.log", level=logging.INFO,
                            format='%(asctime)s:%(levelname)s%(message)s')

Now when running for example:

.. code-block:: python

    >>> client = APIClient("./clarify-credentials.json")

    >>> data = DataFrame(
    >>>         times=["2021-03-11T21:50:06Z", "2021-04-11T21:50:06Z"],
    >>>         series={"id": [1, 2]})
    >>> client.insert(data=data)

A new file is created called client.log with containing the loggings. 
