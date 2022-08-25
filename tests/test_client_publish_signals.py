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


class TestClarifyClientPublishSignals(unittest.TestCase):
    def setUp(self):
        self.client = Client("./tests/mock_data/mock-clarify-credentials.json")

        with open("./tests/mock_data/items.json") as f:
            mock_data = json.load(f)
            self.test_cases = mock_data["publish_signals"]["test_cases"]
        dummy_items = self.test_cases[1]["dummy-items"]
        self.signal_ids = list(dummy_items.keys())
        self.items = list(dummy_items.values())

        with open("./tests/mock_data/mock-client-common.json") as f:
            self.mock_data = json.load(f)
        self.mock_access_token = self.mock_data["mock_access_token"]

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_publish_no_item(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.test_cases[0]["response"]

        response_data = self.client.publish_signals(signal_ids=[], items=[])
        for x in response_data.result.itemsBySignal:
            self.assertEqual(x, {})

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_publish_one_item(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.test_cases[1]["response"]

        response_data = self.client.publish_signals(
            signal_ids=self.signal_ids[:1], items=self.items[:1]
        )
        for x in response_data.result.itemsBySignal:
            self.assertEqual(x, self.signal_ids[0])
            break

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_publish_multiple_signals(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.test_cases[1]["response"]

        response_data = self.client.publish_signals(
            signal_ids=self.signal_ids, items=self.items
        )
        for i, x in enumerate(response_data.result.itemsBySignal):
            self.assertEqual(x, self.signal_ids[i])

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_publish_without_signal_ids(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.test_cases[0]["response"]

        response_data = self.client.publish_signals(signal_ids=[], items=self.items)
        for x in response_data.result.itemsBySignal:
            self.assertEqual(x, {})

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_publish_without_items(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.test_cases[0]["response"]

        response_data = self.client.publish_signals(
            signal_ids=self.signal_ids, items=[]
        )
        for x in response_data.result.itemsBySignal:
            self.assertEqual(x, {})

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_publish_with_too_many_signal_ids(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.test_cases[1]["response"]

        response_data = self.client.publish_signals(
            signal_ids=self.signal_ids * 2, items=self.items
        )
        for x in response_data.result.itemsBySignal:
            self.assertEqual(x, self.signal_ids[0])
            break

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_publish_with_too_many_items(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.test_cases[2]["response"]

        response_data = self.client.publish_signals(
            signal_ids=self.signal_ids, items=self.items * 2
        )
        for x in response_data.result.itemsBySignal:
            self.assertEqual(x, self.signal_ids[0])
            break

        self.assertFalse(response_data.result.itemsBySignal[x].created)
        self.assertFalse(response_data.result.itemsBySignal[x].updated)


if __name__ == "__main__":
    unittest.main()
