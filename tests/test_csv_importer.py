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

import sys
import unittest
import json
from datetime import datetime, timedelta
from unittest.mock import patch

sys.path.insert(1, "src/")
from pyclarify.client import ClarifyClient
import pyclarify
from pyclarify import DataFrame

""" This is a implementation of tests as subclass of unittest.TestCase for CsvImporter """


class TestCsvImporter(unittest.TestCase):
    def setUp(self):
        self.client = ClarifyClient("./tests/data/mock-clarify-credentials.json")

        with open("./tests/data/mock-client-common.json") as f:
            self.mock_data = json.load(f)

        self.mock_access_token = self.mock_data["mock_access_token"]

        with open("./tests/data/mock-insert.json") as f:
            self.mock_data = json.load(f)

    @patch("pyclarify.client.RawClient.get_token")
    @patch("pyclarify.client.requests.post")
    def test_send_insert(self, client_req_mock, get_token_mock):
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.mock_data["mock_response_1"]

        csv_importer1 = pyclarify.importer.CsvImporter(
            "tests/data/mock-csv-sep-comma.csv"
        )
        csv_importer1.read_csv(delimiter=",").insert_csv_data(
            self.client, labels_dict=None
        )

        csv_importer2 = pyclarify.importer.CsvImporter(
            "tests/data/mock-csv-sep-semicolon-time-col2.csv"
        )
        csv_importer2.read_csv(delimiter=";", time_index_column=1).insert_csv_data(
            self.client, labels_dict=None
        )
        self.assertDictEqual(csv_importer2.data, csv_importer1.data)

        convert_date = lambda date_time_str: datetime.strptime(
            date_time_str, "%d/%m/%Y %H:%M:%S"
        )
        convert_float = lambda float_str: float(float_str.replace(",", "."))

        csv_importer3 = pyclarify.importer.CsvImporter(
            "tests/data/mock-csv-convert-time-convert-vals.csv"
        )
        csv_importer3.read_csv(
            delimiter=";",
            time_index_column=2,
            time_converter=convert_date,
            values_converter={0: convert_float, 1: convert_float},
        ).insert_csv_data(self.client, labels_dict=None)
        self.assertDictEqual(csv_importer3.data, csv_importer1.data)

        csv_importer4 = pyclarify.importer.CsvImporter(
            "tests/data/mock-csv-sep-comma-enum.csv"
        )
        csv_importer4.read_csv(delimiter=",", time_index_column=3).insert_csv_data(
            self.client, labels_dict=None
        )
        self.assertEqual(
            csv_importer4.data["Timestamp"], csv_importer1.data["Timestamp"]
        )
        self.assertEqual(
            csv_importer4.data["Mock Test - Oxygen"],
            csv_importer1.data["Mock Test - Oxygen"],
        )
        self.assertEqual(csv_importer4.data["Mock Test - Enum Cat"], [0, 1, 0, 1])


if __name__ == "__main__":
    unittest.main()
