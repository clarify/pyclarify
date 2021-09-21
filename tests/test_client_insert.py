import sys
import unittest
import json
from datetime import datetime, timedelta
from unittest.mock import patch
from http import HTTPStatus

sys.path.insert(1, "src/")
from pyclarify.client import SimpleClient, ApiClient
import pyclarify.client as client
from pyclarify import DataFrame, Signal


class TestApiClient(unittest.TestCase):
    def setUp(self):
        self.client = ApiClient("./tests/data/mock-clarify-credentials.json")

        with open("./tests/data/mock-client.json") as f:
            self.mock_data = json.load(f)

        self.error_list = self.mock_data["RPC_ERRORS"] + [
            str(e.value) for e in HTTPStatus
        ]
        self.mock_access_token = self.mock_data["mock_access_token"]
        self.times = [
            (datetime.now() - timedelta(seconds=10)).astimezone().isoformat(),
            datetime.now().astimezone().isoformat(),
        ]

        self.values = [0.6, 1.0]

    @patch("pyclarify.client.SimpleClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_send_request(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.mock_data["mock_response_1"]

        signal_id = "test_123_id"
        data = DataFrame(values={signal_id: self.values}, times=self.times)

        result = self.client.insert(data)
        if result.error is not None:
            self.assertIn(result.error.code, self.error_list)
        else:
            self.assertIn(signal_id, result.result.signalsByInput)

    @patch("pyclarify.client.SimpleClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_send_request_2(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.mock_data["mock_response_2"]

        signal_id = "test_1234_id__a"
        data = DataFrame(values={signal_id: self.values}, times=self.times)
        result = self.client.insert(data)
        if result.error is not None:
            self.assertIn(result.error.code, self.error_list)
        else:
            self.assertIn(signal_id, result.result.signalsByInput)


if __name__ == "__main__":
    unittest.main()