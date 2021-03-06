import unittest
import sys
import json
from pydantic.error_wrappers import ValidationError

sys.path.insert(1, "src/")
from pyclarify.models.data import *
from pyclarify.__utils__.auxiliary import *


class TestSummary(unittest.TestCase):
    def setUp(self):
        with open("./tests/data/mock-models-data.json") as f:
            self.mock_data = json.load(f)
        self.generic_summary = self.mock_data["generic_summary"]

    def test_generic_summary(self):
        try:
            summary = GenericSummary(**self.generic_summary)
        except ValidationError:
            self.fail("GenericSummary raised ValidationError unexpectedly!")

        self.assertEqual(summary.json(), json.dumps(self.generic_summary))

    def test_insert_summary(self):
        pass

    def test_save_summary(self):
        summary = self.generic_summary
        summary["updated"] = True

        try:
            summary = SaveSummary(**summary)
        except ValidationError:
            self.fail("SaveSummary raised ValidationError unexpectedly!")

        # assert type validation
        with self.assertRaises(ValidationError):
            SaveSummary(id="c618rbfqfsj7mjkj0ss1", created=True, updated="string")

        with self.assertRaises(ValidationError):
            SaveSummary(id="c618rbfqfsj7mjkj0ss1", created="string", updated=True)

        with self.assertRaises(ValidationError):
            SaveSummary(id=True, created=True, updated=True)


class TestMerge(unittest.TestCase):
    def setUp(self):
        with open("./tests/data/mock-models-data.json") as f:
            self.mock_data = json.load(f)
        self.mock_data_1 = self.mock_data["mock_data_1"]
        self.mock_data_2 = self.mock_data["mock_data_2"]
        self.mock_data_3 = self.mock_data["mock_data_3"]

        self.cdf = DataFrame(
            times=self.mock_data_1["times"],
            series={self.mock_data_1["signal"]: self.mock_data_1["values"]},
        )

        self.cdf2 = DataFrame(
            times=self.mock_data_2["times"],
            series={self.mock_data_2["signal"]: self.mock_data_2["values"]},
        )

        self.cdf3 = DataFrame(
            times=self.mock_data_3["times"],
            series={self.mock_data_3["signal"]: self.mock_data_3["values"]},
        )

    def test_merge_single_input(self):
        merged = merge([self.cdf])

        # expect merged to be same as single input
        self.assertEqual(merged, self.cdf)

    def test_merge_two_inputs(self):
        merged = merge([self.cdf, self.cdf2])
        merged_reverse = merge([self.cdf2, self.cdf])

        self.assertEqual(merged, merged_reverse)

    def test_merge_multiple_inputs(self):

        merged = merge([self.cdf, self.cdf2, self.cdf3])
        merged2 = merge([self.cdf, self.cdf3, self.cdf2])
        merged3 = merge([self.cdf2, self.cdf, self.cdf3])
        merged4 = merge([self.cdf2, self.cdf3, self.cdf])
        merged5 = merge([self.cdf3, self.cdf, self.cdf2])
        merged6 = merge([self.cdf3, self.cdf2, self.cdf])

        self.assertEqual(merged, merged2)
        self.assertEqual(merged, merged3)
        self.assertEqual(merged, merged4)
        self.assertEqual(merged, merged5)
        self.assertEqual(merged, merged6)

    def test_merge_equal_input(self):
        merged = merge([self.cdf, self.cdf])

        self.assertEqual(merged, self.cdf)


class TestPandas(unittest.TestCase):
    def setUp(self):
        with open("./tests/data/mock-models-data.json") as f:
            self.mock_data = json.load(f)

        self.pd = local_import("pandas")
        self.mock_data_1 = self.mock_data["mock_data_1"]
        self.mock_data_2 = self.mock_data["mock_data_2"]
        self.mock_data_3 = self.mock_data["mock_data_3"]

        self.cdf = DataFrame(
            times=self.mock_data_1["times"],
            series={self.mock_data_1["signal"]: self.mock_data_1["values"]},
        )

        self.cdf2 = DataFrame(
            times=self.mock_data_2["times"],
            series={self.mock_data_2["signal"]: self.mock_data_2["values"]},
        )

        self.cdf3 = DataFrame(
            times=self.mock_data_3["times"],
            series={
                self.mock_data_1["signal"]: self.mock_data_1["values"],
                self.mock_data_2["signal"]: self.mock_data_2["values"],
                self.mock_data_3["signal"]: self.mock_data_3["values"],
            },
        )

    def test_convert_single_signal(self):
        df = self.cdf.to_pandas()

        # Is of type pandas.DataFrame
        self.assertIsInstance(df, self.pd.DataFrame)

        # Assert that values are correctly transferred
        signal = list(self.cdf.series.keys())[0]

        # Signal name
        self.assertEqual(signal, df.columns[0])

        # Values
        # NB: Change numpy float to native float
        values = [x.item() for x in df[signal].values]

        self.assertEqual(self.cdf.series[signal], values)

        # Times
        # NB: Change both values to timestamp
        from datetime import datetime

        # Divide by 10^9 because of microseconds
        numpy_ts = [int(x / 1e9) for x in df.index.values.tolist()]
        clarify_ts = [datetime.timestamp(x) for x in self.cdf.times]
        self.assertEqual(clarify_ts, numpy_ts)

    def test_convert_three_signals(self):
        df = self.cdf3.to_pandas()

        # Is of type pandas.DataFrame
        self.assertIsInstance(df, self.pd.DataFrame)

        # Assert that values are correctly transferred
        signals = list(self.cdf3.series.keys())

        # Signal name
        self.assertEqual(signals, list(df.columns))

        # Values
        self.assertEqual(
            list(self.cdf3.series.values()), list(df.to_dict(orient="list").values())
        )

        # Times
        # NB: Change both values to timestamp
        from datetime import datetime

        # Divide by 10^9 because of microseconds
        numpy_ts = [int(x / 1e9) for x in df.index.values.tolist()]
        clarify_ts = [datetime.timestamp(x) for x in self.cdf3.times]
        self.assertEqual(clarify_ts, numpy_ts)


if __name__ == "__main__":
    unittest.main()
