import sys
import unittest
from datetime import datetime, timedelta

sys.path.insert(1, "src/pyclarify")
from interface import ServiceInterface, ClarifyInterface
from dateutil import parser

parser = parser.isoparser("T")

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
        VALID_RPC_PAYLOAD = {
            "jsonrpc": "2.0",
            "method": "getBlockHash",
            "id": 0,
            "params": {"height": 1},
        }

        payload = self.interface.create_payload(METHOD, PARAMS)

        # assert correct creation
        self.assertEqual(payload, VALID_RPC_PAYLOAD)

        # assert incrementation of id
        payload_1 = self.interface.create_payload(METHOD, PARAMS)
        self.assertEqual(payload_1["id"], 1)

    def test_send_request(self):
        payload = self.interface.create_payload(METHOD, PARAMS)
        response = self.interface.send(payload)

        # assert valid response type
        self.assertIsInstance(response, dict)

        # assert is JSONRPC
        # self.assertEqual(response["jsonrpc"], "2.0")

        # assert is correct id
        # self.assertEqual(response["id"], payload["id"])


class TestClarifyInterface(unittest.TestCase):
    def setUp(self):
        self.interface = ClarifyInterface()

    def test_send_request(self):
        integration = "c4ivn4rsbu84313ljdgg"
        times = [(datetime.now() - timedelta(seconds=10)).astimezone().isoformat(),
                 datetime.now().astimezone().isoformat()]
        values = [0.6, 1.0]
        signal_id = "test_123_id"
        result = self.interface.add_data_single_signal(integration=integration, input_id=signal_id,
                                                       times=times, values=values)
        print(result)
        self.assertEqual(result.id, str(self.interface.current_id + 1))

    def test_send_request_2(self):
        integration = "c4ivn4rsbu84313ljdgg"
        times = [(datetime.now() - timedelta(seconds=10)).astimezone().isoformat(),
                 datetime.now().astimezone().isoformat()]
        values = [0.6, 6.7]
        signal_id = "test_1234_id"
        result = self.interface.add_data_single_signal(integration=integration, input_id=signal_id,
                                                       times=times, values=values)
        print(result)
        self.assertEqual(result.id, str(self.interface.current_id + 1))


if __name__ == "__main__":
    unittest.main()
