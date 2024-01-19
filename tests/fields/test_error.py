import unittest
import sys
import json

sys.path.insert(1, "src/")
from pyclarify.fields.error import Error, ErrorData


class TestError(unittest.TestCase):
    def setUp(self):
        with open("./tests/mock_data/generics.json") as f:
            self.mock_data = json.load(f)
        self.error_data = self.mock_data["error_data"]
        self.error = self.mock_data["error"]

    def test_error_data(self):
        error_data = ErrorData(**self.error_data)
        self.assertEqual(
            error_data.model_dump_json(),
            json.dumps(self.error_data, separators=(',', ':')),
        )

    def test_error(self):
        error = Error(**self.error)
        self.assertEqual(
            error.model_dump_json(),
            json.dumps(self.error, separators=(',', ':')),
        )


if __name__ == "__main__":
    unittest.main()
