"""
Service Intercase module is the main module of PyClarify.

The module provides a class for setting up a HTTPClient which will communicate with
the Clarify API. Methods for reading and writing to the API is implemented with the
help of jsonrpcclient framework. 
"""

import requests
import json
import logging
import functools
from typing import List

from pyclarify.models.data import NumericalValuesType, Signal, ClarifyDataFrame
from pyclarify.models.requests import (
    ResponseSave,
    ParamsInsert,
    InsertJsonRPCRequest,
    SaveJsonRPCRequest,
    ParamsSave,
)

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s %(message)s ", level=logging.INFO)


def mockup_get_token():
    return "token1234567890"


def increment_id(func):
    """
    Decorator which increments the current id variable.

    Returns
    -------
    [type]
        [description]
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args[0].current_id += 1  # args[0] = self
        return func(*args, **kwargs)

    return wrapper


class ServiceInterface:
    def __init__(
            self,
            base_url,
    ):
        self.base_url = base_url
        self.headers = {"content-type": "application/json"}
        self.current_id = 0

    def send(self, payload):
        """
        Returns json dict of JSONPRC request.

        Parameters
        ----------
        payload : JSONRPC dict
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
        Creates a JSONRPC request.

        Parameters
        ----------
        method : str
            The RPC method to call.
        params : dict
            The arguments to the method call.

        Returns
        -------
        [type]
            [description]
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


class ClarifyInterface(ServiceInterface):
    def __init__(self):
        super().__init__("https://api.clarify.us/v1/rpc")
        self.update_headers({"X-API-Version": "1.0"})

    @increment_id
    def add_data_single_signal(
            self, integration: str, input_id: str, times: list, values: NumericalValuesType
    ) -> ResponseSave:
        """
        This call inserts data for one signal. The signal is uniquely identified by its input ID in combination with
        the integration ID. If no signal with the given combination exists, an empty signal is created.
        Meta-data for the signal can be provided either through the admin panel or using
        the 'add_metadata' call.
        Mirrors the API call (`integration.Insert`)[https://docs.clarify.us/reference#integrationinsert] for a single
        signal.

        Parameters
        ----------
        integration : str
            The ID if the integration to save signal information for.
        input_id : str
            An Input ID maps uniquely to one signal within an integration. For all API calls that accept Input IDs,
            new signals are automatically created when needed. This means you do not need to create a signal before
            writing data to it. Should follow regex: "^[a-z0-9_-]{1,40}$"
        times : list
            List of timestamps (either as a python datetime or as `YYYY-MM-DD[T]HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]]]`
            to insert.
        values : List[NumericalValuesType]
            Array of data points to insert by Input ID. The length of each array must match that of the times array.
            To omit a value for a given timestamp in times, use the value null.

        Returns
        -------
        ResponseSave
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
        data = ClarifyDataFrame(times=times, series={input_id: values})
        request_data = InsertJsonRPCRequest(
            params=ParamsInsert(integration=integration, data=data)
        )
        self.update_headers({"Authorization": f"Bearer {mockup_get_token()}"})
        result = self.send(request_data.json())
        return ResponseSave(**result)

    @increment_id
    def add_data_multiple_signals(
            self,
            integration: str,
            input_id_lst: List[str],
            times: list,
            values_lst: List[List[NumericalValuesType]],
    ) -> ResponseSave:
        """
        This call inserts data for multiple signals. The signals are uniquely identified by its input ID in
        combination with the integration ID. If no signal with the given combination exists, an empty signal is created.
        Meta-data for the signal can be provided either through the admin panel or using  the 'add_metadata' call.
        Mirrors the API call (`integration.Insert`)[https://docs.clarify.us/reference#integrationinsert] for multiple
        signals.

        Parameters
        ----------
        integration : str
            The ID if the integration to save signal information for.
        input_id_lst: List[str]
            List of input_ids to be added
        times: list
            List of timestamps (either as a python datetime or as `YYYY-MM-DD[T]HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]]]`
            to insert.
        values_lst : List[List[NumericalValuesType]]
            List of list of data points to insert for each respective Input ID in the `input_id_lst`. The length of
            each array must match that of the times array. To omit a value for a given timestamp in times,
            use the value None.

        Returns
        -------
        ResponseSave

        """
        series_dict = {input_id: values for input_id, values in zip(input_id_lst, values_lst)}
        data = ClarifyDataFrame(times=times, series=series_dict)
        request_data = InsertJsonRPCRequest(params=ParamsInsert(integration=integration, data=data))

        self.update_headers({"Authorization": f"Bearer {mockup_get_token()}"})
        result = self.send(request_data.json())

        return ResponseSave(**result)

    @increment_id
    def add_metadata_signals(
            self,
            integration: str,
            signal_metadata_list: List[Signal],
            created_only: bool = False,
    ) -> ResponseSave:
        """
        This call inserts metadata for multiple signals. The signals are uniquely identified by its input ID in
        combination with the integration ID. A List of Signals should be provided with the intended meta-data.
        Mirrors the API call (`integration.SaveSignals`)[https://docs.clarify.us/reference#integrationsavesignals] for
        multiple signals.

        Parameters
        ----------
        integration : str
            The ID if the integration to save signal information for.

        signal_metadata_list : List[Signal]
            List of `Signal` objects. The `Signal` object contains metadata for a signal.
            Check (`Signal (API)`)[https://docs.clarify.us/reference#signal]

        created_only: bool
            If set to true, skip update of information for existing signals. That is, all Input IDs that map to
            existing signals are silently ignored.



        Returns
        -------
        ResponseSave
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

        input_map = {signal.name: signal for signal in signal_metadata_list}
        request_data = SaveJsonRPCRequest(
            params=ParamsSave(
                integration=integration, inputs=input_map, createdOnly=created_only
            )
        )

        self.update_headers({"Authorization": f"Bearer {mockup_get_token()}"})
        result = self.send(request_data.json())

        return ResponseSave(**result)
