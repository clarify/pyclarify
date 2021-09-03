import sys
import unittest
import json
from datetime import datetime, timedelta
from unittest.mock import patch

# Standard library imports...


sys.path.insert(1, "src/")
from pyclarify.interface import ServiceInterface, ClarifyInterface
import pyclarify.interface as interface

# using DASH cryptocurrency RPC endpoints as test API
# (https://dashplatform.readme.io/docs/reference-dapi-endpoints-json-rpc-endpoints)
URL = "http://seed-1.testnet.networks.dash.org:3000/"
# Valid method and parameters for said endpoint
METHOD = "getBlockHash"
PARAMS = {"height": 1}


class TestBase(unittest.TestCase):
    def setUp(self):
        self.interface = ServiceInterface(base_url=URL)

    def test_update_header(self):
        """
        Test for updating request headers of interface
        """
        content_type_headers = {"content-type": "application/json"}
        # assert initialisation
        self.assertEqual(self.interface.headers, content_type_headers)

        # assert direct overwrite
        self.interface.headers = {}
        self.assertEqual(self.interface.headers, {})

        # assert update_header method working
        self.interface.update_headers(content_type_headers)
        self.assertEqual(self.interface.headers, content_type_headers)

        # assert update_header method working with existing headers
        self.interface.update_headers(content_type_headers)
        self.assertEqual(self.interface.headers, content_type_headers)

        # assert update_header method working with new headers
        content_type_headers = {"X-API-Version": "1.0"}
        self.interface.update_headers(content_type_headers)

        self.assertEqual(
            self.interface.headers,
            {"content-type": "application/json", "X-API-Version": "1.0"},
        )

    def test_create_payload(self):
        VALID_RPC_PAYLOAD = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "getBlockHash",
                "id": 1,
                "params": {"height": 1},
            }
        )

        payload = self.interface.create_payload(METHOD, PARAMS)

        # assert correct creation
        self.assertEqual(payload, VALID_RPC_PAYLOAD)

        # assert incrementation of id
        payload_1 = json.loads(self.interface.create_payload(METHOD, PARAMS))
        self.assertEqual(payload_1["id"], 2)

    def test_send_request(self):
        payload = self.interface.create_payload(METHOD, PARAMS)
        response = self.interface.send(payload)
        payload = json.loads(payload)

        # assert valid response type
        self.assertIsInstance(response, dict)

        # assert is JSONRPC
        self.assertEqual(response["jsonrpc"], "2.0")

        # assert is correct id
        self.assertEqual(response["id"], payload["id"])
    
    def test_authentication(self):
        read = self.interface.authenticate("./tests/test-clarify-credentials.json")
        self.assertTrue(read)


class TestClarifyInterface(unittest.TestCase):
    def setUp(self):
        self.interface = ClarifyInterface()
        self.error_list = [
            "-32000",
            "-32001",
            "-32002",
            "-32003",
            "-32009",
            "-32015",
            "-32600",
            "-32601",
            "-32602",
            "-32603",
            "-32700",
        ]
        signals_by_input_1 = {"test_123_id": {"id": "test_123_id", "created": True}}
        self.mock_response_insert_1 = {
            "jsonrpc": "2.0",
            "id": "1",
            "result": {"signalsByInput": signals_by_input_1},
            "error": None,
        }

        signals_by_input_2 = {
            "test_1234_id__a": {"id": "test_1234_id__a", "created": False}
        }
        self.mock_response_insert_2 = {
            "jsonrpc": "2.0",
            "id": "1",
            "result": {"signalsByInput": signals_by_input_2},
            "error": None,
        }
        self.mock_token = "token1234567890"
        self.interface.authenticate("./tests/test-clarify-credentials.json")
    
    @patch("pyclarify.interface.ServiceInterface.get_token")
    @patch("pyclarify.interface.requests.post")
    def test_send_request(self, interface_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_token
        interface_req_mock.return_value.ok = True
        interface_req_mock.return_value.json = lambda: self.mock_response_insert_1
        integration = "c4ivn4rsbu84313ljdgg"
        times = [
            (datetime.now() - timedelta(seconds=10)).astimezone().isoformat(),
            datetime.now().astimezone().isoformat(),
        ]
        values = [0.6, 1.0]
        signal_id = "test_123_id"
        result = self.interface.add_data_single_signal(
            integration=integration, input_id=signal_id, times=times, values=values
        )
        if result.error is not None:
            self.assertIn(result.error.code, self.error_list)
        else:
            self.assertIn(signal_id, result.result.signalsByInput)

    @patch("pyclarify.interface.ServiceInterface.get_token")
    @patch("pyclarify.interface.requests.request")
    def test_send_request_2(self, interface_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_token
        interface_req_mock.return_value.ok = True
        interface_req_mock.return_value.json = lambda: self.mock_response_insert_2
        integration = "a12vn4rsbu84313ljdgg"
        times = [
            (datetime.now() - timedelta(seconds=10)).astimezone().isoformat(),
            datetime.now().astimezone().isoformat(),
        ]
        values = [0.6, 6.7]
        signal_id = "test_1234_id__a"
        result = self.interface.add_data_single_signal(
            integration=integration, input_id=signal_id, times=times, values=values
        )
        if result.error is not None:
            self.assertIn(result.error.code, self.error_list)
        else:
            self.assertIn(signal_id, result.result.signalsByInput)


if __name__ == "__main__":
    unittest.main()
