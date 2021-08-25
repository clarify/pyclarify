"""
Service Intercase module is the main module of PyClarify.

The module provides a class for setting up a HTTPClient which will communicate with
the Clarify API. Methods for reading and writing to the API is implemented with the
help of jsonrpcclient framework. 
"""

import requests
import json
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s %(message)s ", level=logging.INFO)


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
            "POST", self.base_url, data=json.dumps(payload), headers=self.headers
        )
        logging.info(f"<-- {self.base_url} ({response.status_code})")

        if response.ok:
            return response.json()
        else:
            return {"error": response.status_code}

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
        return payload

    def update_headers(self, headers):
        """
        Updates headers of client.
        
        Parameters:
            headers (dict): The headers to be added with key being parameter and 
                            value being value.
            
        """
        for key, value in headers.items():
            self.headers[key] = value
