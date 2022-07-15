"""
Copyright 2022 Searis AS

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Client module is the main module of PyClarify.

The module provides a class for setting up a JSONRPCClient which will communicate with
the Clarify API. Methods for reading and writing to the API is implemented with the
help of jsonrpcclient framework.
"""
import requests
from datetime import timedelta
from pydantic import validate_arguments
from pydantic.fields import Optional
from typing import List, Union
from typing_extensions import Literal

from pyclarify.jsonrpc.client import JSONRPCClient
from pyclarify.fields.dataframe import DataFrame
from pyclarify.views.items import Item
from pyclarify.views.signals import SignalInfo
from pyclarify.fields.constraints import InputID, ResourceID, ApiMethod
from pyclarify.views.generics import Request, Response
from pyclarify.jsonrpc.oauth2 import GetToken
from pyclarify.__utils__.time import compute_iso_timewindow
from pyclarify.query import Filter


class ClarifyClient(JSONRPCClient):
    def __init__(self, clarify_credentials):
        super().__init__(None)
        self.update_headers({"X-API-Version": "1.1beta1"})
        self.authentication = GetToken(clarify_credentials)
        self.base_url = f"{self.authentication.api_url}rpc"


    @validate_arguments
    def insert(self, data: DataFrame) -> Response:
        """
        This call inserts data to one or multiple signals. The signal is given an input id by the user. The signal is uniquely identified by its input ID in combination with
        the integration ID. If no signal with the given combination exists, an empty signal is created. With the creation of the signal, a unique signal id gets assigned to it.
        Mirroring the Clarify API call `integration.insert <https://docs.clarify.io/api/methods/integration/insert>`_ .

        Parameters
        ----------
        data : DataFrame
            Dataframe with the fields:

            - series: Dict[InputID, List[Union[None, float, int]]]
                Map of inputid to Array of data points to insert by Input ID.
                The length of each array must match that of the times array.
                To omit a value for a given timestamp in times, use the value null.

            - times:  List of timestamps
                Either as a python datetime or as
                YYYY-MM-DD[T]HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]]] to insert.

            Example
            -------
                >>> from pyclarify import DataFrame
                >>> date = ["2021-11-01T21:50:06Z",  "2021-11-02T21:50:06Z"]
                >>> data = DataFrame(
                >>>             series={"<INPUT_ID_1>": [1, 2], "<INPUT_ID_2>": [3, 4]},
                >>>             times=date
                >>>          )

        Returns
        -------
        Response
            In case of a valid return value, returns a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                >>> id = '1'
                >>>             signalsByInput = {
                >>>                      '<INPUT_ID_1>': InsertSummary(id = '<SIGNAL_ID_1>', created = True),
                >>>                      '<INPUT_ID_2>': InsertSummary(id = '<SIGNAL_ID_2>', created = True)
                >>>                       }
                >>> error = None

            Where:

            - InsertResponse is a a pydantic model with field signalsByInput.
            - signalsByInput is a Dict[InputID, InsertSummary].
            - InsertSummary is a a pydantic model with field id: str and created: bool (True if a new instance was created, False is the instance already existed).

            In case of the error (for example not equal length) the method return a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                >>> id = '1'
                >>> result = None
                >>> error = Error(
                >>>         code = '-32602',
                >>>         message = 'Invalid params',
                >>>         data = ErrorData(
                >>>                     trace = <trace_id>,
                >>>                     params = {'data.series.id': ['not same length as times']}
                >>>         )
                >>> )

        """
        request_data = Request(
            method=ApiMethod.insert,
            params={"integration": self.authentication.integration_id, "data": data},
        )

        self.update_headers({"Authorization": f"Bearer {self.get_token()}"})

        return self.make_requests(request_data.json())

    @validate_arguments
    def select_items(
        self,
        filter: Optional[Filter] = None,
        include_dataframe: bool = True,
        include_metadata: bool = True,
        not_before=None,
        before=None,
        skip: int = 0,
        limit: int = 10,
        rollup: Union[timedelta, Literal["window"]] = None,
    ) -> Response:
        """
        Return item data from selected items.
        For more information click `here <https://docs.clarify.io/api/next/datatypes/data-query>`_ .

        Parameters
        ----------
        filter: Filter, optional
            A Filter Model that describes a mongodb filter to be applied.

        include_dataframe: bool
            A boolean deciding whether to include dataframe from item or not.

        include_metadata: bool
            A boolean deciding whether to include metadata from item or not.

        not_before: string(RFC 3339 timestamp) or python datetime, optional, default datetime.now() - 40days
            An RFC3339 time describing the inclusive start of the window.

        before: string(RFC 3339 timestamp) or python datetime, optional, default datetime.now()
            An RFC3339 time describing the exclusive end of the window.

        skip: int, default 0
            Integer describing how many of the first N items to exclude from response.

        limit: int, default 10
            Number of items to include in the match.

        rollup: timedelta or string(RFC 3339 duration) or "window", default None
            If RFC 3339 duration is specified, roll-up the values into either the full time window
            (`notBefore` -> `before`) or evenly sized buckets.


        Example
        -------
            >>> client.select_items(
            >>>     filter = query.Filter(fields={"name": query.NotEqual(value="Air Temperature")}),
            >>>     include_metadata = False,
            >>>     not_before = "2021-10-01T12:00:00Z",
            >>>     before = "2021-11-10T12:00:00Z",
            >>>     skip = 0,
            >>>     limit = 10,
            >>>     rollup = "P1DT"
            >>> )


        Returns
        -------
        Response
            In case of a valid return value, returns a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                >>> id = '1'
                >>> result = SelectItemsResponse(
                >>>             items = None,
                >>>             data = DataFrame(
                >>>                 times = [datetime.datetime(2020, 6, 1, 10, 0, tzinfo=datetime.timezone.utc)],
                >>>                 series = {
                >>>                    '<ITEM_ID>_avg': [478.19],
                >>>                    '<ITEM_ID>_count': [1.0],
                >>>                    '<ITEM_ID>_max': [478.19],
                >>>                    '<ITEM_ID>_min': [478.19],
                >>>                    '<ITEM_ID>_sum': [478.19]
                >>>                 }))
                >>> error = None

            In case where `rollup = None`, the response in the DataFrame has the following (example) format:

                >>>  data = DataFrame(
                >>>                    times = [ datetime.datetime(2020, 6, 1, 10, 0, tzinfo=datetime.timezone.utc) ],
                >>>                    series = {'<ITEM_ID>': [478.19]}
                >>>         )

            In case of the error the method return a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                >>> id = '1'
                >>> result = None
                >>> error = Error(
                >>>         code = '-32602',
                >>>         message = 'Invalid params',
                >>>         data = ErrorData(trace = <trace_id>, params = {})
                >>> )

        """
        not_before, before = compute_iso_timewindow(not_before, before)
        params = {
            "items": {
                "include": include_metadata,
                "limit": limit,
                "skip": skip,
                "filter": filter.to_query() if isinstance(filter, Filter) else {},
            },
            "data": {
                "include": include_dataframe,
                "notBefore": not_before,
                "before": before,
                "rollup": rollup,
            },
        }

        request_data = Request(
            id=self.current_id, method=ApiMethod.select_items, params=params
        )
        self.update_headers({"Authorization": f"Bearer {self.get_token()}"})
        return self.make_requests(request_data.json())

    @validate_arguments
    def save_signals(
        self,
        input_ids: List[InputID],
        signals: List[SignalInfo],
        create_only: bool = False,
        integration: str = None,
    ) -> Response:
        """
        This call inserts metadata to one or multiple signals. The signals are uniquely identified by its <INPUT_ID>.
        Mirroring the Clarify API call `integration.saveSignals <https://docs.clarify.io/api/next/methods/integration/save-signals>`_ .

        Parameters
        ----------
        input_ids: List['<INPUT_ID>']
            List of strings to be the input ID of the signal.
            Click `here <https://docs.clarify.io/api/next/datatypes/input-id>`_ for more information.

        signals: List[SignalInfo]
            List of SignalInfo object that contains metadata for a signal.
            Click `here <https://docs.clarify.io/api/next/datatypes/signal-info>`_ for more information.

        create_only: bool, default False
            If set to true, skip update of information for existing signals. That is, all Input_ID's
            that map to existing signals are silently ignored.

        integration: str, default None
            Integration ID in string format. None means using the integration in credential file.


        Example
        -------

            >>> from pyclarify import SignalInfo
            >>> signal = SignalInfo(
            >>>    name = "Home temperature",
            >>>    description = "Temperature in the bedroom",
            >>>    labels = {"data-source": ["Raspberry Pi"], "location": ["Home"]}
            >>> )
            >>> save_signals(input_ids=['<INPUT_ID>'], signals=[signal], create_only=False)

        Returns
        -------
        Response
            In case of a valid return value, returns a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                >>> id = '1'
                >>> result = SaveSignalsResponse(
                >>>             signalsByInput={
                >>>                 '<INPUT_ID>': SaveSummary(id='<SIGNAL_ID>', created=True, updated=False)
                >>>              }
                >>>          )
                >>> error = None

            In case of the error the method return a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                >>> id = '1'
                >>> result = None
                >>> error = Error(
                >>>         code = '-32602',
                >>>         message = 'Invalid params',
                >>>         data = ErrorData(trace = <trace_id>, params = {})
                >>> )

        """

        # create params dict
        params = {"inputs": {}, "createOnly": create_only, "integration": integration}

        # assert integration parameter
        if not params["integration"]:
            params["integration"] = self.authentication.integration_id

        # populate inputs
        for input_id, signal in zip(input_ids, signals):
            params["inputs"][input_id] = signal

        request_data = Request(method=ApiMethod.save_signals, params=params)

        self.update_headers({"Authorization": f"Bearer {self.get_token()}"})
        return self.make_requests(request_data.json())

    @validate_arguments
    def publish_signals(
        self,
        signal_ids: List[ResourceID],
        items: List[Item],
        create_only: bool = False,
        integration: str = None,
    ) -> Response:
        """
        Publishes one or multiple signals to create one or multiple items, and creates or updates a set of signals with the provided metadata.
        Each signal is uniquely identified by its input ID in combination with the integration ID.
        Mirroring the Clarify API call `admin.publishSignals <https://docs.clarify.io/api/next/methods/admin/publish-signals>`_ .

        Parameters
        ----------
        signal_ids: List['<SIGNAL_ID>']
            List of strings to be the input ID of the signal.

        items: List[ Item ]
            List of Item object that contains metadata for a Item.
            Click `here <https://docs.clarify.io/api/next/datatypes/item>`_ for more information.

        create_only: bool, default False
            If set to True, skip update of information for existing Items. That is, all Input_ID's
            that map to existing items are silently ignored.

        integration: str Default None
          Integration ID in string format. None means using the integration in credential file.


        Example
        -------
            >>> from pyclairfy import Item
            >>>
            >>> item = Item(
            >>>    name = "Home temperature",
            >>>    description = "Temperature in the bedroom",
            >>>    labels = {"data-source": ["Raspberry Pi"], "location": ["Home"]},
            >>>    visible=True
            >>> )
            >>> client.publish_signals(signal_ids=['<SIGNAL_ID>'], items=[item], create_only=False)

        Returns
        -------
        Response
            In case of a valid return value, returns a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                >>> id = '1'
                >>> result = PublishSignalsResponse(
                >>>                    itemsBySignal = {'<SIGNAL_ID>': SaveSummary(
                >>>                           id='<ITEM_ID>',
                >>>                           created=True,
                >>>                           updated=False )})
                >>> error = None

            In case of the error the method return a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                >>> id = '1'
                >>> result = None
                >>> error = Error(
                >>>         code = '-32602',
                >>>         message = 'Invalid params',
                >>>         data = ErrorData(trace = <trace_id>, params = {})
                >>> )

        """

        # create params dict
        params = {
            "itemsBySignal": {},
            "createOnly": create_only,
            "integration": integration,
        }

        # assert integration parameter
        if not params["integration"]:
            params["integration"] = self.authentication.integration_id

        # populate inputs
        for signal_id, item in zip(signal_ids, items):
            params["itemsBySignal"][signal_id] = item

        request_data = Request(method=ApiMethod.publish_signals, params=params)

        self.update_headers({"Authorization": f"Bearer {self.get_token()}"})
        return self.make_requests(request_data.json())


    @validate_arguments
    def select_signals(
        self,
        filter: Optional[Filter] = None,
        include_items: bool = False,
        skip: int = 0,
        limit: int = 10,
        integration: str = None,
    ) -> Response:
        """
        Return signal metadata from selected signals and/or item.

        Parameters
        ----------
        filter: Filter, optional
            A Filter Model that describes a mongodb filter to be applied.

        include_items: bool default: False
            If set to true, include items metadata in the response.

        skip: int default: 0
            Skip first N signals.

        limit: int, default: 10
            Number of signals to include in the match.

        integration: str Default None
            Integration ID in string format. None means using the integration in credential file.

        Example
        -------

            >>> client.select_signals(
            >>>     filter = Filter(fields={"name": filter.NotEqual(value="Air Temperature")}),
            >>>     limit = 10,
            >>>     skip = 0,
            >>>     include_items = False
            >>> )

        Returns
        -------
        Response
            In case of a valid return value, returns a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                >>> id = '1'
                >>> result = SelectSignalsResponse(
                >>>             signals = {'<SIGNAL_ID>': SignalInfo},
                >>>             items = None
                >>>          )
                >>> error = None

            In case of the error the method return a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                >>> id = '1'
                >>> result = None
                >>> error = Error(
                >>>         code = '-32602',
                >>>         message = 'Invalid params',
                >>>         data = ErrorData(trace = <trace_id>, params = {})
                >>> )
        """
        params = {
            "integration": integration,
            "signals": {
                "include": True,
                "filter": filter.to_query() if isinstance(filter, Filter) else {},
                "limit": limit,
                "skip": skip,
            },
            "items": {"include": include_items},
        }

        # assert integration parameter
        if not params["integration"]:
            params["integration"] = self.authentication.integration_id

        request_data = Request(method=ApiMethod.select_signals, params=params)

        self.update_headers({"Authorization": f"Bearer {self.get_token()}"})
        return self.make_requests(request_data.json())
