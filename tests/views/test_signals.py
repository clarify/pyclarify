import unittest
import sys
import json
from pydantic import ValidationError
from datetime import datetime, timedelta

sys.path.insert(1, "src/")

from pyclarify.views.signals import (
    SelectSignalsParams,
    SaveSignalsParams,
    SaveSignalsResponse,
)

class TestSaveSignalsParams(unittest.TestCase):
    def setUp(self):
        with open("./tests/mock_data/signals.json") as f:
            self.mock_data = json.load(f)
        self.save_signals_params = self.mock_data["save_signals"]["args"]

    def test_save_signals_params(self):
        try:
            SaveSignalsParams(**self.save_signals_params)
        except ValidationError:
            self.fail("SaveSignalsParams raised ValidationError unexpectedly!")

        try:
            SaveSignalsParams(
                integration="c618rbfqfsj7mjkj0ss1", inputs={}, createOnly=True
            )
        except ValidationError:
            self.fail("SaveSignalsParams raised ValidationError unexpectedly!")

        # assert type validation
        with self.assertRaises(ValidationError):
            SaveSignalsParams(inputs="string")
        with self.assertRaises(ValidationError):
            SaveSignalsParams(createOnly="string")
        with self.assertRaises(ValidationError):
            SaveSignalsParams(integration="string")

class TestMaps(unittest.TestCase):
    def setUp(self):
        with open("./tests/mock_data/signals.json") as f:
            self.mock_data = json.load(f)
        self.save_signal_response = self.mock_data["save_signals"]["response"]

    def test_save_signals_map(self):
        try:
            SaveSignalsResponse(**self.save_signal_response)
        except ValidationError:
            self.fail("SaveSignalsResponse raised ValidationError unexpectedly!")


class TestSelectSignalsParams(unittest.TestCase):
    def setUp(self):
        with open("./tests/mock_data/signals.json") as f:
            self.mock_data = json.load(f)
        select_signals_args = self.mock_data["select_signals"]["args"]
        include = select_signals_args.pop("include")
        self.select_signals_params = {"query": select_signals_args}
        self.select_signals_params["integration"] = "c618rbfqfsj7mjkj0ss1"
        self.select_signals_params["include"] = include

    def test_select_signals_params(self):
        try:
            SelectSignalsParams(**self.select_signals_params)
        except ValidationError:
            self.fail("SelectSignalsParams raised ValidationError unexpectedly!")

        try:
            SelectSignalsParams(
                integration="c618rbfqfsj7mjkj0ss1",
                query={"filter":{}},
            )
        except ValidationError:
            self.fail("SelectSignalsParams raised ValidationError unexpectedly!")

        # assert type validation
        with self.assertRaises(ValidationError):
            SelectSignalsParams(inputs="string")
        with self.assertRaises(ValidationError):
            SelectSignalsParams(query={})
        with self.assertRaises(ValidationError):
            SelectSignalsParams(integration="string")
