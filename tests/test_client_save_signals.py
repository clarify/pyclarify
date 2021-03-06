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
from datetime import datetime, timedelta
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

        with open("./tests/data/mock-save-signals.json") as f:
            self.mock_data = json.load(f)

        self.times = [
            (datetime.now() - timedelta(seconds=10)).astimezone().isoformat(),
            datetime.now().astimezone().isoformat(),
        ]

        self.values = [0.6, 1.0]

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_send_request_1(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.mock_data["mock_response_1"]

        signal_id = "c5vv12btaf7d0qbk0l0g"
        data = DataFrame(values={signal_id: self.values}, times=self.times)
        result = self.client.insert(data)

        signal_meta_data = SignalInfo(
            name=signal_id,
            description="test description",
            labels={"test_label_py": ["completed mo"]},
            gapDetection="PT5M",
        )
        result = self.client.save_signals(
            params={"inputs": {signal_id: signal_meta_data}, "createOnly": True}
        )
        if result.error is not None:
            self.assertIn(result.error.code, self.error_list)
        else:
            self.assertIn(signal_id, result.result.signalsByInput)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_send_request_2(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.mock_data["mock_response_2"]

        signal_id = "c5vv12btaf7d0qbk0l0e"
        data = DataFrame(values={signal_id: self.values}, times=self.times)
        result = self.client.insert(data)

        signal_meta_data = SignalInfo(
            name=signal_id,
            description="test description",
            labels={
                "test_label_py": ["completed no", "and one more"],
                "thisonetoo": ["house"],
            },
            gapDetection="PT3M",
        )
        result = self.client.save_signals(
            params={"inputs": {signal_id: signal_meta_data}, "createOnly": True}
        )

        if result.error is not None:
            self.assertIn(result.error.code, self.error_list)
        else:
            self.assertIn(signal_id, result.result.signalsByInput)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_send_request_3(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.mock_data["mock_response_3"]

        signal_id = "c5vv12btaf7d0qbk0l0g"
        data = DataFrame(values={signal_id: self.values}, times=self.times)
        result = self.client.insert(data)

        signal_meta_data = SignalInfo(
            name=signal_id,
            description="test description",
            labels={
                "test_label_py": ["completed yes", "and now updated"],
                "location": ["house"],
            },
        )
        result = self.client.save_signals(
            params={"inputs": {signal_id: signal_meta_data}, "createOnly": True}
        )

        if result.error is not None:
            self.assertIn(result.error.code, self.error_list)
        else:
            self.assertIn(signal_id, result.result.signalsByInput)


if __name__ == "__main__":
    unittest.main()
