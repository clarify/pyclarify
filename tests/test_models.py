import unittest
import sys

sys.path.insert(1, "src/")
import pyclarify.models as models


class TestModels(unittest.TestCase):
    def test_creation(self):
        empty_request = models.requests.JsonRPCRequest()
        self.assertEqual(
            empty_request.json(),
            '{"jsonrpc": "2.0", "method": "clarify.SelectItems", "id": "1", "params": {}}',
        )

    def test_creation_insert(self):
        empty_request = models.requests.JsonRPCRequest(
            method=models.requests.ApiMethod.insert
        )
        self.assertEqual(
            empty_request.json(),
            '{"jsonrpc": "2.0", "method": "integration.Insert", "id": "1", "params": {}}',
        )

    def test_creation_save(self):
        empty_request = models.requests.JsonRPCRequest(
            method=models.requests.ApiMethod.save_signals
        )
        self.assertEqual(
            empty_request.json(),
            '{"jsonrpc": "2.0", "method": "integration.SaveSignals", "id": "1", "params": {}}',
        )

    def test_creation_params_1(self):
        empty_request = models.requests.JsonRPCRequest(params={})
        self.assertEqual(
            empty_request.json(),
            '{"jsonrpc": "2.0", "method": "clarify.SelectItems", "id": "1", "params": {}}',
        )

    def test_creation_params_2(self):
        integration = "testintegration12345"
        times = ["2021-03-11T21:49:06Z", "2021-03-11T21:50:06Z"]
        values = [0.6, 1.0]
        signal_id = "test_123_id"
        data = models.data.ClarifyDataFrame(times=times, series={signal_id: values})
        empty_request = models.requests.JsonRPCRequest(
            method=models.requests.ApiMethod.insert,
            params=models.requests.ParamsInsert(integration=integration, data=data),
        )
        self.assertEqual(
            empty_request.json(),
            '{"jsonrpc": "2.0", "method": "integration.Insert", "id": "1", "params": {"integration": "testintegration12345", "data": {"times": ["2021-03-11T21:49:06+00:00", "2021-03-11T21:50:06+00:00"], "series": {"test_123_id": [0.6, 1.0]}}}}',
        )

    def test_insert_params_request(self):
        integration = "testintegration12345"
        times = ["2021-03-11T21:49:06Z", "2021-03-11T21:50:06Z"]
        values = [0.6, 1.0]
        signal_id = "test_123_id"
        data = models.data.ClarifyDataFrame(times=times, series={signal_id: values})
        empty_request = models.requests.InsertJsonRPCRequest(
            params=models.requests.ParamsInsert(integration=integration, data=data)
        )
        self.assertEqual(
            empty_request.json(),
            '{"jsonrpc": "2.0", "method": "integration.Insert", "id": "1", "params": {"integration": "testintegration12345", "data": {"times": ["2021-03-11T21:49:06+00:00", "2021-03-11T21:50:06+00:00"], "series": {"test_123_id": [0.6, 1.0]}}}}',
        )

    def test_regex(self):
        integration = "01234567890123456789"
        times = ["2021-03-11T21:49:06Z", "2021-03-11T21:50:06Z"]
        values = [0.6, 1.0]
        signal_id = "test_123_id"
        data = models.data.ClarifyDataFrame(times=times, series={signal_id: values})
        empty_request = models.requests.InsertJsonRPCRequest(
            params=models.requests.ParamsInsert(integration=integration, data=data)
        )
        self.assertEqual(
            empty_request.json(),
            '{"jsonrpc": "2.0", "method": "integration.Insert", "id": "1", "params": {"integration": "01234567890123456789", "data": {"times": ["2021-03-11T21:49:06+00:00", "2021-03-11T21:50:06+00:00"], "series": {"test_123_id": [0.6, 1.0]}}}}',
        )

    def test_merge_single_input(self):
        times = ["2021-03-11T21:49:06Z", "2021-03-11T21:50:06Z", "2021-03-11T21:51:06Z"]
        values = [0.6, 1.0, 2.4]
        signal_id = "signal_1"
        cdf = models.data.ClarifyDataFrame(times=times, series={signal_id: values})

        merged = models.data.merge([cdf])

        # expect merged to be same as single input
        self.assertEqual(merged, cdf)

    def test_merge_two_inputs(self):
        times = ["2021-03-11T21:49:06Z", "2021-03-11T21:50:06Z", "2021-03-11T21:51:06Z"]
        values = [0.6, 1.0, 2.4]
        signal_id = "signal_1"
        cdf = models.data.ClarifyDataFrame(times=times, series={signal_id: values})

        times = ["2021-03-10T21:49:06Z", "2021-03-10T21:50:06Z", "2021-03-11T21:51:06Z"]
        values = [0.3, 2.0, 3.5]
        signal_id = "signal_2"
        cdf2 = models.data.ClarifyDataFrame(times=times, series={signal_id: values})

        merged = models.data.merge([cdf, cdf2])
        merged_reverse = models.data.merge([cdf2, cdf])

        self.assertEqual(merged, merged_reverse)

    def test_merge_multiple_inputs(self):
        times = ["2021-03-11T21:49:06Z", "2021-03-11T21:50:06Z", "2021-03-11T21:51:06Z"]
        values = [0.6, 1.0, 2.4]
        signal_id = "signal_1"
        cdf = models.data.ClarifyDataFrame(times=times, series={signal_id: values})

        times = ["2021-03-10T21:49:06Z", "2021-03-10T21:50:06Z", "2021-03-11T21:51:06Z"]
        values = [0.3, 2.0, 3.5]
        signal_id = "signal_2"
        cdf2 = models.data.ClarifyDataFrame(times=times, series={signal_id: values})

        times = ["2021-03-09T21:49:06Z", "2021-03-09T21:50:06Z", "2021-03-11T21:51:06Z"]
        values = [0.6, 1.0, 2.4]
        signal_id = "signal_3"
        cdf3 = models.data.ClarifyDataFrame(times=times, series={signal_id: values})

        merged = models.data.merge([cdf, cdf2, cdf3])
        merged2 = models.data.merge([cdf, cdf3, cdf2])
        merged3 = models.data.merge([cdf2, cdf, cdf3])
        merged4 = models.data.merge([cdf2, cdf3, cdf])
        merged5 = models.data.merge([cdf3, cdf, cdf2])
        merged6 = models.data.merge([cdf3, cdf2, cdf])

        self.assertEqual(merged, merged2)
        self.assertEqual(merged, merged3)
        self.assertEqual(merged, merged4)
        self.assertEqual(merged, merged5)
        self.assertEqual(merged, merged6)

    def test_merge_equal_input(self):
        times = ["2021-03-11T21:49:06Z", "2021-03-11T21:50:06Z", "2021-03-11T21:51:06Z"]
        values = [0.6, 1.0, 2.4]
        signal_id = "signal_1"
        cdf = models.data.ClarifyDataFrame(times=times, series={signal_id: values})

        times = ["2021-03-11T21:49:06Z", "2021-03-11T21:50:06Z", "2021-03-11T21:51:06Z"]
        values = [0.6, 1.0, 2.4]
        signal_id = "signal_1"
        cdf2 = models.data.ClarifyDataFrame(times=times, series={signal_id: values})

        merged = models.data.merge([cdf, cdf2])

        self.assertEqual(merged, cdf)


if __name__ == "__main__":
    unittest.main()
