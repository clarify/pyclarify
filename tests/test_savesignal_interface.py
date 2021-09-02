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

    @patch("pyclarify.interface.requests.request")
    def test_send_request_2(self, mock_request):
        mock_request.return_value.ok = True
        mock_request.return_value.json = lambda: self.mock_response_insert_1
        integration = "c4ivn4rsbu84313ljdgg"

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
        if result.error is not None:
            self.assertIn(result.error.code, self.error_list)
        else:
            self.assertIn(signal_id, result.result.signalsByInput)

    @patch("pyclarify.interface.requests.request")
    def test_send_request_3(self, mock_request):
        mock_request.return_value.ok = True
        mock_request.return_value.json = lambda: self.mock_response_insert_2
        integration = "c4ivn4rsbu84313ljdgg"

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

        if result.error is not None:
            self.assertIn(result.error.code, self.error_list)
        else:
            self.assertIn(signal_id, result.result.signalsByInput)


if __name__ == "__main__":
    unittest.main()