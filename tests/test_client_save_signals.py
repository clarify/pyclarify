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


class TestClarifyClientSaveSignals(unittest.TestCase):
    def setUp(self):
        self.client = Client("./tests/mock_data/mock-clarify-credentials.json")

        with open("./tests/mock_data/signals.json") as f:
            self.mock_data = json.load(f)
        self.test_cases = self.mock_data["save_signals"]["test_cases"]
        dummy_signals = self.test_cases[1]["dummy-signals"]
        self.input_ids = list(dummy_signals.keys())
        self.signals = list(dummy_signals.values())

        with open("./tests/mock_data/mock-client-common.json") as f:
            self.mock_data = json.load(f)
        self.mock_access_token = self.mock_data["mock_access_token"]

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_save_no_signal(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.test_cases[0]["response"]

        response_data = self.client.save_signals(input_ids=[], signals=[])
        for x in response_data.result.signalsByInput:
            self.assertEqual(x, {})

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_save_one_signal(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.test_cases[1]["response"]

        response_data = self.client.save_signals(
            input_ids=self.input_ids[:1], signals=self.signals[:1]
        )
        for x in response_data.result.signalsByInput:
            self.assertEqual(x, self.input_ids[0])
            break

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_save_multiple_signals(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.test_cases[1]["response"]

        response_data = self.client.save_signals(
            input_ids=self.input_ids, signals=self.signals
        )
        for i, x in enumerate(response_data.result.signalsByInput):
            self.assertEqual(x, self.input_ids[i])

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_save_without_input_ids(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.test_cases[0]["response"]

        response_data = self.client.save_signals(input_ids=[], signals=self.signals)
        for x in response_data.result.signalsByInput:
            self.assertEqual(x, {})

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_save_without_signals(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.test_cases[0]["response"]

        response_data = self.client.save_signals(input_ids=self.input_ids, signals=[])
        for x in response_data.result.signalsByInput:
            self.assertEqual(x, {})

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_save_with_too_many_input_ids(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.test_cases[1]["response"]

        response_data = self.client.save_signals(
            input_ids=self.input_ids * 2, signals=self.signals
        )
        for x in response_data.result.signalsByInput:
            self.assertEqual(x, self.input_ids[0])
            break

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_save_with_too_many_signals(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.test_cases[2]["response"]

        response_data = self.client.save_signals(
            input_ids=self.input_ids, signals=self.signals * 2
        )
        for x in response_data.result.signalsByInput:
            self.assertEqual(x, self.input_ids[0])
            break

        self.assertFalse(response_data.result.signalsByInput[x].created)
        self.assertFalse(response_data.result.signalsByInput[x].updated)


if __name__ == "__main__":
    unittest.main()
