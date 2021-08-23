import sys
import unittest
sys.path.insert(1, 'src/pyclarify')
from interface import ServiceInterface

# using DASH cryptocurrency RPC endpoints as test API 
# (https://dashplatform.readme.io/docs/reference-dapi-endpoints-json-rpc-endpoints)
URL = "http://seed-1.testnet.networks.dash.org:3000/"
# Valid method and parameters for said endpoint
METHOD = "getBlockHash"
PARAMS = {
    "height": 1
    }
class TestBase(unittest.TestCase):
    def setUp(self):
        self.interface = ServiceInterface(URL)

    def test_update_header(self):
        """
        Test for updating request headers of interface
        """
        content_type_headers = { "content-type": "application/json" }
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
        content_type_headers = { "X-API-Version": "1.0" }
        self.interface.update_headers(content_type_headers)

        self.assertEqual(self.interface.headers, 
            { 
                "content-type": "application/json",
                "X-API-Version": "1.0" 
            }
        )
        
    def test_create_payload(self):
        VALID_RPC_PAYLOAD = {
            "jsonrpc": "2.0",
            "method": "getBlockHash",
            "id": 0,
            "params": {
                "height": 1
            }
        }

        payload = self.interface.create_payload(METHOD, PARAMS)
        
        # assert correct creation
        self.assertEqual(payload, VALID_RPC_PAYLOAD)

        # assert incrementation of id
        payload_1 = self.interface.create_payload(METHOD, PARAMS)
        self.assertEqual(payload_1["id"], 1)
    
    def test_send_request(self):
        payload = self.interface.create_payload(METHOD, PARAMS)
        response = self.interface.send_request(payload)

        # assert valid response type
        self.assertIsInstance(response, dict)

        # assert is JSONRPC
        self.assertEqual(response["jsonrpc"], "2.0")

        # assert is correct id
        self.assertEqual(response["id"], payload["id"])



if __name__ == '__main__':
    unittest.main()