import unittest
import sys

sys.path.insert(1, "src/")
from pyclarify.__utils__.pagination import GetDates, GetItems
import datetime


class TestPagination(unittest.TestCase):
    def test_get_items(self):

        items = GetItems(50, 123, 45)
        item_iter = iter(items)

        self.assertEqual(next(item_iter), (50, 45))
        self.assertEqual(next(item_iter), (50, 95))
        self.assertEqual(next(item_iter), (23, 145))
        with self.assertRaises(StopIteration):
            next(item_iter)

    def test_get_dates(self):

        dates = GetDates(["2020-10-06T17:48:04Z", "2021-01-10T21:50:06Z"])
        dates_iter = iter(dates)

        self.assertEqual(
            next(dates_iter),
            (
                datetime.datetime(2020, 10, 6, 17, 48, 4),
                datetime.datetime(2020, 11, 15, 17, 48, 4),
            ),
        )
        self.assertEqual(
            next(dates_iter),
            (
                datetime.datetime(2020, 11, 15, 17, 48, 5),
                datetime.datetime(2020, 12, 25, 17, 48, 5),
            ),
        )
        self.assertEqual(
            next(dates_iter),
            (
                datetime.datetime(2020, 12, 25, 17, 48, 6),
                datetime.datetime(2021, 1, 10, 21, 50, 6),
            ),
        )
        with self.assertRaises(StopIteration):
            next(dates_iter)


if __name__ == "__main__":
    unittest.main()
