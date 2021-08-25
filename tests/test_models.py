import unittest
import sys

sys.path.insert(1, "src/pyclarify")
import models


class TestModels(unittest.TestCase):
    def test_creation(self):
        empty_request = models.requests.JsonRPCRequest()
        self.assertEqual(empty_request.json(), '{"jsonrpc": "2.0", "method": "item.Select", "id": "1", "params": {}}')

    def test_creation_insert(self):
        empty_request = models.requests.JsonRPCRequest(method=models.requests.ApiMethod.insert)
        self.assertEqual(empty_request.json(),
                         '{"jsonrpc": "2.0", "method": "integration.Insert", "id": "1", "params": {}}')

    def test_creation_save(self):
        empty_request = models.requests.JsonRPCRequest(method=models.requests.ApiMethod.save_signals)
        self.assertEqual(empty_request.json(),
                         '{"jsonrpc": "2.0", "method": "integration.SaveSignals", "id": "1", "params": {}}')

    def test_creation_params_1(self):
        empty_request = models.requests.JsonRPCRequest(params={})
        self.assertEqual(empty_request.json(), '{"jsonrpc": "2.0", "method": "item.Select", "id": "1", "params": {}}')

    def test_creation_params_2(self):
        integration = "testintegration12345"
        times = ["2021-03-11T21:49:06Z", "2021-03-11T21:50:06Z"]
        values = [0.6, 1.0]
        signal_id = "test_123_id"
        data = models.data.ClarifyDataFrame(times=times, series={signal_id: values})
        empty_request = models.requests.JsonRPCRequest(method=models.requests.ApiMethod.insert,
                                                       params=models.requests.ParamsInsert(integration=integration,
                                                                                           data=data))
        self.assertEqual(empty_request.json(),
                         '{"jsonrpc": "2.0", "method": "integration.Insert", "id": "1", "params": {"integration": "testintegration12345", "data": {"times": ["2021-03-11T21:49:06+00:00", "2021-03-11T21:50:06+00:00"], "series": {"test_123_id": [0.6, 1.0]}}}}')

    def test_insert_params_request(self):
        integration = "testintegration12345"
        times = ["2021-03-11T21:49:06Z", "2021-03-11T21:50:06Z"]
        values = [0.6, 1.0]
        signal_id = "test_123_id"
        data = models.data.ClarifyDataFrame(times=times, series={signal_id: values})
        empty_request = models.requests.InsertJsonRPCRequest(
            params=models.requests.ParamsInsert(integration=integration,
                                                data=data))
        self.assertEqual(empty_request.json(),
                         '{"jsonrpc": "2.0", "method": "integration.Insert", "id": "1", "params": {"integration": "testintegration12345", "data": {"times": ["2021-03-11T21:49:06+00:00", "2021-03-11T21:50:06+00:00"], "series": {"test_123_id": [0.6, 1.0]}}}}')

    def test_regex(self):
        integration = "01234567890123456789"
        times = ["2021-03-11T21:49:06Z", "2021-03-11T21:50:06Z"]
        values = [0.6, 1.0]
        signal_id = "test_123_id"
        data = models.data.ClarifyDataFrame(times=times, series={signal_id: values})
        empty_request = models.requests.InsertJsonRPCRequest(
            params=models.requests.ParamsInsert(integration=integration,
                                                data=data))
        self.assertEqual(empty_request.json(),
                         '{"jsonrpc": "2.0", "method": "integration.Insert", "id": "1", "params": {"integration": "01234567890123456789", "data": {"times": ["2021-03-11T21:49:06+00:00", "2021-03-11T21:50:06+00:00"], "series": {"test_123_id": [0.6, 1.0]}}}}')


if __name__ == '__main__':
    unittest.main()


""" TODO:
- Implement test for Signal and SaveSignal models

"""