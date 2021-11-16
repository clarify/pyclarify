"""
Copyright 2021 Clarify

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest
import sys
import json

sys.path.insert(1, "src/")
import pyclarify.models as models


class TestJSONRPCRequest(unittest.TestCase):
    def setUp(self):
        with open("./tests/data/mock-models.json") as f:
            self.mock_data = json.load(f)

    def test_creation(self):
        empty_request = models.requests.JSONRPCRequest()
        self.assertEqual(
            empty_request.json(),
            json.dumps(self.mock_data["select_items"]),
        )

    def test_creation_insert(self):
        empty_request = models.requests.JSONRPCRequest(
            method=models.requests.ApiMethod.insert
        )
        self.assertEqual(
            empty_request.json(),
            json.dumps(self.mock_data["insert"]),
        )

    def test_creation_save(self):
        empty_request = models.requests.JSONRPCRequest(
            method=models.requests.ApiMethod.save_signals
        )
        self.assertEqual(
            empty_request.json(),
            json.dumps(self.mock_data["save_signals"]),
        )

    def test_creation_params_1(self):
        empty_request = models.requests.JSONRPCRequest(params={})
        self.assertEqual(
            empty_request.json(),
            json.dumps(self.mock_data["select_items"]),
        )

    def test_creation_params_2(self):
        integration = self.mock_data["mock_integration"]
        times = self.mock_data["mock_times"]
        values = self.mock_data["mock_values"]
        signal_id = self.mock_data["mock_signal_id"]
        data = models.data.DataFrame(times=times, series={signal_id: values})
        empty_request = models.requests.JSONRPCRequest(
            method=models.requests.ApiMethod.insert,
            params=models.requests.InsertParams(integration=integration, data=data),
        )
        self.assertEqual(
            empty_request.json(),
            json.dumps(self.mock_data["mock_request"]),
        )


class TestInsertRequest(unittest.TestCase):
    def setUp(self):
        with open("./tests/data/mock-models.json") as f:
            self.mock_data = json.load(f)

    def test_insert_params_request(self):
        integration = self.mock_data["mock_integration"]
        times = self.mock_data["mock_times"]
        values = self.mock_data["mock_values"]
        signal_id = self.mock_data["mock_signal_id"]
        data = models.data.DataFrame(times=times, series={signal_id: values})
        empty_request = models.requests.InsertRequest(
            params=models.requests.InsertParams(integration=integration, data=data)
        )
        self.assertEqual(
            empty_request.json(),
            json.dumps(self.mock_data["mock_request"]),
        )

    def test_regex(self):
        integration = "01234567890123456789"
        times = self.mock_data["mock_times"]
        values = self.mock_data["mock_values"]
        signal_id = self.mock_data["mock_signal_id"]
        data = models.data.DataFrame(times=times, series={signal_id: values})
        empty_request = models.requests.InsertRequest(
            params=models.requests.InsertParams(integration=integration, data=data)
        )
        self.assertEqual(
            empty_request.json(),
            json.dumps(self.mock_data["mock_request_regex"]),
        )


class TestMerge(unittest.TestCase):
    def setUp(self):
        with open("./tests/data/mock-models.json") as f:
            self.mock_data = json.load(f)
        self.mock_data_1 = self.mock_data["mock_data_1"]
        self.mock_data_2 = self.mock_data["mock_data_2"]
        self.mock_data_3 = self.mock_data["mock_data_3"]

        self.cdf = models.data.DataFrame(
            times=self.mock_data_1["times"],
            series={self.mock_data_1["signal"]: self.mock_data_1["values"]},
        )

        self.cdf2 = models.data.DataFrame(
            times=self.mock_data_2["times"],
            series={self.mock_data_2["signal"]: self.mock_data_2["values"]},
        )

        self.cdf3 = models.data.DataFrame(
            times=self.mock_data_3["times"],
            series={self.mock_data_3["signal"]: self.mock_data_3["values"]},
        )

    def test_merge_single_input(self):
        merged = models.data.merge([self.cdf])

        # expect merged to be same as single input
        self.assertEqual(merged, self.cdf)

    def test_merge_two_inputs(self):
        merged = models.data.merge([self.cdf, self.cdf2])
        merged_reverse = models.data.merge([self.cdf2, self.cdf])

        self.assertEqual(merged, merged_reverse)

    def test_merge_multiple_inputs(self):

        merged = models.data.merge([self.cdf, self.cdf2, self.cdf3])
        merged2 = models.data.merge([self.cdf, self.cdf3, self.cdf2])
        merged3 = models.data.merge([self.cdf2, self.cdf, self.cdf3])
        merged4 = models.data.merge([self.cdf2, self.cdf3, self.cdf])
        merged5 = models.data.merge([self.cdf3, self.cdf, self.cdf2])
        merged6 = models.data.merge([self.cdf3, self.cdf2, self.cdf])

        self.assertEqual(merged, merged2)
        self.assertEqual(merged, merged3)
        self.assertEqual(merged, merged4)
        self.assertEqual(merged, merged5)
        self.assertEqual(merged, merged6)

    def test_merge_equal_input(self):
        merged = models.data.merge([self.cdf, self.cdf])

        self.assertEqual(merged, self.cdf)


class TestOauthModels(unittest.TestCase):
    def setUp(self):
        with open("./tests/data/mock-clarify-credentials.json") as f:
            self.credentials_dict = json.load(f)

    def test_populate_auth_objs(self):
        credential_obj = models.auth.ClarifyCredential(**self.credentials_dict)
        self.assertEqual(credential_obj.credentials.type, "client-credentials")
        oauth_request_obj = models.auth.OAuthRequestBody(
            client_id=credential_obj.credentials.clientId,
            client_secret=credential_obj.credentials.clientSecret,
        )
        self.assertEqual(
            oauth_request_obj.client_id, credential_obj.credentials.clientId
        )


if __name__ == "__main__":
    unittest.main()
