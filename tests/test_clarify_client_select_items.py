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
from pyclarify import ClarifyClient, SignalInfo, DataFrame
from pyclarify.models.response import Response, SelectItemsResponse


class TestClarifyClientSelectItems(unittest.TestCase):
    def setUp(self):
        self.client = ClarifyClient("./tests/data/mock-clarify-credentials.json")

        with open("./tests/data/mock-clarify-client-select-items.json") as f:
            self.mock_data = json.load(f)
        self.test_cases = self.mock_data["test_cases"]

        with open("./tests/data/mock-client-common.json") as f:
            self.mock_data = json.load(f)
        self.mock_access_token = self.mock_data["mock_access_token"]

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_all_item_metadata(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[0]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_items_metadata()

        for x in response_data.result.items:
            self.assertIsInstance(response_data.result.items[x], SignalInfo)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_items_metadata_with_ids(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[0]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_items_metadata(ids=test_case["args"]["ids"])

        for x in response_data.result.items:
            self.assertIsInstance(response_data.result.items[x], SignalInfo)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_items_metadata_with_name(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[0]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_items_metadata(
            name=test_case["args"]["name"]
        )

        for x in response_data.result.items:
            self.assertIsInstance(response_data.result.items[x], SignalInfo)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_items_metadata_with_labels(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[0]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_items_metadata(
            labels=test_case["args"]["labels"]
        )

        for x in response_data.result.items:
            self.assertIsInstance(response_data.result.items[x], SignalInfo)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_items_metadata_with_all(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[0]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_items_metadata(**test_case["args"])

        for x in response_data.result.items:
            self.assertIsInstance(response_data.result.items[x], SignalInfo)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_items_data_with_none(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[1]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_items_data()

        self.assertIsNone(response_data.result.items)
        self.assertIsInstance(response_data.result.data, DataFrame)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_items_data_with_ids(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[1]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_items_data(ids=test_case["args"]["ids"])

        self.assertIsNone(response_data.result.items)
        self.assertIsInstance(response_data.result.data, DataFrame)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_items_data_with_not_before(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[1]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_items_data(
            not_before=test_case["args"]["not_before"]
        )

        self.assertIsNone(response_data.result.items)
        self.assertIsInstance(response_data.result.data, DataFrame)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_items_data_with_before(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[1]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_items_data(
            before=test_case["args"]["before"]
        )

        self.assertIsNone(response_data.result.items)
        self.assertIsInstance(response_data.result.data, DataFrame)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_items_data_with_rollup(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[1]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_items_data(
            rollup=test_case["args"]["rollup"]
        )

        self.assertIsNone(response_data.result.items)
        self.assertIsInstance(response_data.result.data, DataFrame)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_items_data_metadata_with_all(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[1]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_items_data(**test_case["args"])

        self.assertIsNone(response_data.result.items)
        self.assertIsInstance(response_data.result.data, DataFrame)
        self.assertIsNone(response_data.error)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_1100_items_metadata_only(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[2]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_items_metadata(**test_case["args"])

        for x in response_data.result.items:
            self.assertIsInstance(response_data.result.items[x], SignalInfo)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_item_with_id_and_limit_skip(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[3]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_items_data(**test_case["args"])
        self.assertIsInstance(response_data.result.data, DataFrame)
        self.assertIsNone(response_data.error)


if __name__ == "__main__":
    unittest.main()
