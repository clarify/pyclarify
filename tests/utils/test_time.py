"""
Copyright 2021 Clarify

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
import unittest
from datetime import datetime

sys.path.insert(1, "src/")
from pyclarify.__utils__.time import time_to_string, compute_iso_timewindow


class TestTime(unittest.TestCase):
    def setUp(self):
        # consistent time
        self.string_start_time = "2022-01-01T01:01:01Z"
        self.string_end_time = "2022-10-01T01:01:01Z"
        self.start_time = datetime.strptime(self.string_start_time, "%Y-%m-%dT%H:%M:%SZ")
        self.end_time = datetime.strptime(self.string_end_time, "%Y-%m-%dT%H:%M:%SZ")

    def test_convert_time_to_string(self):
        self.assertEqual(time_to_string(self.start_time), self.string_start_time)
        self.assertEqual(time_to_string(self.end_time), self.string_end_time)

    def test_compute_iso_timewindow(self):
        start_time, end_time = compute_iso_timewindow(self.string_start_time, self.string_end_time)
        self.assertEqual(start_time, self.string_start_time)
        self.assertEqual(end_time, self.string_end_time)

        start_time, end_time = compute_iso_timewindow(self.start_time, self.end_time)
        self.assertEqual(start_time, self.string_start_time)
        self.assertEqual(end_time, self.string_end_time)

if __name__ == "__main__":
    unittest.main()
