"""
Copyright 2021 Clarify

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
from pydantic import validate_arguments

from pyclarify.models.data import DataFrame
from pyclarify.models.requests import Request, ApiMethod
from pyclarify.models.response import Response
from pyclarify.oauth2 import GetToken


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


class RawClient:
    def __init__(
        self,
        base_url,
    ):
        self.base_url = base_url
        self.headers = {"content-type": "application/json"}
        self.current_id = 0
        self.authentication = None

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

    def send(self, payload):
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
        logging.info(f"--> {self.base_url}, req: {payload}")
        response = requests.post(self.base_url, data=payload, headers=self.headers)
        logging.info(f"<-- {self.base_url} ({response.status_code})")

        if response.ok:
            return response.json()
        else:
            return {
                "error": {
                    "code": response.status_code,
                    "message": "HTTP Response Error",
                }
            }

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


class APIClient(RawClient):
    def __init__(self, clarify_credentials):
        super().__init__(None)
        self.update_headers({"X-API-Version": "1.1"})
        self.authentication = GetToken(clarify_credentials)
        self.base_url = f"{self.authentication.api_url}rpc"

    @increment_id
    @validate_arguments
    def insert(self, data: DataFrame) -> Response:
        """
        This call inserts data for one signal. The signal is uniquely identified by its input ID in combination with
        the integration ID. If no signal with the given combination exists, an empty signal is created.
        Mirroring the Clarify API call `integration.insert <https://docs.clarify.io/v1.1/reference/integrationinsert>`_ .

        Parameters
        ----------
        data : DataFrame
            Dataframe with the fields:

            - times:  List of timestamps 
                Either as a python datetime or as 
                YYYY-MM-DD[T]HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]]] to insert.

            - values: Dict[InputID, List[Union[None, float, int]]]
                Map of inputid to Array of data points to insert by Input ID. 
                The length of each array must match that of the times array.
                To omit a value for a given timestamp in times, use the value null.

        Returns
        -------
        Response
            In case of a valid return value, returns a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                >>> id = '1'
                >>> result = InsertResponse(
                >>>             signalsByInput = {'id': InsertSummary(id = <signal_id>, created = True)}
                >>> ) 
                >>> error = None

            Where InsertSummary is a pydantic model with field id: str (unique ID of the saved instance)
            and created: bool (True if a new instance was created, False is the instance already existed).

            In case of the error the method return a pydantic model with the following format:

            Example
            -------

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
        result = self.send(request_data.json())
        return Response(**result)

    @increment_id
    @validate_arguments
    def save_signals(self, params: dict) -> Response:
        """
        This call inserts metadata for one or multiple signals. The signals are uniquely identified by its <input_ID>.
        Mirroring the Clarify API call `integration.saveSignals <https://docs.clarify.io/v1.1/reference/integrationsavesignals>`_ .

        Parameters
        ----------
        params: Dict[inputs, createOnly]

            - inputs: Dict[InputID, List[SignalInfo]]
                The SignalInfo object contains metadata for a signal. 
                Click `here <https://docs.clarify.io/reference/signal>`_ for more information.

            - created_only: bool
                If True then only published signal with input id equal to input_id will be updated. 
                If False then all the signal with input id equal to input_id will be updated
        
            Example
            -------

                >>> signal = SignalInfo(
                >>>    name = "Home temperature",
                >>>    description = "Temperature in the bedroom",
                >>>    labels = {"data-source": ["Raspberry Pi"], "location": ["Home"]}
                >>> )
                >>> params = {"inputs": {"id1": signal, "createOnly": False}

        Returns
        -------
        Response
            In case of a valid return value, returns a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                >>> id = '1'
                >>> result = SaveSignalsResponse(
                >>>             signalsByInput={
                >>>                 <INPUT_ID>: SaveSummary(id=<signal_id>, created=True, updated=False)
                >>>              }
                >>>          )
                >>> error = None

            WhereSaveSummary is a pydantic model with field id: str (Unique ID of the saved instance), 
            created: bool (True if a new instance was created) and
            updated: bool (True if the metadata where updated).

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
        result = self.send(request_data.json())
        return Response(**result)

    @increment_id
    @validate_arguments
    def select_items(self, params: dict) -> Response:
        """
        Return item data and metadata.
        Mirroring the Clarify API call `clarify.selectItems <https://docs.clarify.io/v1.1/reference/itemselect>`_ .

        Parameters
        ----------
        params : Dict
            Fields include:

            - items: dict
                Query which items to select, and configure inclusion or exclusion of meta-data in the response.
                By default, no meta-data is included.

                - include: bool, default False
                    Set to true to include matched resources in the response.

                - filter: dict, `Resource Filter <https://docs.clarify.io/v1.1/reference/filtering>`_
                    Filter which resources to include.

                - limit: int, default 10
                    Number of resources to include in the match.

                - skip: int, default 0
                    Skip the n first items.

            - data: dict
                Configure which data to include in the response.

                - include: bool, default False
                    Include the timeseries data in the response.

                - notBefore: string(RFC 3339 timestamp), optional
                    An RFC3339 time describing the inclusive start of the window.

                - before: string(RFC 3339 timestamp), optional
                    An RFC3339 time describing the exclusive end of the window.

                - rollup: RFC 3339 duration or "window", default None
                    If RFC 3339 duration is specified, roll-up the values into either the full time window
                    (`notBefore` -> `before`) or evenly sized buckets.
                    For more information click `here <https://docs.clarify.io/v1.1/reference/data-query>`_ .

            Example
            -------

                >>> {
                >>>    "items": {"include":True, "filter": {"id": {"$in": [<item_id>]}} },
                >>>    "data": {"include": True}
                >>> }

        Returns
        -------
        Response
            In case of a valid return value, returns a pydantic model with the following (example) format:

                >>> {
                >>>    "jsonrpc": "2.0",
                >>>    "id": "1",
                >>>    "result": {
                >>>    "items": {
                >>>        "item_id": {
                >>>        "name": "item_name",
                >>>        "type": "numeric"
                >>>        }
                >>>    },
                >>>    "data": {
                >>>        "times": ["2021-10-10T21:00:00+00:00", "2021-10-10T22:00:00+00:00"],
                >>>        "series": {
                >>>        "item_id_avg": [0.0, 0.0],
                >>>        "item_id_count": [20.0, 20.0],
                >>>        "item_id_max": [0.0, 0.0],
                >>>        "item_id_min": [0.0, 0.0],
                >>>        "item_id_sum": [0.0, 0.0]
                >>>        }
                >>>    },
                >>>    "error": null
                >>>    }
                >>> }

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
        result = self.send(request_data.json())

        return Response(**result)

    @increment_id
    @validate_arguments
    def select_signals(self, params: dict) -> Response:
        """
        Return signal meta-data and/or exposed items. This call is a recommend step before doing a publish_signals call.
        Mirroring the Clarify API call `admin.selectSignals <https://docs.clarify.io/v1.1/reference/adminselectsignals>`_ .

        Parameters
        ----------
        params : Dict
            Data model with all the possible settings for method. Fields include:

            - signals: dict
                    Select signals to include (data for).

                    - include: bool, default: False
                        Set to true to render item meta-data in the response.

                    - filter: dict
                        Click `here <https://docs.clarify.io/v1.1/reference/filtering>`_ for more information.

                    - limit: int, min=0, max= 1000, default=50
                        Limit number of signals (max value to be adjusted after tuning).

                    - skip: int, default=0
                        Skip first N signals.

            - items: dict
                Configure item inclusion.

                - include: bool, default=False
                    Set to true to include items exposed by the selected signals.

            Example
            -------
                >>> {
                >>>     "signals": {
                >>>         "include": true,
                >>>         "filter": {"id":{"$in": ["<signal_id1>", "<signal_id2>"]}}
                >>>     },
                >>>     "items": {
                >>>         "include": true
                >>>     }
                >>> }

        Returns
        -------
        Response
            In case of a valid return value, returns a pydantic model with the following format:

                >>> {
                >>>     "jsonrpc": "2.0", 
                >>>     "id": "1",
                >>>     "result": {
                >>>        "signals": {"<signal_id>": Signal},
                >>>        "items": {"<item_id>": SignalInfo},
                >>>     "error": null
                >>> }

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
        result = self.send(request_data.json())
        return Response(**result)

    @increment_id
    @validate_arguments
    def publish_signals(self, params: dict) -> Response:
        """
        Publishes a signal to create an item.
        Mirroring the Clarify API call `admin.publishSignals <https://docs.clarify.io/v1.1/reference/adminpublishsignals>`_ .

        Parameters
        ----------
        params : Dict
            
            - itemsBySignal: Dict
                Select signals to include (data for).

                - signal_id: SignalInfo

            - createOnly: bool
                
            >>> {
            >>>    "itemsBySignal": {
            >>>         "<signal_id>" : SignalInfo(name= "Home temperature")
            >>>     },
            >>>     "createOnly": False
            >>> }

        Example
        -------
        Response
            In case of a valid return value, returns a pydantic model with the following format:

                >>> {
                >>>     "jsonrpc": "2.0",
                >>>     "id": "1", 
                >>>     "result": {
                >>>         "itemsBySignal": {
                >>>             "<signal_id>": {
                >>>                 "id": "<item_id>",
                >>>                 "created": true, 
                >>>                 "updated": false
                >>>             }
                >>>         }
                >>>     }, 
                >>>     "error": null
                >>> }

            In case of the error the method return a pydantic model with the following format:

                >>> jsonrpc = '2.0'
                >>> id = '1'
                >>> result = None
                >>> error = Error(
                >>>         code = '-32602',
                >>>         message = 'Invalid params', 
                >>>         data = ErrorData(trace = <trace_id>, params = {})
                >>> )

        Returns
        -------
        Response
            In case of a valid return value, returns a pydantic model with the following format:

                >>> {
                >>>     "jsonrpc": "2.0",
                >>>     "id": "1", 
                >>>     "result": {
                >>>         "itemsBySignal": {
                >>>             "<signal_id>": {
                >>>                 "id": "<item_id>",
                >>>                 "created": true, 
                >>>                 "updated": false
                >>>             }
                >>>         }
                >>>     }, 
                >>>     "error": null
                >>> }

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
        result = self.send(request_data.json())
        return Response(**result)
