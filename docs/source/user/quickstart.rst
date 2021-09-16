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

You need your Clarify credentials. Click :ref:`here <getcredentials>` for how to find them.



Create one signal
=================
PyClarify provides a fast and easy way to create signals in Clarify, by using the :py:meth:`~pyclarify.interface.ClarifyInterface` class.

Step 1: Create two string objects with your integration id and your signal name. Then define two lists with the timestamps and the values respectively.

Step 2: Use the  :py:meth:`~pyclarify.interface.ServiceInterface.authenticate` method which takes as an argoument the path of your credentials.

Step 3: Call the :py:meth:`~pyclarify.interface.ClarifyInterface.add_data_single_signal` method and provide the two strings and lists you created in step 1. 

An example
^^^^^^^^^^

.. code-block:: python

    >>> interface = pyclarify.interface.ClarifyInterface()

    >>> integration = "<integration_id>"
    >>> input_id = "<signal_name>"
    >>> times = ["2021-04-11T21:49:06Z", "2021-05-11T21:50:06Z"]
    >>> values = [10, 12]

    >>> interface.authenticate('./clarify-credentials.json')
    >>> interface.add_data_single_signal(integration, input_id, times, values)

Create multiple signals
=========================

<text>


An example
^^^^^^^^^^

.. code-block:: python

    interface = pyclarify.interface.ClarifyInterface()

    integration = "<integration_id>"
    times = [["2021-04-11T21:49:06Z", "2021-04-11T21:50:06Z"], ["2021-04-11T21:49:06Z", "2021-04-11T21:50:06Z"]]
    values = [[1, 2], [3, 4] ]
    input_id = ["<signal_name_1>","<signal_name_2>"]

    interface.authenticate('./clarify-credentials.json')
    interface.add_data_multiple_signals(integration, input_id, times, values)



Add or update metadata 
==========================

To add or update the signal's metadata, use the :py:meth:`~pyclarify.models.data.Signal` module. For more details about the parameters
click `here <https://docs.clarify.us/reference#signal>`__.

An example
^^^^^^^^^^

.. code-block:: python

    from pyclarify.models.data import Signal

    interface = pyclarify.interface.ClarifyInterface()

    integration = "<integration_id>"
    signal_metadata_list = Signal(
        name="<signal_name>",
        description="Some description",
        labels={
            "location": ["one", "two"],
            "flavours": ["sweet"],
        },
    )

    interface.authenticate("./clarify-credentials.json")
    interface.add_metadata_signals(integration, [signal_metadata_list])