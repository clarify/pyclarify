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

sys.path.insert(1, "src/")
from pyclarify import Client
from pyclarify.views.items import ItemSelectView
from pyclarify.query import Filter


class TestClarifyClientSelectItems(unittest.TestCase):
    def setUp(self):
        self.client = Client("./tests/mock_data/mock-clarify-credentials.json")

        with open("./tests/mock_data/items.json") as f:
            self.mock_data = json.load(f)
        self.test_cases = self.mock_data["select_items"]["test_cases"]

        with open("./tests/mock_data/mock-client-common.json") as f:
            self.mock_data = json.load(f)
        self.mock_access_token = self.mock_data["mock_access_token"]

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_all_item_data(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[0]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_items()
        for x in response_data.result.data:
            self.assertIsInstance(x, ItemSelectView)

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
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

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_items_metadata_with_all(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[0]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_items(**test_case["args"])

        for x in response_data.result.data:
            self.assertIsInstance(x, ItemSelectView)

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
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
