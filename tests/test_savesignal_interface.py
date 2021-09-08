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
import pyclarify


class TestClarifySaveInterface(unittest.TestCase):
    def setUp(self):
        self.interface = ClarifyInterface()
<<<<<<< HEAD
        self.error_list = ["-32700", "-32600", "-32601", "-32602", "-32603",
                           "-32000", "-32001", "-32002", "-32003", "-32009", "-32015"]
        signals_by_input_1 = {"test_1234_id__a": {"id": "test_1234_id__a", "created": False}}
        self.mock_response_insert_1 = {"jsonrpc": "2.0", "id": "1", "result":
            {"signalsByInput": signals_by_input_1}, "error": None}

        signals_by_input_2 = {"test_1234_id__b": {"id": "test_1234_id__a", "created": False}}
        self.mock_response_insert_2 = {"jsonrpc": "2.0", "id": "1", "result":
            {"signalsByInput": signals_by_input_2}, "error": None}

    @patch('interface.requests.request')
=======
        self.error_list = [
            "-32700",
            "-32600",
            "-32601",
            "-32602",
            "-32603",
            "-32000",
            "-32001",
            "-32002",
            "-32003",
            "-32009",
            "-32015",
        ]
        signals_by_input_1 = {
            "test_1234_id__a": {"id": "test_1234_id__a", "created": False}
        }
        self.mock_response_insert_1 = {
            "jsonrpc": "2.0",
            "id": "1",
            "result": {"signalsByInput": signals_by_input_1},
            "error": None,
        }

        signals_by_input_2 = {
            "test_1234_id__b": {"id": "test_1234_id__a", "created": False}
        }
        self.mock_response_insert_2 = {
            "jsonrpc": "2.0",
            "id": "1",
            "result": {"signalsByInput": signals_by_input_2},
            "error": None,
        }
        self.mock_token = "token1234567890"

    @patch("pyclarify.interface.ServiceInterface.get_token")
    @patch("pyclarify.interface.requests.request")
<<<<<<< HEAD
>>>>>>> 4416be551733f3fd6096140ebe296f7740051ab8
    def test_send_request_2(self, mock_request):
        mock_request.return_value.ok = True
        mock_request.return_value.json = lambda: self.mock_response_insert_1
=======
    def test_send_request_2(self, interface_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_token
        interface_req_mock.return_value.ok = True
        interface_req_mock.return_value.json = lambda: self.mock_response_insert_1
>>>>>>> 7a45ab39cce227dbee2ecabb61103a1a42672986
        integration = "c4ivn4rsbu84313ljdgg"

<<<<<<< HEAD
        times = [(datetime.now() - timedelta(seconds=10)).astimezone().isoformat(),
                 datetime.now().astimezone().isoformat()]
        values = [0.6, 6.7]
        signal_id = "test_1234_id__a"
        result = self.interface.add_data_single_signal(integration=integration, input_id=signal_id,
                                                       times=times, values=values)

        signal_meta_data = Signal(name=signal_id, description="test description",
                                  labels={"test_label_py": ["completed mo"]})
        result = self.interface.add_metadata_signals(integration=integration, signal_metadata_list=[signal_meta_data],
                                                     created_only=True)
=======
        times = [
            (datetime.now() - timedelta(seconds=10)).astimezone().isoformat(),
            datetime.now().astimezone().isoformat(),
        ]
        values = [0.6, 6.7]
        signal_id = "test_1234_id__a"
        result = self.interface.add_data_single_signal(
            integration=integration, input_id=signal_id, times=times, values=values
        )

        signal_meta_data = Signal(
            name=signal_id,
            description="test description",
            labels={"test_label_py": ["completed mo"]},
        )
        result = self.interface.add_metadata_signals(
            integration=integration,
            signal_metadata_list=[signal_meta_data],
            created_only=True,
        )
>>>>>>> 4416be551733f3fd6096140ebe296f7740051ab8
        if result.error is not None:
            self.assertIn(result.error.code, self.error_list)
        else:
            self.assertIn(signal_id, result.result.signalsByInput)

<<<<<<< HEAD
<<<<<<< HEAD
    @patch('interface.requests.request')
=======
    @patch("pyclarify.interface.requests.request")
>>>>>>> 4416be551733f3fd6096140ebe296f7740051ab8
    def test_send_request_3(self, mock_request):
        mock_request.return_value.ok = True
        mock_request.return_value.json = lambda: self.mock_response_insert_2
=======
    @patch("pyclarify.interface.ServiceInterface.get_token")
    @patch("pyclarify.interface.requests.request")
    def test_send_request_3(self, interface_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_token
        interface_req_mock.return_value.ok = True
        interface_req_mock.return_value.json = lambda: self.mock_response_insert_2
>>>>>>> 7a45ab39cce227dbee2ecabb61103a1a42672986
        integration = "c4ivn4rsbu84313ljdgg"

<<<<<<< HEAD
        times = [(datetime.now() - timedelta(seconds=10)).astimezone().isoformat(),
                 datetime.now().astimezone().isoformat()]
        values = [0.6, 6.7]
        signal_id = "test_1234_id__b"
        result = self.interface.add_data_single_signal(integration=integration, input_id=signal_id,
                                                       times=times, values=values)

        signal_meta_data = Signal(name=signal_id, description="test description",
                                  labels={"test_label_py": ["completed no", "and one more"], "thisonetoo": ["house"]})
        result = self.interface.add_metadata_signals(integration=integration, signal_metadata_list=[signal_meta_data],
                                                     created_only=True)
=======
        times = [
            (datetime.now() - timedelta(seconds=10)).astimezone().isoformat(),
            datetime.now().astimezone().isoformat(),
        ]
        values = [0.6, 6.7]
        signal_id = "test_1234_id__b"
        result = self.interface.add_data_single_signal(
            integration=integration, input_id=signal_id, times=times, values=values
        )

        signal_meta_data = Signal(
            name=signal_id,
            description="test description",
            labels={
                "test_label_py": ["completed no", "and one more"],
                "thisonetoo": ["house"],
            },
        )
        result = self.interface.add_metadata_signals(
            integration=integration,
            signal_metadata_list=[signal_meta_data],
            created_only=True,
        )
>>>>>>> 4416be551733f3fd6096140ebe296f7740051ab8

        if result.error is not None:
            self.assertIn(result.error.code, self.error_list)
        else:
            self.assertIn(signal_id, result.result.signalsByInput)


<<<<<<< HEAD
if __name__ == '__main__':
=======
if __name__ == "__main__":
>>>>>>> 4416be551733f3fd6096140ebe296f7740051ab8
    unittest.main()
