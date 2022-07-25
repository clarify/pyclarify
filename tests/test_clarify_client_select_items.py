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

import sys
import unittest
import json
from unittest.mock import patch

# Standard library imports...

sys.path.insert(1, "src/")
from pyclarify import ClarifyClient, DataFrame
from pyclarify.views.items import ItemSelectView
from pyclarify.views.generics import Response, SelectItemsResponse
from pyclarify.query import Filter


class TestClarifyClientSelectItems(unittest.TestCase):
    def setUp(self):
        self.client = ClarifyClient("./tests/data/mock-clarify-credentials.json")

        with open("./tests/data/mock-clarify-client-select-items.json") as f:
            self.mock_data = json.load(f)
        self.test_cases = self.mock_data["test_cases"]

        with open("./tests/data/mock-client-common.json") as f:
            self.mock_data = json.load(f)
        self.mock_access_token = self.mock_data["mock_access_token"]

    @patch("pyclarify.jsonrpc.client.JSONRPCClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_all_item_data(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[0]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_items()

        for x in response_data.result.data:
            self.assertIsInstance(x, ItemSelectView)

    @patch("pyclarify.jsonrpc.client.JSONRPCClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_items_metadata_with_filter(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[0]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_items(
            filter=Filter(**test_case["args"]["filter"])
        )

        for x in response_data.result.data:
            self.assertIsInstance(x, ItemSelectView)

    @patch("pyclarify.jsonrpc.client.JSONRPCClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_items_metadata_with_all(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[0]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_items(**test_case["args"])

        for x in response_data.result.data:
            self.assertIsInstance(x, ItemSelectView)

    # @patch("pyclarify.jsonrpc.client.JSONRPCClient.get_token")
    # @patch("pyclarify.client.requests.post")
    # def test_get_items_data_with_none(self, client_req_mock, get_token_mock):
    #     test_case = self.test_cases[1]
    #     get_token_mock.return_value = self.mock_access_token
    #     client_req_mock.return_value.ok = True
    #     client_req_mock.return_value.json = lambda: test_case["response"]

    #     response_data = self.client.select_items()
    #     self.assertIsNone(response_data.result.data)
    #     self.assertIsInstance(response_data.result.data, DataFrame)

    # @patch("pyclarify.jsonrpc.client.JSONRPCClient.get_token")
    # @patch("pyclarify.client.requests.post")
    # def test_get_items_data_with_ids(self, client_req_mock, get_token_mock):
    #     test_case = self.test_cases[1]
    #     get_token_mock.return_value = self.mock_access_token
    #     client_req_mock.return_value.ok = True
    #     client_req_mock.return_value.json = lambda: test_case["response"]

    #     response_data = self.client.select_items(
    #         filter=Filter(**test_case["args"]["filter"])
    #     )

    #     self.assertIsNone(response_data.result.data)
    #     self.assertIsInstance(response_data.result.data, DataFrame)

    # @patch("pyclarify.jsonrpc.client.JSONRPCClient.get_token")
    # @patch("pyclarify.client.requests.post")
    # def test_get_items_data_with_not_before(self, client_req_mock, get_token_mock):
    #     test_case = self.test_cases[1]
    #     get_token_mock.return_value = self.mock_access_token
    #     client_req_mock.return_value.ok = True
    #     client_req_mock.return_value.json = lambda: test_case["response"]

    #     response_data = self.client.select_items(
    #         not_before=test_case["args"]["not_before"]
    #     )

    #     self.assertIsNone(response_data.result.data)
    #     self.assertIsInstance(response_data.result.data, DataFrame)

    # @patch("pyclarify.jsonrpc.client.JSONRPCClient.get_token")
    # @patch("pyclarify.client.requests.post")
    # def test_get_items_data_with_before(self, client_req_mock, get_token_mock):
    #     test_case = self.test_cases[1]
    #     get_token_mock.return_value = self.mock_access_token
    #     client_req_mock.return_value.ok = True
    #     client_req_mock.return_value.json = lambda: test_case["response"]

    #     response_data = self.client.select_items(
    #         before=test_case["args"]["before"]
    #     )

    #     self.assertIsNone(response_data.result.data)
    #     self.assertIsInstance(response_data.result.data, DataFrame)

    # @patch("pyclarify.jsonrpc.client.JSONRPCClient.get_token")
    # @patch("pyclarify.client.requests.post")
    # def test_get_items_data_with_rollup(self, client_req_mock, get_token_mock):
    #     test_case = self.test_cases[1]
    #     get_token_mock.return_value = self.mock_access_token
    #     client_req_mock.return_value.ok = True
    #     client_req_mock.return_value.json = lambda: test_case["response"]

    #     response_data = self.client.select_items(
    #         rollup=test_case["args"]["rollup"]
    #     )

    #     self.assertIsNone(response_data.result.data)
    #     self.assertIsInstance(response_data.result.data, DataFrame)

    # @patch("pyclarify.jsonrpc.client.JSONRPCClient.get_token")
    # @patch("pyclarify.client.requests.post")
    # def test_get_items_data_metadata_with_all(self, client_req_mock, get_token_mock):
    #     test_case = self.test_cases[1]
    #     get_token_mock.return_value = self.mock_access_token
    #     client_req_mock.return_value.ok = True
    #     client_req_mock.return_value.json = lambda: test_case["response"]

    #     response_data = self.client.select_items(
    #         filter=Filter(**test_case["args"]["filter"]),
    #         skip=test_case["args"]["skip"],
    #         not_before=test_case["args"]["not_before"],
    #         before=test_case["args"]["before"],
    #         rollup=test_case["args"]["rollup"],
    #     )

    #     self.assertIsNone(response_data.result.data)
    #     self.assertIsInstance(response_data.result.data, DataFrame)
    #     self.assertIsNone(response_data.error)

    @patch("pyclarify.jsonrpc.client.JSONRPCClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_1100_items_metadata_only(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[2]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_items(**test_case["args"])

        for x in response_data.result.data:
            self.assertIsInstance(x, ItemSelectView)


if __name__ == "__main__":
    unittest.main()
