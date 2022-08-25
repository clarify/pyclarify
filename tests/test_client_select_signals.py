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

from pyclarify.views.items import ItemSelectView

sys.path.insert(1, "src/")
from pyclarify import Client
from pyclarify.views.signals import SignalSelectView


class TestClarifyClientSelectSignals(unittest.TestCase):
    def setUp(self):
        self.client = Client("./tests/mock_data/mock-clarify-credentials.json")

        with open("./tests/mock_data/signals.json") as f:
            self.mock_data = json.load(f)
        test_data = self.mock_data["select_signals"]
        self.args = test_data["args"]
        self.response = test_data["response"]
        with open("./tests/mock_data/mock-client-common.json") as f:
            self.mock_data = json.load(f)
        self.mock_access_token = self.mock_data["mock_access_token"]

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_no_arguments(self, client_req_mock, get_token_mock):
        return_value = self.response
        return_value["result"]["included"] = None
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: return_value

        response_data = self.client.select_signals()

        for signal in response_data.result.data:
            self.assertIsInstance(signal, SignalSelectView)


    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_all_arguments(self, client_req_mock, get_token_mock):
        return_value = self.response
        return_value["result"]["included"] = None
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: return_value

        response_data = self.client.select_signals(**self.args)

        for signal in response_data.result.data:
            self.assertIsInstance(signal, SignalSelectView)

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_all_arguments_with_included(self, client_req_mock, get_token_mock):
        return_value = self.response
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: return_value

        response_data = self.client.select_signals(**self.args)

        for signal in response_data.result.data:
            self.assertIsInstance(signal, SignalSelectView)

        for x in response_data.result.included.items:
            self.assertIsInstance(x, ItemSelectView)

if __name__ == "__main__":
    unittest.main()
