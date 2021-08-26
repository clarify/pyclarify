"""
Service Intercase module is the main module of PyClarify.

The module provides a class for setting up a HTTPClient which will communicate with
the Clarify API. Methods for reading and writing to the API is implemented with the
help of jsonrpcclient framework. 
"""

import requests
import json
import logging
import models
from models.data import NumericalValuesType
from typing import List

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s %(message)s ", level=logging.INFO)


def mockup_get_token():
    return 'token1234567890'


class ServiceInterface:
    def __init__(
            self, base_url,
    ):
        self.base_url = base_url
        self.headers = {"content-type": "application/json"}
        self.current_id = 0

    def send(self, payload):
        """
        Returns json dict of JSONPRC request.
        
        Parameters:
            payload (JSONRPC dict): A dictionary in the form of a JSONRPC request.
        
        Returns:
            JSON dictionary response.
        
        """
        logging.info(f"--> {self.base_url}, req: {payload}")
        response = requests.request(
            "POST", self.base_url, data=payload, headers=self.headers
        )
        logging.info(f"<-- {self.base_url} ({response.status_code})")

        if response.ok:
            return response.json()
        else:
            return {"error": {"code": response.status_code, "message": "HTTP Response Error"}}

    def create_payload(self, method, params):
        """
        Creates a JSONRPC request.
        
        Parameters:
            method (str): The RPC method to call. 
            params (dict): The arguments to the method call.
        """
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self.current_id,
            "params": params,
        }
        self.current_id += 1
        return json.dumps(payload)

    def update_headers(self, headers):
        """
        Updates headers of client.
        
        Parameters:
            headers (dict): The headers to be added with key being parameter and 
                            value being value.
            
        """
        for key, value in headers.items():
            self.headers[key] = value


class ClarifyInterface(ServiceInterface):
    def __init__(self):
        super().__init__('https://api.clarify.us/v1/rpc')
        self.update_headers({"X-API-Version": "1.0"})

    def add_data_single_signal(self, integration: str, input_id: str,
                               times: list, values: NumericalValuesType) -> models.requests.ResponseSave:
        """
        This call inserts data for one signal. The signal is uniquely identified by its input ID in combination with
        the integration ID. If no signal with the given combination exists, an empty signal is created.
        Meta-data for the signal can be provided either through the admin panel or using
        the 'add_metadata' call.
        Mirrors the API call (`integration.Insert`)[https://docs.clarify.us/reference#integrationinsert] for a single
        signal.

        Parameters
        ----------
        integration
        input_id
        times
        values

        Returns
        -------

        """
        data = models.data.ClarifyDataFrame(times=times, series={input_id: values})
        request_data = models.requests.InsertJsonRPCRequest(params=models.requests.ParamsInsert(integration=integration,
                                                                                                data=data))
        self.update_headers({"Authorization": f"Bearer {mockup_get_token()}"})
        result = self.send(request_data.json())
        return models.requests.ResponseSave(**result)

    def add_data_multiple_signals(self, integration: str, input_id_lst: List[str],
                                  times: list, values_lst: List[NumericalValuesType]) -> models.requests.ResponseSave:
        """
        This call inserts data for multiple signals. The signals are uniquely identified by its input ID in
        combination with the integration ID. If no signal with the given combination exists, an empty signal is created.
        Meta-data for the signal can be provided either through the admin panel or using  the 'add_metadata' call.
        Mirrors the API call (`integration.Insert`)[https://docs.clarify.us/reference#integrationinsert] for multiple
        signals.

        Parameters
        ----------
        integration :
        times :
        input_id_lst :
        values_lst :

        Returns
        -------

        """
        series_dict = {input_id: values for input_id, values in zip(input_id_lst, values_lst)}
        data = models.data.ClarifyDataFrame(times=times, series=series_dict)
        request_data = models.requests.InsertJsonRPCRequest(params=models.requests.ParamsInsert(integration=integration,
                                                                                                data=data))
        self.update_headers({"Authorization": f"Bearer {mockup_get_token()}"})
        result = self.send(request_data.json())
        return models.requests.ResponseSave(**result)

