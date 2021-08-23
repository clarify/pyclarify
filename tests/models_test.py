import unittest
import sys

sys.path.append("../src")
import pyclarify.models as models


class TestJSONRPC(unittest.TestCase):
    def test_creation(self):
        empty_request = models.requests.JsonRPCRequest()
        self.assertEqual( empty_request.json(), '{"jsonrpc": "2.0", "method": "item.Select", "id": "1", "params": {}}' )

    def test_creation_insert(self):
        empty_request = models.requests.JsonRPCRequest(method=models.requests.ApiMethod.insert)
        self.assertEqual(empty_request.json(), '{"jsonrpc": "2.0", "method": "integration.Insert", "id": "1", "params": {}}')

    def test_creation_save(self):
        empty_request = models.requests.JsonRPCRequest(method=models.requests.ApiMethod.save_signals)
        self.assertEqual(empty_request.json(), '{"jsonrpc": "2.0", "method": "integration.SaveSignals", "id": "1", "params": {}}')

    def test_creation_params(self):
        empty_request = models.requests.JsonRPCRequest()
        self.assertEqual( empty_request.json(), '{"jsonrpc": "2.0", "method": "item.Select", "id": "1", "params": {}}' )


if __name__ == '__main__':
    unittest.main()