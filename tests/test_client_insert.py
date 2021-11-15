import sys
import unittest
import json
from datetime import datetime, timedelta
from unittest.mock import patch

sys.path.insert(1, "src/")
from pyclarify.client import APIClient
from pyclarify import DataFrame


class TestAPIClient(unittest.TestCase):
    def setUp(self):
        self.client = APIClient("./tests/data/mock-clarify-credentials.json")

        with open("./tests/data/mock-client-common.json") as f:
            self.mock_data = json.load(f)

        self.mock_access_token = self.mock_data["mock_access_token"]

        with open("./tests/data/mock-insert.json") as f:
            self.mock_data = json.load(f)

        self.times = [
            (datetime.now() - timedelta(seconds=10)).astimezone().isoformat(),
            datetime.now().astimezone().isoformat(),
        ]

        self.values = [0.6, 1.0]

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_send_request(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.mock_data["mock_response_1"]

        signal_id = "c5vv12btaf7d0qbk0l0g"
        data = DataFrame(values={signal_id: self.values}, times=self.times)

        result = self.client.insert(data)
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
        self.assertIn(signal_id, result.result.signalsByInput)


if __name__ == "__main__":
    unittest.main()
