import unittest
import sys
import json

sys.path.insert(1, "src/")
from pyclarify.__utils__.time import rfc3339_to_timedelta
from datetime import timedelta


class TestTime(unittest.TestCase):
    def setUp(self):
        with open("./tests/data/mock-utils-time.json") as f:
            self.mock_data = json.load(f)
        self.rfc_data_inputs = self.mock_data["rfc3339"]["inputs"]
        self.rfc_data_outputs = self.mock_data["rfc3339"]["outputs"]
    
    def test_rfc3339_to_timedelta(self):
        for inp, outp in zip(self.rfc_data_inputs, self.rfc_data_outputs):
            self.assertEqual(rfc3339_to_timedelta(inp), timedelta(seconds=outp))

if __name__ == "__main__":
    unittest.main()
