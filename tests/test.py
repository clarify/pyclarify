import sys
import unittest
sys.path.insert(1, 'src/pyclarify')
from interface import ServiceInterface


class TestBase(unittest.TestCase):
    def setUp(self):
        self.interface = ServiceInterface()

    def test_greeting(self):
        """
        Test for recieving geeting from interfce
        """
        greeting = self.interface.greeting()
        self.assertEqual(greeting, "Welcome to Clarify Python SDK")
        

if __name__ == '__main__':
    unittest.main()