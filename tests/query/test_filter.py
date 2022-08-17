import unittest
import sys

sys.path.insert(1, "src/")
from pyclarify import query
from pyclarify.__utils__.exceptions import FilterError


class TestFilter(unittest.TestCase):
    def setUp(self):
        self.f1 = query.Filter(fields={"name": query.NotEqual(value="Lufttemperatur")})
        self.f2 = query.Filter(
            fields={"labels.unit-type": query.NotIn(value=["Flåte", "Merde 5"])}
        )
        self.f3 = query.Filter(fields={"labels.unit_id": query.In(value=["1"])})
        self.f4 = query.Filter(fields={"labels.topic": query.Regex(value="efb")})
        self.f5 = query.Filter(fields={"name": query.Equal(value="Trondheim")})
        self.f6 = query.Filter(fields={"depth": query.LessThan(value=5)})
        self.f7 = query.Filter(fields={"labels.unit_id": query.GreaterThan(value=2)})
        self.f8 = query.Filter(
            fields={"gapDetection": query.GreaterThanOrEqual(value="PT15M")}
        )

    def testSingleFilters(self):
        self.assertEqual(self.f1.to_query(), {"name": {"$ne": "Lufttemperatur"}})
        self.assertEqual(
            self.f2.to_query(), {"labels.unit-type": {"$nin": ["Flåte", "Merde 5"]}}
        )
        self.assertEqual(self.f3.to_query(), {"labels.unit_id": {"$in": ["1"]}})
        self.assertEqual(self.f4.to_query(), {"labels.topic": {"$regex": "efb"}})
        self.assertEqual(self.f5.to_query(), {"name": {"Trondheim"}})

    def testIllegalComparions(self):
        # Not Equal
        with self.assertRaises(FilterError):
            query.NotEqual(value=["list", "not", "valid"])

        # Not In
        with self.assertRaises(FilterError):
            query.NotIn(value=42)

        with self.assertRaises(FilterError):
            query.NotIn(value="invalid")

        with self.assertRaises(FilterError):
            query.NotIn(value=b"bytes")

        # In
        with self.assertRaises(FilterError):
            query.In(value=42)

        with self.assertRaises(FilterError):
            query.In(value="invalid")

        with self.assertRaises(FilterError):
            query.In(value=b"bytes")

        # Regex
        with self.assertRaises(FilterError):
            query.Regex(value=["list", "not", "valid"])

        # Equal
        with self.assertRaises(FilterError):
            query.Equal(value=["list", "not", "valid"])

        # Less Than
        with self.assertRaises(FilterError):
            query.LessThan(value=["list", "not", "valid"])

        # GreaterThan
        with self.assertRaises(FilterError):
            query.GreaterThan(value=["list", "not", "valid"])

        # Greater Than or Equal
        with self.assertRaises(FilterError):
            query.GreaterThanOrEqual(value=["list", "not", "valid"])

    def testCombinationFilters(self):
        self.assertEqual(self.f1.to_query(), {"name": {"$ne": "Lufttemperatur"}})
        self.assertEqual(
            self.f2.to_query(), {"labels.unit-type": {"$nin": ["Flåte", "Merde 5"]}}
        )

        f = self.f1 & self.f2
        self.assertIsInstance(f, query.Filter)

        self.assertEqual(
            f.to_query(),
            {
                "$and": [
                    {"name": {"$ne": "Lufttemperatur"}},
                    {"labels.unit-type": {"$nin": ["Flåte", "Merde 5"]}},
                ]
            },
        )


if __name__ == "__main__":
    unittest.main()
