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


class TestClarifyClientSaveSignals(unittest.TestCase):
    def setUp(self):
        self.client = ClarifyClient("./tests/data/mock-clarify-credentials.json")

        with open("./tests/data/mock-clarify-client-save-signals.json") as f:
            self.mock_data = json.load(f)
        self.test_cases = self.mock_data["test_cases"]
        self.signals = self.test_cases[1]["dummy-signals"]

        with open("./tests/data/mock-client-common.json") as f:
            self.mock_data = json.load(f)
        self.mock_access_token = self.mock_data["mock_access_token"]

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_save_no_signal(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.test_cases[0]["response"]

        response_data = self.client.save_signals(input_ids=[], signals=[])
        for x in response_data.result.signalsByInput:
            self.assertEquals(x, {})

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_save_one_signal(self, client_req_mock, get_token_mock):
        input_ids, signals = self.signals.items()
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.test_cases[1]["response"]

        response_data = self.client.save_signals(input_ids=input_ids[:1], signals=signals[:1])
        print(response_data)
        for x in response_data.result.signalsByInput:
            self.assertEquals(x, input_ids[0])

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_save_multiple_signals(self, client_req_mock, get_token_mock):
        print(self.signals.items())
        input_ids, signals = self.signals.items()
        print(input_ids)
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.test_cases[1]["response"]

        response_data = self.client.save_signals(input_ids=input_ids, signals=signals)
        print(response_data)
        for i, x in enumerate(response_data.result.signalsByInput):
            self.assertEquals(x, input_ids[i])


    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_save_without_input_ids(self, client_req_mock, get_token_mock):
        pass
    
    
    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_save_without_signals(self, client_req_mock, get_token_mock):
        pass
    
    
    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_save_with_too_many_input_ids(self, client_req_mock, get_token_mock):
        pass


    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_save_with_too_many_signals(self, client_req_mock, get_token_mock):
        pass


if __name__ == "__main__":
    unittest.main()
