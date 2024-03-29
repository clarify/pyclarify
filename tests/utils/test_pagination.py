import unittest
import sys

sys.path.insert(1, "src/")
from pyclarify.__utils__.pagination import TimeIterator, SegmentIterator
import datetime


class TestPagination(unittest.TestCase):
    def test_item_iterator(self):

        items = SegmentIterator(user_limit=123, limit_per_call=50, skip=45)
        item_iter = iter(items)

        self.assertEqual(next(item_iter), (45, 50))
        self.assertEqual(next(item_iter), (95, 50))
        self.assertEqual(next(item_iter), (145, 23))
        with self.assertRaises(StopIteration):
            next(item_iter)

    def test_in_for_loop(self):
        i = 0
        for skip, limit in SegmentIterator(user_limit=123, limit_per_call=50, skip=45):
            if i == 0:
                self.assertEqual(skip, 45)
                self.assertEqual(limit, 50)
            if i == 1:
                self.assertEqual(skip, 95)
                self.assertEqual(limit, 50)
            if i == 2:
                self.assertEqual(skip, 145)
                self.assertEqual(limit, 23)
            i += 1

    def test_time_iterator(self):

        dates = TimeIterator(
            start_time="2020-10-06T17:48:04+00:00", end_time="2021-01-10T21:50:06+00:00"
        )
        dates_iter = iter(dates)
        self.assertEqual(
            next(dates_iter),
            (
                datetime.datetime(2020, 10, 6, 17, 48, 4,tzinfo=datetime.timezone.utc),
                datetime.datetime(2020, 11, 15, 17, 48, 4, tzinfo=datetime.timezone.utc),
            ),
        )
        self.assertEqual(
            next(dates_iter),
            (
                datetime.datetime(2020, 11, 15, 17, 48, 4,tzinfo=datetime.timezone.utc),
                datetime.datetime(2020, 12, 25, 17, 48, 4,tzinfo=datetime.timezone.utc),
            ),
        )
        self.assertEqual(
            next(dates_iter),
            (
                datetime.datetime(2020, 12, 25, 17, 48, 4,tzinfo=datetime.timezone.utc),
                datetime.datetime(2021, 1, 10, 21, 50, 6,tzinfo=datetime.timezone.utc),
            ),
        )
        with self.assertRaises(StopIteration):
            next(dates_iter)

    def test_time_iterator_short_cutoff(self):

        dates = TimeIterator(
            start_time="2022-07-10T00:00:00+00:00", end_time="2022-08-31T00:00:00+00:00"
        )
        dates_iter = iter(dates)
        self.assertEqual(
            next(dates_iter),
            (
                datetime.datetime(2022, 7, 10,tzinfo=datetime.timezone.utc),
                datetime.datetime(2022, 8, 19, tzinfo=datetime.timezone.utc),
            ),
        )
        self.assertEqual(
            next(dates_iter),
            (
                datetime.datetime(2022, 8, 19, tzinfo=datetime.timezone.utc),
                datetime.datetime(2022, 8, 31, tzinfo=datetime.timezone.utc),
            ),
        )
        with self.assertRaises(StopIteration):
            next(dates_iter)


    def test_time_iterator_rollup(self):

        dates = TimeIterator(
            start_time="2020-10-06T17:48:04Z",
            end_time="2021-01-10T21:50:06Z",
            rollup="P1DT",
        )
        dates_iter = iter(dates)

        self.assertEqual(
            next(dates_iter),
            (
                datetime.datetime(2020, 10, 6, 17, 48, 4,tzinfo=datetime.timezone.utc),
                datetime.datetime(2021, 1, 10, 21, 50, 6,tzinfo=datetime.timezone.utc),
            ),
        )

        with self.assertRaises(StopIteration):
            next(dates_iter)


if __name__ == "__main__":
    unittest.main()
