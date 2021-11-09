import sys
import unittest
import json
from datetime import datetime, timedelta
from unittest.mock import patch
import requests
from http import HTTPStatus

# Standard library imports...


sys.path.insert(1, "src/")
from pyclarify import APIClient, SignalInfo, DataFrame
from pyclarify.models.auth import ClarifyCredential, OAuthRequestBody, OAuthResponse
import pyclarify

signal_id = "test_publish_signal"
client = APIClient("./tests/clarify-credentials-8.json")


# item_meta_data = SignalInfo(
#     name="This is my new signal",
#     description="I created this signal through the PyClarify SDK!",
#     labels={
#         "Test_signal_version": ["3"],
#         "SDK_version": ["0.2.0"]
#     },
#     gapDetection="PT5M",
# )

# response = client.save_signals(
#     inputs={"test_signal_3" : item_meta_data},
#     created_only=False #False = create new signal, True = update existing signal
# )
# print(response)
# test_signal_id_1 = "c64j2vfqfsj0hurrtjdg"
# test_signal_id_2 = "c64j35nqfsj0hurrtje0"
# test_signal_id_3 = "c64j7pnqfsj0hurrtjfg"

# item_meta_data_1 = SignalInfo(
#     name="Item numero tres",
#     description="I published this item through the PyClarify SDK!",
#     labels={
#         "Published_automatically": ["True"],
#         "SDK_version": ["0.2.0"]
#     },
#     gapDetection="PT5M",
# )

# item_meta_data_2 = SignalInfo(
#     name="Item numero quatro",
#     description="I published this item through the PyClarify SDK!",
#     labels={
#         "Published_automatically": ["True"],
#         "SDK_version": ["0.2.0"]
#     },
#     gapDetection="PT5M",
# )


# response = client.publish_signals(signals={test_signal_id_3: item_meta_data_1, test_signal_id_2: item_meta_data_2}, created_only=False)
# print(response)


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

        item_meta_data = SignalInfo(
            **self.mock_data["request"]
        )
        result = self.client.publish_signals(
            signals={"id_does_not_exist": item_meta_data}, created_only=True
        )

        self.assertEqual(result.result.itemsBySignal, {})
    
    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_send_publish_one_signal(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.mock_data["publish_one_response"]

        item_meta_data = SignalInfo(
            **self.mock_data["request"]
        )
        result = self.client.publish_signals(
            signals={"some_valid_id": item_meta_data}, created_only=True
        )
        self.assertTrue(result.result.itemsBySignal["some_valid_id"].created)
        self.assertFalse(result.result.itemsBySignal["some_valid_id"].updated)

    
    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_send_publish_two_signals(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.mock_data["publish_two_response"]

        item_meta_data = SignalInfo(
            **self.mock_data["request"]
        )
        result = self.client.publish_signals(
            signals={"some_valid_id_1": item_meta_data, "some_valid_id_2": item_meta_data}, created_only=True
        )
        self.assertTrue(result.result.itemsBySignal["some_valid_id_1"].created)
        self.assertTrue(result.result.itemsBySignal["some_valid_id_2"].created)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_send_update_one_signal(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.mock_data["update_one_response"]

        item_meta_data = SignalInfo(
            **self.mock_data["request"]
        )
        result = self.client.publish_signals(
            signals={"some_valid_id": item_meta_data}, created_only=True
        )

        self.assertFalse(result.result.itemsBySignal["some_valid_id"].created)
        self.assertTrue(result.result.itemsBySignal["some_valid_id"].updated)

if __name__ == "__main__":
    unittest.main()
