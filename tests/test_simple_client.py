import sys
import unittest
import json

sys.path.insert(1, "src/")
from pyclarify.client import SimpleClient



class TestSimpleClient(unittest.TestCase):
    def setUp(self):
        with open("./tests/data/mock-simple-client.json") as f:
            self.mock_data = json.load(f)
        
        self.client = SimpleClient(base_url=self.mock_data["mock_url"])
        self.content_type_headers = {"content-type": "application/json"}

    def test_update_header(self):
        """
        Test for updating request headers of client
        """
        # assert initialisation
        self.assertEqual(self.client.headers, self.content_type_headers)

        # assert direct overwrite
        self.client.headers = {}
        self.assertEqual(self.client.headers, {})

        # assert update_header method working
        self.client.update_headers(self.content_type_headers)
        self.assertEqual(self.client.headers, self.content_type_headers)

        # assert update_header method working with existing headers
        self.client.update_headers(self.content_type_headers)
        self.assertEqual(self.client.headers, self.content_type_headers)

        # assert update_header method working with new headers
        self.client.update_headers({"X-API-Version": "1.0"})

        self.assertEqual(
            self.client.headers,
            {
                "content-type": "application/json", 
                "X-API-Version": "1.0"
            },
        )

    def test_create_payload(self):
        VALID_RPC_PAYLOAD = json.dumps(self.mock_data["mock_RPC_payload"])

        payload = self.client.create_payload(self.mock_data["mock_method"], self.mock_data["mock_params"])

        # assert correct creation
        self.assertEqual(payload, VALID_RPC_PAYLOAD)

        # assert incrementation of id
        payload_2 = self.client.create_payload(self.mock_data["mock_method"], self.mock_data["mock_params"])
        payload_2 = json.loads(payload_2)
        self.assertEqual(payload_2["id"], 2)

    def test_send_request(self):
        payload = self.client.create_payload(self.mock_data["mock_method"], self.mock_data["mock_params"])
        response = self.client.send(payload)
        payload = json.loads(payload)

        # assert valid response type
        self.assertIsInstance(response, dict)

        # assert is JSONRPC
        self.assertEqual(response["jsonrpc"], "2.0")

        # assert is correct id
        self.assertEqual(response["id"], payload["id"])

    def test_authentication(self):
        read = self.client.authenticate("./tests/data/mock-clarify-credentials.json")
        self.assertTrue(read)


if __name__ == "__main__":
    unittest.main()
