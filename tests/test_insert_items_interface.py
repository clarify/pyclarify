import sys
import unittest
import json
from datetime import datetime, timedelta
from unittest.mock import patch
import requests

# Standard library imports...


sys.path.insert(1, "src/")
from pyclarify import ClarifyInterface, Signal
from pyclarify.models.auth import ClarifyCredential, OAuthRequestBody, OAuthResponse
from pyclarify.models.requests import ItemSelect
from pyclarify.models.data import ClarifyDataFrame


class TestClarifySelectInterface(unittest.TestCase):
    def setUp(self):
        self.interface = ClarifyInterface("./tests/data/test-clarify-credentials.json")
        self.mock_token = "token1234567890"
        with open("./tests/data/mock_items_select.json") as f:
            self.test_cases = json.load(f)

    @patch("pyclarify.interface.ServiceInterface.get_token")
    @patch("pyclarify.interface.requests.post")
    def test_get_items_metadata(self, interface_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_token
        interface_req_mock.return_value.ok = True
        interface_req_mock.return_value.json = lambda: self.test_cases[0]["response"]

        params = ItemSelect(**self.test_cases[0]["args"])
        response_data = self.interface.select_items(params)

        self.assertIn("c4medah70nh34fs577v0", response_data.result.items.keys())
        for x in response_data.result.items:
            self.assertIsInstance(response_data.result.items[x], Signal)

    @patch("pyclarify.interface.ServiceInterface.get_token")
    @patch("pyclarify.interface.requests.post")
    def test_get_items_metadata_data_agg(self, interface_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_token
        interface_req_mock.return_value.ok = True
        interface_req_mock.return_value.json = lambda: self.test_cases[1]["response"]

        params = ItemSelect(**self.test_cases[1]["args"])
        response_data = self.interface.select_items(params)

        for x in response_data.result.items:
            self.assertIsInstance(response_data.result.items[x], Signal)
        self.assertIsInstance(response_data.result.data, ClarifyDataFrame)

        self.assertIn("count", response_data.result.data.series.keys())
        self.assertIn("sum", response_data.result.data.series.keys())
        self.assertIn("min", response_data.result.data.series.keys())
        self.assertIn("max", response_data.result.data.series.keys())

    @patch("pyclarify.interface.ServiceInterface.get_token")
    @patch("pyclarify.interface.requests.post")
    def test_get_items_data_only(self, interface_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_token
        interface_req_mock.return_value.ok = True
        interface_req_mock.return_value.json = lambda: self.test_cases[2]["response"]

        params = ItemSelect(**self.test_cases[2]["args"])
        response_data = self.interface.select_items(params)

        self.assertIsNone(response_data.result.items)
        self.assertIsInstance(response_data.result.data, ClarifyDataFrame)

    @patch("pyclarify.interface.ServiceInterface.get_token")
    @patch("pyclarify.interface.requests.post")
    def test_get_items_data_metadata_empty(self, interface_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_token
        interface_req_mock.return_value.ok = True
        interface_req_mock.return_value.json = lambda: self.test_cases[3]["response"]

        params = ItemSelect(**self.test_cases[3]["args"])
        response_data = self.interface.select_items(params)

        self.assertIsNone(response_data.result.items)
        self.assertIsNone(response_data.result.data)
        self.assertIsNone(response_data.error)


if __name__ == "__main__":
    unittest.main()
