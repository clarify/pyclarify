import unittest
import sys

sys.path.insert(1, "src/")
from pyclarify.__utils__.time import is_datetime
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

if __name__ == "__main__":
    unittest.main()
