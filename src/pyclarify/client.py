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
from typing import List, Dict
from pydantic import validate_arguments

from pyclarify.models.data import NumericalValuesType, Signal, DataFrame, InputID
from pyclarify.models.requests import (
    SaveResponse,
    InsertParams,
    InsertRequest,
    SaveRequest,
    SaveParams,
    ItemSelect,
    SelectResponse,
    SelectRequest,
)
from pyclarify.oauth2 import GetToken


def increment_id(func):
    """
    Decorator which increments the current id variable.

    Parameters
    ----------
    func : function
        Decorator wraps around function using @increment_id

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
        Authenticates the client by using the GetToken class (see oauth2.py)

        Parameters
        ----------
        clarify_credentials : str/dict
            The path to the clarify_credentials.json downloaded from the Clarify app,
            or json/dictionary of the content in clarify_credentials.json

        Returns
        -------
        bool
            True if valid credentials is passed otherwise false
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
            payload string in JSONRPC format
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
    def insert(self, data: DataFrame) -> SaveResponse:
        """
        This call inserts data for one signal. The signal is uniquely identified by its input ID in combination with
        the integration ID. If no signal with the given combination exists, an empty signal is created.
        Meta-data for the signal can be provided either through the admin panel or using
        the 'add_metadata' call.
        Mirrors the API call (`integration.Insert`)[https://docs.clarify.io/reference#integrationinsert] for a single
        signal.

        Parameters
        ----------
        data : DataFrame
             Dataframe with the field
             -   `times`:  List of timestamps (either as a python datetime or as `YYYY-MM-DD[T]HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]]]`
                to insert.
             - `values` : Dict[InputID, List[Union[None, float, int]]]
                Map of inputid to Array of data points to insert by Input ID. The length of each array must match that of the times array.
                To omit a value for a given timestamp in times, use the value null.

        Returns
        -------
        SaveResponse
            In case of a valid return value, returns a pydantic model with the following format
            `{
                "jsonrpc": "2.0",
                "id": 1,
                "result":
                  { "signalsByInput": map of Input ID => SaveResult
                  }
             }`
           Where `SaveResult` is a pydantic model with field `id: str` (Unique ID of the saved instance)
           and  `created: bool` (True if a new instance was created).
           In case of the error the method return a pydantic model with the following format:
            `{
                "jsonrpc": "2.0",
                "id": 1,
                "error": {
                    "code": -32602,
                    "message": "Invalid params",
                    "data": {
                        "trace": "00000000000000000000",
                        "params": {
                            "integration": ["required"]
                        }
                    }
                }
             }`
        """

        request_data = InsertRequest(
            params=InsertParams(
                integration=self.authentication.integration_id, data=data
            )
        )

        self.update_headers({"Authorization": f"Bearer {self.get_token()}"})
        result = self.send(request_data.json())
        return SaveResponse(**result)

    @increment_id
    @validate_arguments
    def save_signals(
        self, inputs: Dict[InputID, Signal], created_only: bool
    ) -> SaveResponse:
        """
        This call inserts metadata for multiple signals. The signals are uniquely identified by its input ID in
        combination with the integration ID. A List of Signals should be provided with the intended meta-data.
        Mirrors the API call (`integration.SaveSignals`)[https://docs.clarify.io/reference#integrationsavesignals] for
        multiple signals.

        Parameters
        ----------
        inputs: Dict[InputID, List[Signal]]
            List of `Signal` objects. The `Signal` object contains metadata for a signal.
            Check (`Signal (API)`)[https://docs.clarify.io/reference#signal]

        created_only: bool
            If set to true, skip update of information for existing signals. That is, all Input IDs that map to
            existing signals are silently ignored.

        Returns
        -------
        SaveResponse
            In case of a valid return value, returns a pydantic model with the following format
            `{
                "jsonrpc": "2.0",
                "id": 1,
                "result":
                  { "signalsByInput": map of Input ID => SaveResult
                  }
             }`
           Where `SaveResult` is a pydantic model with field `id: str` (Unique ID of the saved instance)
           and  `created: bool` (True if a new instance was created).
           In case of the error the method return a pydantic model with the following format:
            `{
                "jsonrpc": "2.0",
                "id": 1,
                "error": {
                    "code": -32602,
                    "message": "Invalid params",
                    "data": {
                        "trace": "00000000000000000000",
                        "params": {
                            "integration": ["required"]
                        }
                    }
                }
             }`
        """
        request_data = SaveRequest(
            params=SaveParams(
                integration=self.authentication.integration_id,
                inputs=inputs,
                createdOnly=created_only,
            )
        )

        self.update_headers({"Authorization": f"Bearer {self.get_token()}"})
        result = self.send(request_data.json())

        return SaveResponse(**result)

    @increment_id
    @validate_arguments
    def select_items(self, params: ItemSelect) -> SelectResponse:
        """
        Return item data and metadata, mirroring the Clarify API call (`item.Select`)[https://docs.clarify.io/reference].

        Parameters
        ----------
        params : ItemSelect
            Data model with all the possible settings for method. Fields include
            - `items`:
               > Select items to include (data for).
              - `include` | **bool** | default: False
                > Set to true to render item meta-data in the response.
              - `filter` | **Dict**:
                > Rest-layer style item filter (potentially with limited query options).
                > Example: {"id":{"$in": ["<id1>", "<id2>"]}}
              - `limit` | **int(min:0,max:50)** | default=`10`
                > Limit number of items (max value to be adjusted after tuning).
              - `skip` | **int**| default=`0`
                > Skip first N items.
            - `times`:
              > Select times to include; ignored if no series are selected.
              - `before` | **str(`""` | |RFC3339 timestamp)**  | default=`""`
              - `notBefore` | **str(`""` || RFC3339 timestamp)**  |  default=`""`
            - `series`:
              > Select which data series to include.
              - `items` | bool | default=False
                > include items mapped by ID in the response data frame.
              - `aggregates` | bool | default=False
                > include aggregated values `"count"`, `"sum"`, `"min"` and `"max"` across all items in the response data frame.
        Example:
            {
                "items": {
                    "include": true,
                    "filter": {"id":{"$in": ["<id1>", "<id2>"]}}
                },
                "times": {
                    "notBefore": "2020-01-01T01:00:00Z"
                },
                "series": {
                    "items": true,
                    "aggregates": true
                }
            }

        Returns
        -------
        SelectResponse
        Data model with the results of the method. Data and metadata can be found in the `result` field, with the
        attributes `result.items` as a dictionary of `item_id` and `Signal` (definition can be found in
        `pyclarify.models.data`) and `result.data` containing a `DataFrame` object with the resulting data
        and aggregates (in case the parameter `series.aggregates` is set to True).
        Example:
            {
                "jsonrpc": "2.0",
                "result": {
                    "items": {
                        "<id1>": {
                            // Signal schema
                        },
                        "<id2>": {
                            //  Signal schema
                        },
                    },
                    "data": { // DataFrame schema
                        "times": ["2020-01-01T01:00:00Z","2020-01-01T02:00:00Z","2020-01-01T03:00:00Z"],
                        "series": {
                            "count": [2, 1, 1],
                            "sum":[20.4, 0.0, 2.7],
                            "min": [10.2, 0.0, 2.7],
                            "max":[10.2, 0.0, 2.7],
                            "<id1>": [10.2, null, 2.7],
                            "<id2>": [10.2, 0.0, null]
                        }
                    }
                }
            }

        """
        request_data = SelectRequest(params=params)

        self.update_headers({"Authorization": f"Bearer {self.get_token()}"})
        result = self.send(request_data.json())

        return SelectResponse(**result)
