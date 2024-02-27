"""
Copyright 2023 Clarify

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

import sys
import unittest
import json
from datetime import datetime, timedelta
from unittest.mock import patch

from pydantic import ValidationError

sys.path.insert(1, "src/")
from pyclarify import ItemAggregation, Calculation
from pyclarify import Client, DataFrame
from pyclarify.views.items import ItemSelectView
from pyclarify.query import Filter
from pyclarify.fields.error import Error


class TestClarifyClientSelectItems(unittest.TestCase):
    def setUp(self):
        self.client = Client("./tests/mock_data/mock-clarify-credentials.json")

        with open("./tests/mock_data/evaluate.json") as f:
            self.mock_data = json.load(f)
        test_data = self.mock_data["evaluate"]
        self.args = test_data["args"]
        self.response = test_data["response"]
        self.error = test_data["error"]
        self.http_error = test_data["http_error"]

        with open("./tests/mock_data/mock-client-common.json") as f:
            self.mock_data = json.load(f)
        self.mock_access_token = self.mock_data["mock_access_token"]

    def test_get_data_with_no_params(self):
        with self.assertRaises(ValidationError):
            self.client.evaluate()


    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_data_with_only_rollup(self, client_req_mock, get_token_mock):
        return_value = self.response
        return_value["result"]["included"] = None
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: return_value

        response_data = self.client.evaluate(rollup="PT5M")
        self.assertIsInstance(response_data.result.data, DataFrame)

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_items_except_included(self, client_req_mock, get_token_mock):
        return_value = self.response
        return_value["result"]["included"] = None
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: return_value

        response_data = self.client.evaluate(**self.args)

        self.assertIsInstance(response_data.result.data, DataFrame)

    
    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_items_with_included(self, client_req_mock, get_token_mock):
        return_value = self.response
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: return_value

        response_data = self.client.evaluate(**self.args)

        self.assertIsInstance(response_data.result.data, DataFrame)

        for x in response_data.result.included.items:
            self.assertIsInstance(x, ItemSelectView)

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_internal_error(self, client_req_mock, get_token_mock):
        return_value = self.error
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: return_value

        response_data = self.client.evaluate(**self.args)

        if isinstance(response_data.error, list):
            error = response_data.error[0]
        else:
            error = response_data.error

        self.assertIsInstance(error, Error)
        self.assertEqual(error.code, return_value["error"]["code"])
        self.assertEqual(error.message, return_value["error"]['message'])
        self.assertEqual(error.data.model_dump(), return_value["error"]["data"])
    
    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_http_error(self, client_req_mock, get_token_mock):
        return_value = self.http_error
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = False
        client_req_mock.return_value.status_code = return_value["status_code"]
        client_req_mock.return_value.reason = return_value["reason"]
        client_req_mock.return_value.text = return_value["text"]
        response_data = self.client.evaluate(**self.args)
        if isinstance(response_data.error, list):
            error = response_data.error[0]
        else:
            error = response_data.error
        self.assertIsInstance(error, Error)
        self.assertEqual(error.code, return_value["status_code"])
        self.assertEqual(error.message, f"HTTP Response Error: {return_value['reason']}")
        self.assertEqual(error.data, return_value["text"])


if __name__ == "__main__":
    unittest.main()
