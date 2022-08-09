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

from pyclarify.__utils__.exceptions import AuthError
from pyclarify.fields.constraints import ApiMethod
from pyclarify.fields.error import Error
from pyclarify.views.generics import Response
from pyclarify.__utils__.time import compute_iso_timewindow
from pyclarify.__utils__.time import time_to_string

from .oauth2 import Authenticator
from .pagination import ItemIterator, TimeIterator


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
        payload_list = []
        payload = json.loads(args[1])
        API_LIMIT = None
        selecting_dataframe = False
        if payload["method"] == ApiMethod.select_items:
            API_LIMIT = 1000

        if payload["method"] == ApiMethod.select_signals:
            API_LIMIT = 1000

        if payload["method"] == ApiMethod.select_dataframe:
            API_LIMIT = 50
            selecting_dataframe = True

        if API_LIMIT is not None:
            user_limit = payload["params"]["query"]["limit"]
            skip = payload["params"]["query"]["skip"]

            for skip, limit in SelectIterator(
                user_limit=user_limit, limit_per_call=API_LIMIT, skip=skip
            ):
                current_payload = deepcopy(payload)
                current_payload["params"]["query"]["limit"] = limit
                current_payload["params"]["query"]["skip"] = skip
                if selecting_dataframe:
                    times = current_payload["params"]["data"]["filter"]["times"]
                    user_gte = times.pop("$gte", None)
                    user_lt = times.pop("$lt", None)
                    for start_time, end_time in TimeIterator(
                        user_gte, user_lt, current_payload["params"]["data"]["rollup"]
                    ):
                        current_payload["params"]["data"]["filter"]["times"]["$gte"] = time_to_string(start_time)
                        current_payload["params"]["data"]["filter"]["times"]["$lt"] = time_to_string(end_time)
                        payload_list += [current_payload]
                else:
                    payload_list += [payload]
        else:
            payload_list = [payload]

        args[0].payload_list = payload_list

        return func(*args, **kwargs)

    return wrapper


class JSONRPCClient:
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
        Authenticates the client by using the Authenticator class (see oauth2.py).

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
            self.authentication = Authenticator(clarify_credentials)
            return True
        except AuthError:
            return False

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
