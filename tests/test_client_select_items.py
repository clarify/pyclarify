import sys
import unittest
import json
from unittest.mock import patch

# Standard library imports...

sys.path.insert(1, "src/")
from pyclarify import APIClient, SignalInfo, DataFrame
from pyclarify.models.requests import ItemSelect


class TestClarifySelectItemsClient(unittest.TestCase):
    def setUp(self):
        self.client = APIClient("./tests/data/mock-clarify-credentials.json")

        with open("./tests/data/mock-items-select.json") as f:
            self.mock_data = json.load(f)
        self.test_cases = self.mock_data["test_cases"]

        with open("./tests/data/mock-client-common.json") as f:
            self.mock_data = json.load(f)
        self.mock_access_token = self.mock_data["mock_access_token"]

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_all_item_metadata(self, client_req_mock, get_token_mock):

        get_token_mock.return_value = self.mock_access_token

        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.test_cases[0]["response"]

        params = ItemSelect(**self.test_cases[0]["args"])
        response_data = self.client.select_items(params)

        for x in response_data.result.items:
            self.assertIsInstance(response_data.result.items[x], SignalInfo)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_items_metadata_data_agg(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token

        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.test_cases[1]["response"]

        params = ItemSelect(**self.test_cases[1]["args"])
        response_data = self.client.select_items(params)

        for x in response_data.result.items:
            self.assertIsInstance(response_data.result.items[x], SignalInfo)
        self.assertIsInstance(response_data.result.data, DataFrame)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_items_data_only(self, client_req_mock, get_token_mock):

        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.test_cases[2]["response"]

        params = ItemSelect(**self.test_cases[2]["args"])
        response_data = self.client.select_items(params)

        self.assertIsNone(response_data.result.items)
        self.assertIsInstance(response_data.result.data, DataFrame)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_items_data_metadata_empty(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.test_cases[3]["response"]

        params = ItemSelect(**self.test_cases[3]["args"])
        response_data = self.client.select_items(params)

        self.assertIsNone(response_data.result.items)
        self.assertIsNone(response_data.result.data)
        self.assertIsNone(response_data.error)


if __name__ == "__main__":
    unittest.main()
