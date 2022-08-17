import unittest
import sys
import json
from pydantic.error_wrappers import ValidationError

sys.path.insert(1, "src/")
from pyclarify.views.items import (
    SelectItemsParams,
    PublishSignalsParams,
    SelectItemsDataParams,
    SaveSummary,
    PublishSignalsResponse,
)



class TestSelectItems(unittest.TestCase):
    def setUp(self):
        with open("./tests/mock_data/items.json") as f:
            self.mock_data = json.load(f)
        select_items_args = self.mock_data["select_items"]["args"]
        self.select_items_params = {"query": select_items_args}

    def test_select_items_params(self):
        try:
            SelectItemsParams(**self.select_items_params)
        except ValidationError:
            self.fail("SelectItemsParams raised ValidationError unexpectedly!")

        try:
            SelectItemsParams(query= {"filter": {}}, include=[], groupIncludedByType = False)
        except ValidationError:
            self.fail("SelectItemsParams raised ValidationError unexpectedly!")

        with self.assertRaises(ValidationError):
            SelectItemsParams(items="string")
        with self.assertRaises(ValidationError):
            SelectItemsParams(data="string")

class TestPublishSignalsParams(unittest.TestCase):
    def setUp(self):
        with open("./tests/mock_data/items.json") as f:
            self.mock_data = json.load(f)
        self.publish_signals_args = self.mock_data["publish_signals"]["args"]

    def test_publish_signals_params(self):
        try:
            PublishSignalsParams(**self.publish_signals_args)
        except ValidationError:
            self.fail("InsertParams raised ValidationError unexpectedly!")

        try:
            PublishSignalsParams(
                integration="c618rbfqfsj7mjkj0ss1", itemsBySignal={}, createOnly=True
            )
        except ValidationError:
            self.fail("InsertParams raised ValidationError unexpectedly!")

        with self.assertRaises(ValidationError):
            PublishSignalsParams(integration="string")
        with self.assertRaises(ValidationError):
            PublishSignalsParams(data="string")


class TestPublishSignalsResponse(unittest.TestCase):
    def setUp(self):
        with open("./tests/mock_data/items.json") as f:
            mock_data = json.load(f)
            self.publish_signal_response = mock_data["publish_signals"]["response"]

    def test_publish_signals_map(self):
        try:
            PublishSignalsResponse(**self.publish_signal_response)
        except ValidationError:
            self.fail("PublishSignalsResponse raised ValidationError unexpectedly!")


class TestSaveSummary(unittest.TestCase):
    def setUp(self):
        with open("./tests/mock_data/dataframe.json") as f:
            mock_data = json.load(f)
            self.generic_summary = mock_data["generic_summary"]

    def test_save_summary(self):
        summary = self.generic_summary
        summary["updated"] = True

        try:
            summary = SaveSummary(**summary)
        except ValidationError:
            self.fail("SaveSummary raised ValidationError unexpectedly!")

        with self.assertRaises(ValidationError):
            SaveSummary(id="c618rbfqfsj7mjkj0ss1", created=True, updated="string")

        with self.assertRaises(ValidationError):
            SaveSummary(id="c618rbfqfsj7mjkj0ss1", created="string", updated=True)

        with self.assertRaises(ValidationError):
            SaveSummary(id=True, created=True, updated=True)
