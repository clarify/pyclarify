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
import logging
from datetime import timedelta, datetime
from pydantic import validate_arguments
from pydantic.fields import Optional
from typing import Dict, List, Union
import pyclarify
from pyclarify.jsonrpc.client import JSONRPCClient
from pyclarify.views.dataframe import DataFrame
from pyclarify.views.items import Item
from pyclarify.views.signals import Signal
from pyclarify.fields.constraints import InputID, ResourceID, ApiMethod
from pyclarify.views.generics import Request, Response
from pyclarify.query import Filter, DataFilter
from pyclarify.query.query import ResourceQuery, DataQuery


class Client(JSONRPCClient):
    """
    The class containing all rpc methods for talking to Clarify. Uses credential file on initialization. 

    Parameters
    ----------
    clarify_credentials: path to json file
        Path to the Clarify credentials json file from the integrations page in clarify. See user guide for more information.

    Example
    -------
        >>> client = Client("./clarify-credentials.json")
    """

    def __init__(self, clarify_credentials):
        super().__init__(None)
        self.update_headers({"X-API-Version": pyclarify.__API_version__})
        self.update_headers({"User-Agent": f"PyClarify/{pyclarify.__version__}"})
        auth_success = self.authenticate(clarify_credentials)
        if auth_success:
            self.base_url = f"{self.authentication.api_url}rpc"
            logging.debug("Successfully connected to Clarify!")
            logging.debug(f"SDK version: {pyclarify.__version__}")
            logging.debug(f"API version: {pyclarify.__API_version__}")
            

    @validate_arguments
    def insert(self, data: DataFrame) -> Response:
        """
        This call inserts data to one or multiple signals. The signal is given an input id by the user. The signal is uniquely identified by its input ID in combination with
        the integration ID. If no signal with the given combination exists, an empty signal is created. With the creation of the signal, a unique signal id gets assigned to it.
        Mirroring the Clarify API call `integration.insert <https://docs.clarify.io/api/methods/integration/insert>`_ .

        Parameters
        ----------
        data : DataFrame
            Dataframe containing the values of a signal in a key-value pair, and separate time axis. 

        Returns
        -------
        Response
            `Response.result.data` is a dictionary mapping <INPUT_ID> to <SIGNAL_ID>.

        See Also
        --------
        Client.data_frame : Retrieve data from selected items.
        Client.save_signals : Save meta data for signals.
        DataFrame : Model used for transporting data to and from Clarify.

        Example
        -------
            >>> from pyclarify import Client, DataFrame
            >>> client = Client("./clarify-credentials.json")

            Inserting some dummy data.

            >>> data = DataFrame(
            ...     series={"<INPUT_ID_1>": [1, 2], "<INPUT_ID_2>": [3, 4]},
            ...     times=["2021-11-01T21:50:06Z",  "2021-11-02T21:50:06Z"]
            ... )
            >>> client.insert(data)

            Inserting pandas.DataFrame.
            
            >>> import pandas as pd
            >>> df = pd.DataFrame(data={"<INPUT_ID_1>": [1, 2], "<INPUT_ID_2>": [3, 4]})
            >>> df.index = ["2021-11-01T21:50:06Z",  "2021-11-02T21:50:06Z"]
            >>> client.insert(DataFrame.from_pandas(df))


        Response
            In case of a valid return value, returns a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                ... id = '1'
                ... signalsByInput = {
                ...     '<INPUT_ID_1>': CreateSummary(id = '<SIGNAL_ID_1>', created = True),
                ...     '<INPUT_ID_2>': CreateSummary(id = '<SIGNAL_ID_2>', created = True)
                ... }
                ... error = None

            Where:

            - InsertResponse is a a pydantic model with field signalsByInput.
            - signalsByInput is a Dict[InputID, CreateSummary].
            - CreateSummary is a a pydantic model with field id: str and created: bool (True if a new instance was created, False is the instance already existed).

            In case of the error (for example not equal length) the method return a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                ... id = '1'
                ... result = None
                ... error = Error(
                ...         code = '-32602',
                ...         message = 'Invalid params',
                ...         data = ErrorData(
                ...                     trace = <trace_id>,
                ...                     params = {'data.series.id': ['not same length as times']}
                ...         )
                ... )

        """
        request_data = Request(
            method=ApiMethod.insert,
            params={"integration": self.authentication.integration_id, "data": data},
        )

        self.update_headers(
            {"Authorization": f"Bearer {self.authentication.get_token()}"}
        )

        return self.make_requests(request_data.json())

    @validate_arguments
    def select_items(
        self,
        filter: Optional[Filter] = None,
        include: Optional[List] = [],
        skip: int = 0,
        limit: int = 10,
        sort: List[str] = [],
        total: Optional[bool] = False,
    ) -> Response:
        """
        Return item metadata from selected items.
        For more information click `here <https://docs.clarify.io/api/1.1beta2/methods/clarify/select-items>`_ .

        Parameters
        ----------
        filter: Filter, optional
            A Filter Model that describes a mongodb filter to be applied.

        include: List of strings, optional
            A list of strings specifying which relationships to be included in the response.

        skip: int, default 0
            Integer describing how many of the first N items to exclude from response.

        limit: int, default 10
            Number of items to include in the match.

        sort: list of strings
            List of strings describing the order in which to sort the items in the response.
        
        total: bool, default False
            When true, force the inclusion of a total count in the response. A total count is the total number of resources that matches filter.



        Returns
        -------
        Response
            ``Response.result.data`` is an array of ItemSelectView            


        Example
        -------
            >>> client = Client("./clarify-credentials.json")

            Querying items based on a filter.

            >>> client.select_items(
            ...     filter = Filter(fields={"name": filter.NotEqual(value="Air Temperature")}),
            ... )

            Getting 1000 items. 

            >>> client.select_items(
            ...     limit = 1000,
            ... )

            Getting 100 items and sorting by name.

            >>> client.select_signals(
            ...     limit = 100,
            ...     sort = ["name"],
            ... )

            Getting total number of signals (as meta data).
            
            >>> client.select_signals(
            ...     total= True,
            ... )

            Using multiple query parameters.

            >>> client.select_items(
            ...     filter = query.Filter(fields={"name": query.NotEqual(value="Air Temperature")}),
            ...     skip = 3,
            ...     limit = 10,
            ...     sort = ["-id", "name"],
            ...     total=True,
            ... )
        
        Response
            In case of a valid return value, returns a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                ... id = '1'
                ... result = Selection(
                ...     meta={
                ...         'total': -1,
                ...         'groupIncludedByType': True
                ...     },
                ...     data=[
                ...         ItemSelectView(
                ...             id='c5i41fjsbu8cohpkcpvg', 
                ...             type='items', 
                ...             meta=ResourceMetadata(
                ...                 annotations={
                ...                     "docs-clarify-io/example/environment": "office"
                ...                  }, 
                ...                 attributesHash='7602afa2fe611e0c8eff17f7936e108ee29e6817', 
                ...                 relationshipsHash='5f36b2220a14b54ee5ea290645ee34d943ea5be5', 
                ...                 updatedAt=datetime.datetime(2022, 3, 25, 9, 58, 20, 264000, tzinfo=datetime.timezone.utc), 
                ...                 createdAt=datetime.datetime(2021, 10, 11, 13, 48, 46, 958000, tzinfo=datetime.timezone.utc)
                ...             ), 
                ...             attributes=Item(
                ...                 name='Dunder ReBond Inventory Level', 
                ...                 valueType=<TypeSignal.numeric: 'numeric'>, 
                ...                 description='How many reams of the Dunder ReBond we have in the warehouse.', 
                ...                 labels={
                ...                     'type': ['Recycled', 'Bond'], 
                ...                     'location': ['Scranton'],
                ...                     'threat-level': ['Midnight'] 
                ...                 }, 
                ...                 engUnit='', 
                ...                 enumValues={}, 
                ...                 sourceType=<SourceTypeSignal.measurement: 'measurement'>, 
                ...                 sampleInterval=None, 
                ...                 gapDetection=datetime.timedelta(seconds=7200), 
                ...                 visible=True
                ...             ),
                ...             relationships={}
                ...         ),
                ...         ItemSelectView(...),
                ...         ...
                ...     ]
                ... ),
                ... error=None


            In case of the error the method return a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                ... id = '1'
                ... result = None
                ... error = Error(
                ...         code = '-32602',
                ...         message = 'Invalid params',
                ...         data = ErrorData(trace = <trace_id>, params = {})
                ... )

        """
        query = ResourceQuery(
            filter=filter.to_query() if isinstance(filter, Filter) else {},
            sort=sort,
            limit=limit,
            skip=skip,
            total=total,
        )
        params = {"query": query, "include": include}

        request_data = Request(
            id=self.current_id, method=ApiMethod.select_items, params=params
        )
        self.update_headers(
            {"Authorization": f"Bearer {self.authentication.get_token()}"}
        )
        return self.make_requests(request_data.json())

    @validate_arguments
    def save_signals(
        self,
        input_ids: List[InputID] = [],
        signals: List[Signal] = [],
        signals_by_input: Dict[InputID, Signal] = {},
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
            Click `here <https://docs.clarify.io/api/1.1beta2/types/fields#input-key>`_ for more information.

        signals: List[Signal]
            List of Signal object that contains metadata for a signal.
            Click `here <https://docs.clarify.io/api/1.1beta2/types/views#signal-save-integration-namespace>`_ for more information.

        create_only: bool, default False
            If set to true, skip update of information for existing signals. That is, all Input_ID's
            that map to existing signals are silently ignored.

        integration: str, default None
            Integration ID in string format. None means using the integration in credential file.




        Returns
        -------
        Response
            `Response.result.data` is a dictionary mapping <INPUT_ID> to <SIGNAL_ID>.

        Example
        -------
            >>> client = Client("./clarify-credentials.json")

            Saving by using a dictionary.

            >>> from pyclarify import Signal
            >>> signal = Signal(
            ...     name = "Home temperature",
            ...     description = "Temperature in the bedroom",
            ...     labels = {
            ...         "data-source": ["Raspberry Pi"],
            ...         "location": ["Home"]
            ...     }
            ... )
            >>> input_dict = {
            ...     "<INPUT_ID>" : signal
            ... }
            >>> response = client.save_signals(
            ...     signals_by_input=input_dict
            ... )

            Saving using arrays.


            >>> from pyclarify import Signal
            >>> signal = Signal(
            ...    name = "Home temperature",
            ...    description = "Temperature in the bedroom",
            ...    labels = {"data-source": ["Raspberry Pi"], "location": ["Home"]}
            ... )
            >>> client.save_signals(input_ids=['<INPUT_ID>'], signals=[signal], create_only=False)

        Response
            In case of a valid return value, returns a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                ... id = '1'
                ... result = SaveSignalsResponse(
                ...             signalsByInput={
                ...                 '<INPUT_ID>': SaveSummary(id='<SIGNAL_ID>', created=True, updated=False)
                ...              }
                ...          )
                ... error = None

            In case of the error the method return a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                ... id = '1'
                ... result = None
                ... error = Error(
                ...         code = '-32602',
                ...         message = 'Invalid params',
                ...         data = ErrorData(trace = <trace_id>, params = {})
                ... )

        """

        # create params dict
        params = {"inputs": signals_by_input, "createOnly": create_only, "integration": integration}

        # assert integration parameter
        if not params["integration"]:
            params["integration"] = self.authentication.integration_id

        if input_ids != [] and signals != []:
            # populate inputs
            for input_id, signal in zip(input_ids, signals):
                params["inputs"][input_id] = signal

        request_data = Request(method=ApiMethod.save_signals, params=params)

        self.update_headers(
            {"Authorization": f"Bearer {self.authentication.get_token()}"}
        )
        return self.make_requests(request_data.json())

    @validate_arguments
    def publish_signals(
        self,
        signal_ids: List[ResourceID] = [],
        items: List[Item] = [],
        items_by_signal: Dict[ResourceID, Item] = {},
        create_only: bool = False,
        integration: str = None,
    ) -> Response:
        """
        Publishes one or multiple signals to create one or multiple items, and creates or updates a set of signals with the provided metadata.
        Each signal is uniquely identified by its signal ID in combination with the integration ID.
        Mirroring the Clarify API call `admin.publishSignals <https://docs.clarify.io/api/next/methods/admin/publish-signals>`_ .

        Parameters
        ----------
        signal_ids: List['<SIGNAL_ID>']
            List of strings to be the signal ID of the signal.

        items: List[ Item ]
            List of Item object that contains metadata for a Item.
            Click `here <https://docs.clarify.io/api/next/datatypes/item>`_ for more information.

        items_by_signal: Dict[ResourceID, Item]
            Dictionary with IDs of signals mapped to Item metadata.

        create_only: bool, default False
            If set to True, skip update of information for existing Items. That is, all signal_ids
            that map to existing items are silently ignored.

        integration: str Default None
          Integration ID in string format. None means using the integration in credential file.

        Returns
        -------
        Response
            `Response.result.data` is a dictionary mapping <SIGNAL_ID> to <ITEM_ID>.

    
        Example
        -------
            >>> client = Client("./clarify-credentials.json")

            Publishing by using a dictionary.

            >>> from pyclarify import Item
            >>> item = Item(
            ...     name = "Home temperature",
            ...     description = "Temperature in the bedroom",
            ...     labels = {
            ...         "data-source": ["Raspberry Pi"],
            ...         "location": ["Home"]
            ...     },
            ...     visible=True
            ... )
            >>> items_dict = {
            ...     "<SIGNAL_ID>": item
            ... }
            >>> response = client.publish_signals(
            ...     items_by_signal=item_dict
            ... )

            Publishing using arrays.

            >>> from pyclarify import Item
            >>> item = Item(
            ...     name = "Home temperature",
            ...     description = "Temperature in the bedroom",
            ...     labels = {
            ...         "data-source": ["Raspberry Pi"], 
            ...         "location": ["Home"]},
            ...     visible=True
            ... )
            >>> client.publish_signals(signal_ids=['<SIGNAL_ID>'], items=[item], create_only=False)
            

        Response
            In case of a valid return value, returns a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                ... id = '1'
                ... result = PublishSignalsResponse(
                ...                    itemsBySignal = {'<SIGNAL_ID>': SaveSummary(
                ...                           id='<ITEM_ID>',
                ...                           created=True,
                ...                           updated=False )})
                ... error = None

            In case of the error the method return a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                ... id = '1'
                ... result = None
                ... error = Error(
                ...         code = '-32602',
                ...         message = 'Invalid params',
                ...         data = ErrorData(trace = <trace_id>, params = {})
                ... )

        """

        params = {
            "itemsBySignal": items_by_signal,
            "createOnly": create_only,
            "integration": integration,
        }

        if not params["integration"]:
            params["integration"] = self.authentication.integration_id

        if signal_ids != [] and items != []:
            for signal_id, item in zip(signal_ids, items):
                params["itemsBySignal"][signal_id] = item

        request_data = Request(method=ApiMethod.publish_signals, params=params)

        self.update_headers(
            {"Authorization": f"Bearer {self.authentication.get_token()}"}
        )
        return self.make_requests(request_data.json())

    @validate_arguments
    def select_signals(
        self,
        filter: Optional[Filter] = None,
        skip: int = 0,
        limit: int = 20,
        sort: List[str] = [],
        total: Optional[bool] = False,
        include: Optional[List] = [],
        integration: str = None,
    ) -> Response:
        """
        Return signal metadata from selected signals and/or item.

        Parameters
        ----------
        filter: Filter, optional
            A Filter Model that describes a mongodb filter to be applied.

        skip: int, default 0
            Integer describing how many of the first N items to exclude from response.

        limit: int, default 10
            Number of items to include in the match.

        sort: list of strings
            List of strings describing the order in which to sort the items in the response.
        
        total: bool, default False
            When true, force the inclusion of a total count in the response. A total count is the total number of resources that matches filter.
        
        include: List of strings, optional
            A list of strings specifying which relationships to be included in the response.

        integration: str Default None
            Integration ID in string format. None means using the integration in credential file.

        Returns
        -------
        Response
            ``Response.result.data`` is an array of SignalSelectView
                    
        Example
        -------
            >>> client = Client("./clarify-credentials.json")

            Querying signals based on a filter.

            >>> client.select_signals(
            ...     filter = Filter(fields={"name": filter.NotEqual(value="Air Temperature")}),
            ... )

            Getting 1000 signals. 

            >>> client.select_signals(
            ...     limit = 1000,
            ... )

            Getting 100 signals and sorting by name.

            >>> client.select_signals(
            ...     limit = 100,
            ...     sort = ["name"],
            ... )

            Getting total number of signals (as meta data) and including the exposed items.

            >>> client.select_signals(
            ...     total= True,
            ...     include = ["item"]
            ... )


        Response
            In case of a valid return value, returns a pydantic model with the following format:

                >>> jsonrpc='2.0' 
                ... id='1' 
                ... result=Selection(
                ...     meta=SelectionMeta(
                ...     total=725, 
                ...     groupIncludedByType=True
                ...     ), 
                ...     data=[
                ...         SignalSelectView(
                ...             id='c5fg083sab1b6pm3u290', 
                ...             type='signals', 
                ...             meta=ResourceMetadata(
                ...                 annotations={
                ...                     "docs-clarify-io/example/environment": "office"
                ...                 }, 
                ...                 attributesHash='9ae4eb17c8b3b9f24cea06f09a1a4cab34569077', 
                ...                 relationshipsHash='02852897e7fe1e7896360b3c3914c5207d2af6fa', 
                ...                 updatedAt=datetime.datetime(2022, 3, 17, 12, 17, 10, 199000, tzinfo=datetime.timezone.utc), 
                ...                 createdAt=datetime.datetime(2021, 10, 7, 14, 11, 44, 897000, tzinfo=datetime.timezone.utc)
                ...             ), 
                ...             attributes=SavedSignal(
                ...                 name='Total reams of paper', 
                ...                 description='Total count of reams of paper in inventory', 
                ...                 labels={
                ...                     'type': ['Recycled', 'Bond'], 
                ...                     'location': ['Scranton']
                ...                 }, 
                ...                 sourceType=<SourceTypeSignal.measurement: 'measurement'>, 
                ...                 valueType=<TypeSignal.numeric: 'numeric'>, 
                ...                 engUnit='', 
                ...                 enumValues={}, 
                ...                 sampleInterval=None, 
                ...                 gapDetection=None, 
                ...                 input='inventory_recycled_bond', 
                ...                 integration=None, 
                ...                 item=None
                ...             ), 
                ...             relationships=RelationshipsDict(
                ...                 integration=RelationshipData(
                ...                     data=RelationshipMetadata(
                ...                         type='integrations', 
                ...                         id='c5e3u8coh8drsbpi4cvg'
                ...                     )
                ...                 ), 
                ...                 item=RelationshipData(data=None)
                ...             )
                ...         ), 
                ...         ...
                ...     ], 
                ...     included=IncludedField(
                ...         integration=None, 
                ...         items=[
                ...             ItemSelectView(
                ...                 id='c5i41fjsbu8cohpkcpvg', 
                ...                 type='items', 
                ...                 meta=ResourceMetadata(
                ...                     annotations={
                ...                         "docs-clarify-io/example/environment": "office"
                ...                     }, 
                ...                     attributesHash='7602afa2fe611e0c8eff17f7936e108ee29e6817', 
                ...                     relationshipsHash='5f36b2220a14b54ee5ea290645ee34d943ea5be5', 
                ...                     updatedAt=datetime.datetime(2022, 3, 25, 9, 58, 20, 264000, tzinfo=datetime.timezone.utc), 
                ...                     createdAt=datetime.datetime(2021, 10, 11, 13, 48, 46, 958000, tzinfo=datetime.timezone.utc)
                ...                 ), 
                ...                 attributes=Item(
                ...                     name='Dunder ReBond Inventory Level', 
                ...                     valueType=<TypeSignal.numeric: 'numeric'>, 
                ...                     description='How many reams of the Dunder ReBond we have in the warehouse.', 
                ...                     labels={
                ...                         'type': ['Recycled', 'Bond'], 
                ...                         'location': ['Scranton'],
                ...                         'threat-level': ['Midnight'] 
                ...                     }, 
                ...                     engUnit='', 
                ...                     enumValues={}, 
                ...                     sourceType=<SourceTypeSignal.measurement: 'measurement'>, 
                ...                     sampleInterval=None, 
                ...                     gapDetection=datetime.timedelta(seconds=7200), 
                ...                     visible=True
                ...                 )
                ...             )
                ...             ...
                ...         ]
                ...     )
                ... ) 
                ... error=None

            In case of the error the method return a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                ... id = '1'
                ... result = None
                ... error = Error(
                ...         code = '-32602',
                ...         message = 'Invalid params',
                ...         data = ErrorData(trace = <trace_id>, params = {})
                ... )

        """
        query = ResourceQuery(
            filter=filter.to_query() if isinstance(filter, Filter) else {},
            sort=sort,
            limit=limit,
            skip=skip,
            total=total,
        )
        params = {"integration": integration, "query": query, "include": include}

        # assert integration parameter
        if not params["integration"]:
            params["integration"] = self.authentication.integration_id

        request_data = Request(method=ApiMethod.select_signals, params=params)

        self.update_headers(
            {"Authorization": f"Bearer {self.authentication.get_token()}"}
        )
        return self.make_requests(request_data.json())

    @validate_arguments
    def data_frame(
        self,
        filter: Optional[Filter] = None,
        sort: List[str] = [],
        limit: int = 20,
        skip: int = 0,
        total: bool = False,
        gte: Union[datetime, str] = None,
        lt: Union[datetime, str] = None,
        last: int = -1,
        rollup: Union[str, timedelta] = None,
        include: List[str] = [],
        window_size: Union[str, timedelta] = None
    ) -> Response:
        """
        Retrieve DataFrame for items stored in Clarify.


        Parameters
        ----------
        filter: Filter, optional
            A Filter Model that describes a mongodb filter to be applied.

        sort: list of strings
            List of strings describing the order in which to sort the items in the response.

        limit: int, default 20
            The maximum number of resources to select. Negative numbers means no limit, which may or may not be allowed.

        skip: int default: 0
            Skip the first N matches. A negative skip is treated as 0.

        total: bool default: False
            When true, force the inclusion of a total count in the response. A total count is the total number of resources that matches filter.

        gte: string(RFC 3339 timestamp) or python datetime, optional, default <now - 7 days>
            An RFC3339 time describing the inclusive start of the window.

        lt: string(RFC 3339 timestamp) or python datetime, optional, default <now + 7 days>
            An RFC3339 time describing the exclusive end of the window.

        last: int, default -1
            If above 0, select last N timestamps per series. The selection happens after the rollup aggregation.

        rollup: timedelta or string(RFC 3339 duration) or "window", default None
            If RFC 3339 duration is specified, roll-up the values into either the full time window
            (`gte` -> `lt`) or evenly sized buckets.

        include: List of strings, optional
            A list of strings specifying which relationships to be included in the response.

        window_size: RFC 3339 duration, default None
            If RFC 3339 duration is specified, the iterator will use the specified window as a paging size instead of default API limits. This is commonly used when resolution of data is too high to be packaged with default
            values.
        
        Returns
        -------
        Response
            ``Response.result.data`` is a DataFrame

        See Also
        --------
        Client.select_items : Retrieve item metadata from selected items.

        Notes
        -----
        Time selection:

        - Maximum window size is 40 days (40 * 24 hours) when rollup is null or less than PT1M (1 minute).
        - Maximum window size is 400 days (400 * 24 hours) when rollup is greater than or equal to PT1M (1 minute).
        - No maximum window size if rollup is window.

        The limits are used internally by the Clarify API. Should you have very high resolution data (>=1hz), you can use ``time_window`` argument to **reduce** the window, resulting in more requests.


        Example
        -------
            >>> client = Client("./clarify-credentials.json")

            Getting data frame with a filter.

            >>> client.data_frame(
            ...     filter = query.Filter(fields={"name": query.NotEqual(value="Air Temperature")}),
            ... )

            Getting data with a time range.

            >>> client.data_frame(
            ...     gte="2022-01-01T01:01:01Z",
            ...     lt="2022-01-09T01:01:01Z",
            ... )

            Skipping first 3 items and only retrieving 5 items, sorted with descending id.

            >>> client.data_frame(
            ...     sort = ["-id"],
            ...     limit = 5,
            ...     skip = 3,
            ... )

            Setting a lower window size due to json decoding errors.

            >>> client.data_frame(
            ...     window_size = "P20DT,
            ...     limit = 5,
            ...     skip = 3,
            ... )

            .. warning::
                We recommend using ``rollup`` instead of ``window_size`` due to execution time being much faster.

            Using rollup to get sampled data.

            >>> client.data_frame(
            ...     rollup = "PT5M,
            ...     limit = 5,
            ...     skip = 3,
            ... )


        Response
            In case of a valid return value, returns a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                ... id = '1'
                ... result = Selection(
                ...     meta={
                ...         'total': -1,
                ...         'groupIncludedByType': True
                ...     },
                ...     data=DataFrame(
                ...         times=[
                ...             datetime.datetime(2022, 1, 1, 12, 0, tzinfo=datetime.timezone.utc),
                ...             datetime.datetime(2022, 1, 1, 13, 0, tzinfo=datetime.timezone.utc),
                ...             ...],
                ...         series={
                ...             'c5i41fjsbu8cohpkcpvg': [0.18616, 0.18574000000000002, ...],
                ...             'c5i41fjsbu8cohfdepvg': [450.876543125, 450.176543554, ...],
                ...             ...
                ...         }
                ...     )
                ...     
                ... error = None

            In case of the error the method return a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                ... id = '1'
                ... result = None
                ... error = Error(
                ...         code = '-32602',
                ...         message = 'Invalid params',
                ...         data = ErrorData(trace = <trace_id>, params = {})
                ... )

        Tip
        ----
        You can change the `type` of DataFrame from pyclarify to pandas using the `to_pandas()` method.

            >>> r = client.data_frame()
            >>> c_df = r.result.data
            >>> p_df = c_df.to_pandas()
            >>> p_df.head()
            ...                                   cbpmaq6rpn52969vfl00  cbpmaq6rpn52969vfl0g  ...  cbpmaq6rpn52969vfl90  cbpmaq6rpn52969vfl9g
            ... 2022-09-05 11:30:11.432725+00:00                   2.0                   8.0  ...                   0.0                   4.0
            ... 2022-09-05 11:31:11.432723+00:00                   9.0                   2.0  ...                   8.0                   8.0
            ... 2022-09-05 11:32:11.432722+00:00                   6.0                   4.0  ...                   8.0                   9.0
            ... 2022-09-05 11:33:11.432720+00:00                   0.0                   7.0  ...                   9.0                   4.0
            ... 2022-09-05 11:34:11.432719+00:00                   8.0                   6.0  ...                   8.0                   5.0

        """

        query = ResourceQuery(
            filter=filter.to_query() if isinstance(filter, Filter) else {},
            sort=sort,
            limit=limit,
            skip=skip,
            total=total,
        )
        data_filter = DataFilter(gte=gte, lt=lt)
        data_query = DataQuery(filter=data_filter.to_query(), last=last, rollup=rollup, window_size=window_size)
        params = {"query": query, "data": data_query, "include": include}

        request_data = Request(method=ApiMethod.data_frame, params=params)

        self.update_headers(
            {"Authorization": f"Bearer {self.authentication.get_token()}"}
        )
        return self.make_requests(request_data.json())
