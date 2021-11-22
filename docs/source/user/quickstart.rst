====================
PyClarify quickstart
====================

.. currentmodule:: pyclarify

.. code-block:: python

   >>> import pyclarify

Prerequisites
=============

You'll need to know a bit of Python. For a refresher, see the `Python
tutorial <https://docs.python.org/tutorial/>`__.

You'll need your Clarify credentials. Click :ref:`here <getcredentials>` for how to find them.



Interact with Clarify
=====================
PyClarify provides a fast and easy way to write data into Clarify, create or update the signal metadata and get item data, by using the :py:meth:`~pyclarify.client.APIClient` class. 
This class takes as an argument the path of your credentials in string format, which should always be the first step when starting to interact with PyClarify. 

For information about the Clarify Developer documentation
click `here <https://docs.clarify.io/reference>`__.


Add Signal metadata
===================

To add or update the signal's metadata, use the :py:meth:`~pyclarify.client.APIClient.save_signals` method. 

Step 1 : Create a :py:meth:`~pyclarify.models.data.SignalInfo` model. 

Step 2 : Use the  :py:meth:`~pyclarify.client.APIClient.save_signals` method.


Example: Add Signal metadata 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

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

|

.. image:: metadata.png
    :scale: 50 %

|


Write data into Clarify
=======================

Step 1: Create a :py:meth:`~pyclarify.models.data.DataFrame` model. 

Step 2: Use the  :py:meth:`~pyclarify.client.APIClient.insert` method which takes as an argument the DataFrame model.


Example: Write data into Clarify
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

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


Now, you should be able to see the newly created signal in Clarify.

|

.. image:: signal_data.png
    :scale: 50 %

|


Get Signal meta-data
====================
This call retrieves signal meta-data and/or exposed items.
This call is a recommend step before doing a publishSignals call. For more information click `here <https://docs.clarify.io/v1.1/reference/adminselectsignals>`_ .

Step 1: Create the params dictionary. See :py:meth:`~pyclarify.client.APIClient.select_signals.params` for more information.

Step 2: Call the :py:meth:`~pyclarify.client.APIClient.select_signals` method.

Example: Get Signal meta-data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> from pyclarify import APIClient

    >>> client = APIClient("./clarify-credentials.json")

    >>> response = client.select_signals(
    >>>     params={
    >>>         "signals": {
    >>>             "include": True,
    >>>             "filter": {"id": {"$in": ["<signal_id>"]}},
    >>>     },
    >>>     "items": {
    >>>         "include": True,
    >>>     },
    >>> }
    >>> )
    >>> print(response.json())


Publish signals
===============
Publish one or more Signals by providing the SignalInfo, which will add metadata to your created Item.

Example: Publish signals
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> from pyclarify import APIClient, SignalInfo

    >>> client = APIClient("./clarify-credentials.json")

    >>> response = client.publish_signals(
    >>> params={
    >>>     "itemsBySignal": {"<signal_id>": SignalInfo(name="<item_name>")},
    >>>     "createOnly": False,
    >>>     }
    >>> )
    >>> print(response.json())



Get Item data  
=============

To get the data from an item, you must first have an integration with reading access.
Once reading access is enabled, use the :py:meth:`~pyclarify.client.APIClient.select_items` method.

Step 1: Create the params dictionary. For more information see :py:meth:`~pyclarify.client.APIClient.select_items.params` .

Step 2: Call the :py:meth:`~pyclarify.client.APIClient.select_items` method.


Example: Get Item data  
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    >>> from pyclarify import APIClient

    >>> client = APIClient("./clarify-credentials.json")

    >>> response = client.select_items(
    >>>    params={
    >>>        "items": {"include": True, "filter": {"id": {"$in": ["<item_id>"]}}},
    >>>        "data": {"include": True},
    >>>     }
    >>> )
    >>> print(response.json())
