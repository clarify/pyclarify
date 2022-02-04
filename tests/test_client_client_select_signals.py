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
from pyclarify import ClarifyClient, Signal, SignalInfo


class TestClarifyClientSelectSignals(unittest.TestCase):
    def setUp(self):
        self.client = ClarifyClient("./tests/data/mock-clarify-credentials.json")

        with open("./tests/data/mock-clarify-client-select-signals.json") as f:
            self.mock_data = json.load(f)
        self.test_cases = self.mock_data["test_cases"]

        with open("./tests/data/mock-client-common.json") as f:
            self.mock_data = json.load(f)
        self.mock_access_token = self.mock_data["mock_access_token"]

    """
    ids: List = [],
    name: str = "",
    labels: dict = {},
    limit: int = 10,
    skip: int = 0,
    include_items: bool = False
    """


    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_empty_request(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[0]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_signals(**test_case["args"])

        # Assert content of return
        for key, signal in response_data.result.signals.items():
            self.assertIsInstance(signal, Signal)

        for key, item in response_data.result.items.items():
            self.assertIsInstance(item, SignalInfo)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_filter_id(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[1]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_signals(**test_case["args"])

        # Assert content of return
        for key, signal in response_data.result.signals.items():
            self.assertIsInstance(signal, Signal)


    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def get_nothing(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[2]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_signals(**test_case["args"])

        # Assert no Items or Signals
        self.assertEqual(response_data.result.items, {})
        self.assertEqual(response_data.result.signals, {})

#TODO: Write more rigorous tests

if __name__ == "__main__":
    unittest.main()
