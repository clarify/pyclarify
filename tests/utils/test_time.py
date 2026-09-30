import unittest
import sys

sys.path.insert(1, "src/")
from pyclarify.__utils__.time import is_datetime, parse_datetime
import datetime
import numpy as np


class TestTime(unittest.TestCase):
    def test_possible_scenarios(self):
        self.assertFalse(is_datetime(-1))
        self.assertFalse(is_datetime(0))
        self.assertFalse(is_datetime(1))
        self.assertFalse(is_datetime(-1.0))
        self.assertFalse(is_datetime(0.0))
        self.assertFalse(is_datetime(1.0))
        self.assertFalse(is_datetime(np.nan))
        self.assertFalse(is_datetime("hello"))
        self.assertFalse(is_datetime(""))
        self.assertFalse(is_datetime("aVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryLongString"))
        self.assertFalse(is_datetime(100000000000000000))
        self.assertFalse(is_datetime(-10000000000))
        # Timestamp of 2122
        self.assertFalse(is_datetime(4800000000))
        # Must be newer than 1973
        self.assertFalse(is_datetime("1814-05-17T12:00:00+02:00"))

        self.assertTrue(is_datetime("2020-01-01T00:00:00Z"))
        self.assertTrue(is_datetime("2020-01-01T00:00:00+00:00"))
        self.assertTrue(is_datetime("2020-01-01"))
        self.assertTrue(is_datetime(datetime.datetime(year=2020,month=1,day=1,hour=0,minute=0,second=0)))
        
        # Timestamp of < 2122
        self.assertTrue(is_datetime(4799999999))

    def test_numpy_datetimes_of_any_resolution(self):
        # pandas 2 gives nanosecond datetimes, pandas 3 microsecond ones.
        expected = datetime.datetime(2021, 11, 1, 21, 50, 6, 500000, tzinfo=datetime.timezone.utc)
        for unit in ("ns", "us", "ms"):
            with self.subTest(unit=unit):
                value = np.datetime64("2021-11-01T21:50:06.500", unit)
                self.assertEqual(parse_datetime(value), expected)
                self.assertTrue(is_datetime(value))
        self.assertFalse(is_datetime(np.datetime64("NaT")))

if __name__ == "__main__":
    unittest.main()
