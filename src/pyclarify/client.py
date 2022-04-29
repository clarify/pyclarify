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
import json
import logging
import functools

from copy import deepcopy
from datetime import timedelta
from pydantic import validate_arguments
from pydantic.fields import Optional
from typing import List, Union
from typing_extensions import Literal

from pyclarify.models.data import DataFrame, SignalInfo, Item, InputID, ResourceID
from pyclarify.models.requests import Request, ApiMethod
from pyclarify.models.response import Response, Error
from pyclarify.oauth2 import GetToken
from pyclarify.__utils__.pagination import ItemIterator, TimeIterator
from pyclarify.__utils__.time import compute_iso_timewindow
from pyclarify.__utils__ import warnings
from pyclarify.query import Filter


def increment_id(func):
    """
    Decorator which increments the current id variable.

    Parameters
    ----------
    func : function
        Decorator wraps around function using @increment_id.

    Returns
    -------
    func : function
        returns the wrapped function.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args[0].current_id += 1  # args[0] = self
        return func(*args, **kwargs)

    return wrapper


def iterator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        LEGAL_ITERATOR_TYPES = [ApiMethod.select_items]
        payload_list = []
        payload = json.loads(args[1])

        if payload["method"] in LEGAL_ITERATOR_TYPES:
            # Contraints from API (https://docs.clarify.io/api/next/general/limits-and-quotas#rpc-limits)
            if payload["method"] == ApiMethod.select_items:
                API_LIMIT = 50
                selector = "items"
                if not payload["params"]["data"]["include"]:
                    API_LIMIT = 1000

                user_limit = payload["params"][selector]["limit"]
                skip = payload["params"][selector]["skip"]
                notBefore, before = compute_iso_timewindow(
                    start_time=payload["params"]["data"]["notBefore"],
                    end_time=payload["params"]["data"]["before"],
                )
                rollup = payload["params"]["data"]["rollup"]

                for skip, limit in ItemIterator(
                    user_limit=user_limit, limit_per_call=API_LIMIT, skip=skip
                ):
                    current_payload = deepcopy(payload)
                    current_payload["params"][selector]["limit"] = limit
                    current_payload["params"][selector]["skip"] = skip

                    for current_notBefore, current_before in TimeIterator(
                        start_time=notBefore, end_time=before, rollup=rollup
                    ):
                        current_payload = deepcopy(current_payload)
                        current_notBefore, current_before = compute_iso_timewindow(
                            current_notBefore, current_before
                        )
                        current_payload["params"]["data"][
                            "notBefore"
                        ] = current_notBefore
                        current_payload["params"]["data"]["before"] = current_before
                        payload_list += [current_payload]
            else:
                payload_list += [payload]
        else:
            payload_list = [payload]

        args[0].payload_list = payload_list

        return func(*args, **kwargs)

    return wrapper


class RawClient:
    def __init__(
        self, base_url,
    ):
        self.base_url = base_url
        self.headers = {"content-type": "application/json"}
        self.current_id = 0
        self.authentication = None
        self.params_list = []

    def authenticate(self, clarify_credentials):
        """
        Authenticates the client by using the GetToken class (see oauth2.py).

        Parameters
        ----------
        clarify_credentials : str/dict
            The path to the clarify_credentials.json downloaded from the Clarify app,
            or json/dictionary of the content in clarify_credentials.json.

        Returns
        -------
        bool
            True if valid credentials is passed otherwise False.
        """
        try:
            self.authentication = GetToken(clarify_credentials)
            return True
        except:
            return False

    def get_token(self):
        """
        Using the GetToken class (see oauth2.py) to get a new authentication token.

        Returns
        -------
        str
            Access token.
        """
        return self.authentication.get_token()

    @iterator
    def make_requests(self, payload) -> Response:
        """
        Uses post request to send JSON RPC payload.

        Parameters
        ----------
        payload : JSON RPC dictionary
            A dictionary in the form of a JSONRPC request.

        Returns
        -------
        JSON
            JSON dictionary response.

        """
        for payload in self.payload_list:
            logging.debug(f"--> {self.base_url}, req: {payload}")
            res = requests.post(
                self.base_url, data=json.dumps(payload), headers=self.headers
            )
            logging.debug(f"<-- {self.base_url} ({res.status_code})")
            if not res.ok:
                err = {
                    "code": res.status_code,
                    "message": f"HTTP Response Error {res.reason}",
                    "data": res.text,
                }
                res = Response(id=payload["id"], error=Error(**err))

            elif hasattr(res.json(), "error"):
                res = Response(id=payload["id"], error=res.json()["error"])
            else:
                res = Response(**res.json())
            if "responses" not in locals():
                responses = res
            else:
                responses += res
        return responses

    @increment_id
    def create_payload(self, method, params):
        """
        Creates a JSONRPC request payload.
        Parameters
        ----------
        method : str
            The RPC method to call.
        params : dict
            The arguments to the method call.
        Returns
        -------
        str
            Payload string in JSONRPC format.
        """
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self.current_id,
            "params": params,
        }
        return json.dumps(payload)

    def update_headers(self, headers):
        """
        Updates headers of client.

        Parameters
        ----------
        headers : dict
            The headers to be added with key being parameter and value being value.
        """
        for key, value in headers.items():
            self.headers[key] = value

@warnings.deprecated("Use ClarifyClient instead.")
class APIClient(RawClient):
    def __init__(self, clarify_credentials):
        super().__init__(None)
        self.update_headers({"X-API-Version": "1.1beta1"})
        self.authentication = GetToken(clarify_credentials)
        self.base_url = f"{self.authentication.api_url}rpc"

    @increment_id
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

    @increment_id
    @validate_arguments
    def save_signals(self, params: dict) -> Response:
        """
        This call inserts metadata for one or multiple signals. The signals are uniquely identified by its <INPUT_ID>.
        Mirroring the Clarify API call `integration.saveSignals <https://docs.clarify.io/api/methods/integration/save-signals>`_ .

        Parameters
        ----------
        params: dict

            - inputs: Dict[InputID, SignalInfo]
                The SignalInfo object contains metadata for a signal.
                Click `here <https://docs.clarify.io/api/datatypes/signal>`_ for more information.

            - createOnly: bool
                If set to true, skip update of information for existing signals. That is, all input id's
                that map to existing signals are silently ignored.

            Example
            -------

                >>> from pyclarify import SignalInfo
                >>> signal_1 = SignalInfo(
                >>>    name = "Home temperature",
                >>>    description = "Temperature in the bedroom",
                >>>    labels = {"data-source": ["Raspberry Pi"], "location": ["Home"]}
                >>> )
                >>> signal_2 = SignalInfo(name = "Office temperature")
                >>> params = {
                >>>     "inputs": {"<INPUT_ID_1>": signal_1,
                >>>     "<INPUT_ID_2>": signal_2}, 
                >>>     "createOnly": False
                >>>     }

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

            Where:

            - SaveSignalsResponse is a a pydantic model with field signalsByInput.
            - signalsByInput is a Dict[InputID, SaveSummary].
            - SaveSummary is a a pydantic model with field:
                - id: str,
                - created: bool (True if a new instance was created)
                - updated: bool (True if the metadata where updated).

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

        # assert integration parameter
        if not hasattr(params, "integration"):
            params["integration"] = self.authentication.integration_id

        request_data = Request(method=ApiMethod.save_signals, params=params)

        self.update_headers({"Authorization": f"Bearer {self.get_token()}"})
        return self.make_requests(request_data.json())

    @increment_id
    @validate_arguments
    def select_items(self, params: dict) -> Response:
        """
        Get data and metadata for one or multiple items.
        Mirroring the Clarify API call `clarify.selectItems <https://docs.clarify.io/api/next/methods/clarify/select-items>`_ .

        Parameters
        ----------
        params : dict

            - items: dict
                Query which items to select and configure inclusion or exclusion of meta-data in the response.
                By default, no meta-data is included.
                For more information click `here <https://docs.clarify.io/api/next/datatypes/resource-query>`_ .

                - include: bool, default False
                    Set to true to include matched items in the response.

                - filter: dict
                    Filter which items to include.
                    Click `here <https://docs.clarify.io/api/next/general/filtering>`_ for more information.

                - limit: int, default 10
                    Number of items to include in the match.

                - skip: int, default 0
                    Skip the n first items.

            - data: dict
                Configure which data to include in the response.
                For more information click `here <https://docs.clarify.io/api/next/datatypes/data-query>`_ .

                - include: bool, default False
                    Include the timeseries data in the response.

                - notBefore: string(RFC 3339 timestamp) or python datetime, optional
                    Describing the inclusive start of the window.

                - before: string(RFC 3339 timestamp) or python datetime optional
                    Describing the exclusive end of the window.

                - rollup: RFC 3339 duration or "window", default None
                    If RFC 3339 duration is specified, roll-up the values into either the full time window
                    (`notBefore` -> `before`) or evenly sized buckets.

            Example
            -------

                >>> items = {"include": True, "filter": {"id": {"$in": ["<ITEM_ID>"]}},  "limit": 10, "skip": 0}
                >>> data = {
                >>>         "include": True,
                >>>          "notBefore":"2021-11-09T21:50:06Z",
                >>>          "before": "2021-11-10T21:50:06Z",
                >>>          "rollup": "PT1H"
                >>>         }
                >>> 
                >>> params = {"items": items, "data": data}

        Returns
        -------
        Response
            In case of a valid return value, returns a pydantic model with the following (example) format:

                >>> jsonrpc = '2.0'
                >>> id = '1'
                >>> result = SelectItemsResponse(
                >>>             items = {
                >>>                 '<ITEM_ID>' : SignalInfo
                >>>             },
                >>>             data = DataFrame( 
                >>>                 times = [datetime.datetime(2020, 6, 1, 10, 0, tzinfo=datetime.timezone.utc)],
                >>>                 series = {
                >>>                      '<ITEM_ID>_avg': [478.19], 
                >>>                      '<ITEM_ID>_count': [1.0], 
                >>>                      '<ITEM_ID>_max': [478.19], 
                >>>                      '<ITEM_ID>_min': [478.19], 
                >>>                      '<ITEM_ID>_sum': [478.19]
                >>>                      }
                >>>                  )
                >>>
                >>>          )
                >>> error = None

            In case where `rollup = None`, the response in the DataFrame has the following (example) format: 

                >>>  data = DataFrame(
                >>>          times = [datetime.datetime(2020, 6, 1, 10, 0, tzinfo=datetime.timezone.utc)],
                >>>          series = {'<ITEM_ID>': [478.19]}
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

        request_data = Request(method=ApiMethod.select_items, params=params)
        self.update_headers({"Authorization": f"Bearer {self.get_token()}"})
        result = self.make_requests(request_data.json())

        return result

    @increment_id
    @validate_arguments
    def select_signals(self, params: dict) -> Response:
        """
        Get signal metadata and/or exposed items. This call is a recommend step before doing a publish_signals call.
        Mirroring the Clarify API call `admin.selectSignals <https://docs.clarify.io/api/next/methods/admin/select-signals>`_ .

        Parameters
        ----------
        params : dict

            - signals: dict
                    Select signals to include (data for).

                    - include: bool, default False
                        Set to true to include signal metadata in the response.

                    - filter: dict
                        Filter which signals to include.
                        Click `here <https://docs.clarify.io/api/next/general/filtering>`_ for more information.

                    - limit: int, default 50
                        Limit number of signals.

                    - skip: int, default=0
                        Skip first N signals.

            - items: dict
                Configure item inclusion.

                - include: bool, default False
                    Set to true to include items metadata exposed by the selected signals.

            Example
            -------
                >>> signals = {
                >>>             "include": True,
                >>>             "filter": {"id":{"$in": ["<SIGNAL_ID>"]}},
                >>>             "limit": 10, 
                >>>             "skip": 0
                >>>            }
                >>> items = {"include": True}
                >>> 
                >>> params = {"signals": signals, "items": items}

        Returns
        -------
        Response
            In case of a valid return value, returns a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                >>> id = '1'
                >>> result = SelectSignalsResponse(
                >>>             items = {'<ITEM_ID>': SignalInfo},
                >>>             signals= {'<SIGNAL_ID>': Signal}
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

        # assert integration parameter
        if not hasattr(params, "integration"):
            params["integration"] = self.authentication.integration_id

        request_data = Request(method=ApiMethod.select_signals, params=params)
        self.update_headers({"Authorization": f"Bearer {self.get_token()}"})
        return self.make_requests(request_data.json())

    @increment_id
    @validate_arguments
    def publish_signals(self, params: dict) -> Response:
        """
        Publishes one or multiple signals to create one or multiple items.
        Each signal is uniquely identified by its input ID in combination with the integration ID.
        Mirroring the Clarify API call `admin.publishSignals <https://docs.clarify.io/api/next/methods/admin/publish-signals>`_ .

        Parameters
        ----------
        params : dict

            - itemsBySignal: Dict['<SIGNAL_ID>', SignalInfo]
                Select signals to publish.

            - createOnly: bool
                If set to true, skip update of information for existing items.

            Example
            -------

                >>> from pyclarify import SignalInfo
                >>> itemsBySignal = {'<SIGNAL_ID>': SignalInfo(name="<item_name>")}
                >>> createOnly = False
                >>>  
                >>> params = {"itemsBySignal": itemsBySignal, "createOnly": createOnly}   

        Returns
        -------
        Response
            In case of a valid return value, returns a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                >>> id = '1'
                >>> result = PublishSignalsResponse(
                >>>                    itemsBySignal = {
                >>>                            '<SIGNAL_ID>': SaveSummary(
                >>>                                                id='<ITEM_ID>',
                >>>                                                created=True, 
                >>>                                                updated=False )
                >>>                                    }
                >>>                                ) 
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

        # assert integration parameter
        if not hasattr(params, "integration"):
            params["integration"] = self.authentication.integration_id

        request_data = Request(method=ApiMethod.publish_signals, params=params)

        self.update_headers({"Authorization": f"Bearer {self.get_token()}"})
        return self.make_requests(request_data.json())

class ClarifyClient(RawClient):
    def __init__(self, clarify_credentials):
        super().__init__(None)
        self.update_headers({"X-API-Version": "1.1beta1"})
        self.authentication = GetToken(clarify_credentials)
        self.base_url = f"{self.authentication.api_url}rpc"

    @warnings.deprecated("Use select_items() with include_metadata=False instead.")
    @increment_id
    @validate_arguments
    def select_items_data(
        self,
        ids: List = [],
        limit: int = 10,
        skip: int = 0,
        not_before=None,
        before=None,
        rollup: Union[timedelta, Literal["window"]] = None,
    ) -> Response:
        """
        Return item data from selected items.
        For more information click `here <https://docs.clarify.io/api/next/datatypes/data-query>`_ .
        Parameters
        ----------
        ids: list, optional
            List of item ids to retrieve. Empty list means take all.
        limit: int, default 10
            Number of items to include in the match.
        skip: int, default 0
            Skip first N items.
        not_before: string(RFC 3339 timestamp) or python datetime, optional, default datetime.now() - 40days
            An RFC3339 time describing the inclusive start of the window.
        before: string(RFC 3339 timestamp) or python datetime, optional, default datetime.now()
            An RFC3339 time describing the exclusive end of the window.
            
        rollup: RFC 3339 duration or "window", default None
            If RFC 3339 duration is specified, roll-up the values into either the full time window
            (`notBefore` -> `before`) or evenly sized buckets.
        Example
        -------
            >>> client.select_items_data(
            >>>     ids = ['<ITEM_ID>'],
            >>>     limit = 10,
            >>>     skip = 0,
            >>>     not_before = "2021-10-01T12:00:00Z",
            >>>     before = "2021-11-10T12:00:00Z",
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
            "items": {"include": False, "limit": limit, "skip": skip},
            "data": {
                "include": True,
                "notBefore": not_before,
                "before": before,
                "rollup": rollup,
            },
        }
        if isinstance(ids, list):
            if len(ids) > 0:
                params["items"]["filter"] = {"id": {"$in": ids}}

        request_data = Request(
            id=self.current_id, method=ApiMethod.select_items, params=params
        )
        self.update_headers({"Authorization": f"Bearer {self.get_token()}"})
        return self.make_requests(request_data.json())
    
    @warnings.deprecated("Use select_items() with include_dataframe=False instead.")
    @increment_id
    @validate_arguments
    def select_items_metadata(
        self,
        ids: List = [],
        name: str = "",
        labels: dict = {},
        limit: int = 10,
        skip: int = 0,
    ) -> Response:
        """
        Return item metadata from selected items.
        Parameters
        ----------
        ids: list, optional
            List of item ids to retrieve. Empty list means take all.
        name: string, default: ""
            String containing regex of the name of an Item.
        labels: dict default: {}
            Dictionary with labels and keys to be used as a filter
        
        limit: int, default: 10
            Number of items to include in the match.
        
        skip: int default: 0
            Skip first N items.
        Example
        -------
            >>> client.select_items_metadata(
            >>>     ids = ['<ITEM_ID>'],
            >>>     name = "Electricity",
            >>>     labels = {"city": "Trondheim"},
            >>>     limit = 10,
            >>>     skip = 0
            >>> )
        Returns
        -------
        Response
            In case of a valid return value, returns a pydantic model with the following format:
                >>> jsonrpc = '2.0'
                >>> id = '1'
                >>> result = SelectSignalsResponse(
                >>>             items = {'<ITEM_ID>': SignalInfo},
                >>>             signals = None
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
        filters = []
        if isinstance(ids, list):
            if len(ids) > 0:
                filters += [{"id": {"$in": ids}}]

        if name != "":
            filters += [{"name": {"$regex": name}}]

        params = {
            "items": {"include": True, "filter": {}, "limit": limit, "skip": skip},
            "data": {"include": False}
        }

        if len(filters) > 0:
            params["items"]["filter"]["$or"] = filters

        if len(labels) > 0:
            for key, value in labels.items():
                params["items"]["filter"][f"labels.{key}"] = value

        request_data = Request(
            id=self.current_id, method=ApiMethod.select_items, params=params
        )

        self.update_headers({"Authorization": f"Bearer {self.get_token()}"})
        return self.make_requests(request_data.json())


    @increment_id
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
                "filter": filter.to_query() if isinstance(filter, Filter) else {}
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

    @increment_id
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

    @increment_id
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

    @warnings.deprecated("Use Filter based method instead")
    @increment_id
    @validate_arguments
    def select_signals(
        self,
        ids: List = [],
        name: str = "",
        labels: dict = {},
        limit: int = 10,
        skip: int = 0,
        include_items: bool = False,
        integration: str = None,
    ) -> Response:
        """
        Return signal metadata from selected signals and/or item.
        Parameters
        ----------
        ids: list, optional
            List of signals ids to retrieve. Empty list means take all.
        name: string, default: ""
            String containing regex of the name of an Signal.
        labels: dict default: {}
            Dictionary with labels and keys to be used as a filter
        
        limit: int, default: 10
            Number of signals to include in the match.
        
        skip: int default: 0
            Skip first N signals.
        include_items: bool default: False
            If set to true, include items metadata in the response.
        integration: str Default None
            Integration ID in string format. None means using the integration in credential file.
        Example
        -------
            >>> client.select_signals(
            >>>     ids = ['<SIGNAL_ID>'],
            >>>     name = "Electricity",
            >>>     labels = {"city": "Trondheim"},
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
        filters = []
        if len(ids) > 0:
            filters += [{"id": {"$in": ids}}]
        if name != "":
            filters += [{"name": {"$regex": name}}]

        params = {
            "signals": {"include": True, "filter": {}, "limit": limit, "skip": skip},
            "items": {"include": include_items},
            "integration": integration
        }

        # assert integration parameter
        if not params["integration"]:
            params["integration"] = self.authentication.integration_id

        if len(filters) > 0:
            params["signals"]["filter"]["$or"] = filters
        if len(labels) > 0:
            for key, value in labels.items():
                params["signals"]["filter"][f"labels.{key}"] = value

        request_data = Request(method=ApiMethod.select_signals, params=params)

        self.update_headers({"Authorization": f"Bearer {self.get_token()}"})
        return self.make_requests(request_data.json())

    @increment_id
    @validate_arguments
    def select_signals_filter(
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
                "skip": skip
            },
            "items": {"include": include_items},
        }

        # assert integration parameter
        if not params["integration"]:
            params["integration"] = self.authentication.integration_id

        request_data = Request(method=ApiMethod.select_signals, params=params)

        self.update_headers({"Authorization": f"Bearer {self.get_token()}"})
        return self.make_requests(request_data.json())
