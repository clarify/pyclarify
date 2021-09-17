import sys
import unittest
import json

sys.path.insert(1, "src/")
from pyclarify.client import SimpleClient

# using DASH cryptocurrency RPC endpoints as test API
# (https://dashplatform.readme.io/docs/reference-dapi-endpoints-json-rpc-endpoints)
URL = "http://seed-1.testnet.networks.dash.org:3000/"
# Valid method and parameters for said endpoint
METHOD = "getBlockHash"
PARAMS = {"height": 1}


class TestSimpleClient(unittest.TestCase):
    def setUp(self):
        self.client = SimpleClient(base_url=URL)

    def test_update_header(self):
        """
        Test for updating request headers of client
        """
        content_type_headers = {"content-type": "application/json"}
        # assert initialisation
        self.assertEqual(self.client.headers, content_type_headers)

        # assert direct overwrite
        self.client.headers = {}
        self.assertEqual(self.client.headers, {})

        # assert update_header method working
        self.client.update_headers(content_type_headers)
        self.assertEqual(self.client.headers, content_type_headers)

        # assert update_header method working with existing headers
        self.client.update_headers(content_type_headers)
        self.assertEqual(self.client.headers, content_type_headers)

        # assert update_header method working with new headers
        content_type_headers = {"X-API-Version": "1.0"}
        self.client.update_headers(content_type_headers)

        self.assertEqual(
            self.client.headers,
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

        payload = self.client.create_payload(METHOD, PARAMS)

        # assert correct creation
        self.assertEqual(payload, VALID_RPC_PAYLOAD)

        # assert incrementation of id
        payload_1 = json.loads(self.client.create_payload(METHOD, PARAMS))
        self.assertEqual(payload_1["id"], 2)

    def test_send_request(self):
        payload = self.client.create_payload(METHOD, PARAMS)
        response = self.client.send(payload)
        payload = json.loads(payload)

        # assert valid response type
        self.assertIsInstance(response, dict)

        # assert is JSONRPC
        self.assertEqual(response["jsonrpc"], "2.0")

        # assert is correct id
        self.assertEqual(response["id"], payload["id"])

    def test_authentication(self):
        read = self.client.authenticate("./tests/data/test-clarify-credentials.json")
        self.assertTrue(read)


if __name__ == "__main__":
    unittest.main()
