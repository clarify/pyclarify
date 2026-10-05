import unittest
import sys
import warnings

sys.path.insert(1, "src/")
from pyclarify.__utils__.warnings import deprecated


@deprecated("use new_function")
def old_function():
    return "result"


@deprecated
class OldClass:
    pass


class TestDeprecated(unittest.TestCase):
    def test_function_with_reason(self):
        with self.assertWarnsRegex(DeprecationWarning, r"Call to deprecated function old_function \(use new_function\)\."):
            self.assertEqual(old_function(), "result")

    def test_class_without_reason(self):
        with self.assertWarnsRegex(DeprecationWarning, r"Call to deprecated class OldClass\."):
            self.assertIsInstance(OldClass(), OldClass)

    def test_leaves_the_warning_filters_alone(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            filters = list(warnings.filters)
            old_function()
            self.assertEqual(warnings.filters, filters)


if __name__ == "__main__":
    unittest.main()
