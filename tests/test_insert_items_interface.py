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
        print(response_data)

        self.assertIn("c4medah70nh34fs577v0", response_data.result.items.keys())
        for x in response_data.result.items:
            self.assertIsInstance(response_data.result.items[x], Signal)


if __name__ == "__main__":
    unittest.main()
