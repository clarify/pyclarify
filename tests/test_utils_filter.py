import unittest
import sys

sys.path.insert(1, "src/")
import pyclarify.__utils__.filter as filter
from pyclarify.__utils__.exceptions import PyClarifyFilterError




class TestFilter(unittest.TestCase):
    def setUp(self):
        self.f1 = filter.Filter(fields={"name": filter.NotEqual(value="Lufttemperatur")})
        self.f2 = filter.Filter(fields={"labels.unit-type": filter.NotIn(value=["Flåte", "Merde 5"])})
        self.f3 = filter.Filter(fields={"labels.unit_id": filter.In(value=["1"])})
        self.f4 = filter.Filter(fields={"labels.topic": filter.Regex(value="efb")})
        self.f5 = filter.Filter(fields={"name": filter.Comparison(value="Trondheim")})
        self.f6 = filter.Filter(fields={"depth": filter.LessThan(value=5)})
        self.f7 = filter.Filter(fields={"labels.unit_id": filter.GreaterThan(value=2)})
        self.f8 = filter.Filter(fields={"gapDetection": filter.GreaterThanOrEqual(value="PT15M")})

    
    def testSingleFilters(self):
        self.assertEqual(self.f1.to_query(), {'name': {'$ne': 'Lufttemperatur'}})
        self.assertEqual(self.f2.to_query(), {'labels.unit-type': {'$nin': ['Flåte', 'Merde 5']}})
        self.assertEqual(self.f3.to_query(), {'labels.unit_id': {'$in': ['1']}})
        self.assertEqual(self.f4.to_query(), {'labels.topic': {'$regex': 'efb'}})
        self.assertEqual(self.f5.to_query(), {'name': {'Trondheim'}})


    def testIllegalComparions(self):
        # Not Equal
        with self.assertRaises(PyClarifyFilterError):
            filter.NotEqual(value=["list", "not", "valid"])


        # Not In
        with self.assertRaises(PyClarifyFilterError):
            filter.NotIn(value=42)
        
        with self.assertRaises(PyClarifyFilterError):
            filter.NotIn(value="invalid")

        with self.assertRaises(PyClarifyFilterError):
            filter.NotIn(value=b'bytes')


        # In
        with self.assertRaises(PyClarifyFilterError):
            filter.In(value=42)
        
        with self.assertRaises(PyClarifyFilterError):
            filter.In(value="invalid")

        with self.assertRaises(PyClarifyFilterError):
            filter.In(value=b'bytes')


        # Regex 
        with self.assertRaises(PyClarifyFilterError):
            filter.Regex(value=["list", "not", "valid"])

        # Comparison
        with self.assertRaises(PyClarifyFilterError):
            filter.Comparison(value=["list", "not", "valid"])
        
        
        # Less Than
        with self.assertRaises(PyClarifyFilterError):
            filter.LessThan(value=["list", "not", "valid"])
        

        # GreaterThan
        with self.assertRaises(PyClarifyFilterError):
            filter.GreaterThan(value=["list", "not", "valid"])
        

        # Greater Than or Equal
        with self.assertRaises(PyClarifyFilterError):
            filter.GreaterThanOrEqual(value=["list", "not", "valid"])
        


    def testCombinationFilters(self):
        self.assertEqual(self.f1.to_query(), {'name': {'$ne': 'Lufttemperatur'}})
        self.assertEqual(self.f2.to_query(), {'labels.unit-type': {'$nin': ['Flåte', 'Merde 5']}})

        f = self.f1 & self.f2
        self.assertIsInstance(f, filter.Filter)

        self.assertEqual(f.to_query(), {
            '$and': [
                {'name': {'$ne': 'Lufttemperatur'}},
                {'labels.unit-type': {'$nin': ['Flåte', 'Merde 5']}}
                ]
            }
        )

if __name__ == "__main__":
    unittest.main()
