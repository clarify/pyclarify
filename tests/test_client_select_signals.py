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
from pyclarify import ClarifyClient
from pyclarify.views.signals import SignalSelectView
from pyclarify.query import Filter


class TestClarifyClientSelectSignals(unittest.TestCase):
    def setUp(self):
        self.client = ClarifyClient("./tests/data/mock-clarify-credentials.json")

        with open("./tests/data/mock-clarify-client-select-signals.json") as f:
            self.mock_data = json.load(f)
        self.test_cases = self.mock_data["test_cases"]

        with open("./tests/data/mock-client-common.json") as f:
            self.mock_data = json.load(f)
        self.mock_access_token = self.mock_data["mock_access_token"]

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_empty_request(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[0]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_signals(**test_case["args"])

        # Assert content of return
        for signal in response_data.result.data:
            self.assertIsInstance(signal, SignalSelectView)


    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_filter(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[1]
        filter = Filter(**test_case["args"]["filter"])
        include = test_case["args"]["include"]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_signals(
            filter=filter, include=include
        )

        # Assert content of return
        for signal in response_data.result.data:
            self.assertIsInstance(signal, SignalSelectView)

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_filter_returning_nothing(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[2]
        filter = Filter(**test_case["args"]["filter"])
        include = test_case["args"]["include"]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_signals(
            filter=filter, include=["item"]
        )
        # Assert no data
        self.assertEqual(response_data.result.data, [])

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_all_inputs_returning_nothing(self, client_req_mock, get_token_mock):
        test_case = self.test_cases[3]
        args = test_case["args"]
        filter = Filter(**args["filter"])
        include = args["include"]
        skip = args["skip"]
        limit = args["limit"]
        integration = args["integration"]
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: test_case["response"]

        response_data = self.client.select_signals(
            filter=filter,
            include=include,
            skip=skip,
            limit=limit,
            integration=integration,
        )
        # Assert no data
        self.assertEqual(response_data.result.data, [])


if __name__ == "__main__":
    unittest.main()
