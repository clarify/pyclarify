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

sys.path.insert(1, "src/")
from pyclarify.client import Client
from pyclarify import DataFrame


class TestClarifyClientInsert(unittest.TestCase):
    def setUp(self):
        self.client = Client("./tests/mock_data/mock-clarify-credentials.json")

        with open("./tests/mock_data/mock-client-common.json") as f:
            self.mock_data = json.load(f)

        self.mock_access_token = self.mock_data["mock_access_token"]

        with open("./tests/mock_data/dataframe.json") as f:
            mock_data = json.load(f)
            self.insert_response = mock_data["insert"]["response"]
            self.insert_args = mock_data["insert"]["args"]

        self.times = [
            (datetime.now() - timedelta(seconds=10)).astimezone().isoformat(),
            datetime.now().astimezone().isoformat(),
        ]

        self.values = [0.6, 1.0]

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_send_request(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.insert_response

        signal_id = "c5vv12btaf7d0qbk0l0e"
        data = DataFrame(values={signal_id: self.values}, times=self.times)

        result = self.client.insert(data)
        self.assertIn(signal_id, result.result.signalsByInput)


if __name__ == "__main__":
    unittest.main()
