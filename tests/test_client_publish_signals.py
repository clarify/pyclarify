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
from pyclarify import APIClient, SignalInfo, DataFrame
from pyclarify.models.auth import ClarifyCredential, OAuthRequestBody, OAuthResponse
import pyclarify


class TestClarifySaveClient(unittest.TestCase):
    def setUp(self):
        self.client = APIClient("./tests/data/mock-clarify-credentials.json")

        with open("./tests/data/mock-client-common.json") as f:
            self.mock_data = json.load(f)
        self.mock_access_token = self.mock_data["mock_access_token"]

        with open("./tests/data/mock-publish-signals.json") as f:
            self.mock_data = json.load(f)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_send_nonexisting_signal_request(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.mock_data["empty_response"]

        item_meta_data = SignalInfo(**self.mock_data["request"])
        resource_not_exist = "c618j7mjkj1ss0rbfqfs"
        result = self.client.publish_signals(
            params={
                "itemsBySignal": {resource_not_exist: item_meta_data},
                "createOnly": True,
            }
        )

        self.assertEqual(result.result.itemsBySignal, {})

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_send_publish_one_signal(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.mock_data[
            "publish_one_response"
        ]

        item_meta_data = SignalInfo(**self.mock_data["request"])
        resource_not_exist = "c618j7mjkj1ss0rbfqfs"
        resource_does_exist = "c618rbfqfsj7mjkj0ss1"

        result = self.client.publish_signals(
            params={
                "itemsBySignal": {resource_does_exist: item_meta_data},
                "createOnly": True,
            }
        )
        self.assertTrue(result.result.itemsBySignal[resource_does_exist].created)
        self.assertFalse(result.result.itemsBySignal[resource_does_exist].updated)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_send_publish_two_signals(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.mock_data[
            "publish_two_response"
        ]

        item_meta_data = SignalInfo(**self.mock_data["request"])

        resource_does_exist_1 = "c618rbfqfsj7mjkj0ss1"
        resource_does_exist_2 = "c618rbfqfsj7mjkj0ss2"

        result = self.client.publish_signals(
            params={
                "itemsBySignal": {
                    resource_does_exist_1: item_meta_data,
                    resource_does_exist_2: item_meta_data,
                },
                "createOnly": True,
            }
        )
        self.assertTrue(result.result.itemsBySignal[resource_does_exist_1].created)
        self.assertTrue(result.result.itemsBySignal[resource_does_exist_2].created)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_send_update_one_signal(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.mock_data[
            "update_one_response"
        ]

        item_meta_data = SignalInfo(**self.mock_data["request"])

        resource_does_exist = "c618rbfqfsj7mjkj0ss1"

        result = self.client.publish_signals(
            params={
                "itemsBySignal": {resource_does_exist: item_meta_data},
                "createOnly": True,
            }
        )

        self.assertFalse(result.result.itemsBySignal[resource_does_exist].created)
        self.assertTrue(result.result.itemsBySignal[resource_does_exist].updated)


if __name__ == "__main__":
    unittest.main()
