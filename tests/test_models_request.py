import unittest
import sys
import json
from pydantic.error_wrappers import ValidationError
from datetime import datetime, timedelta

sys.path.insert(1, "src/")
from pyclarify.fields.constraints import ApiMethod
from pyclarify.views.generics import Request, JSONRPCRequest
from pyclarify.views.dataframe import InsertParams
from pyclarify.views.items import (
    SelectItemsParams,
    PublishSignalsParams,
    SelectItemsDataParams,
    SaveSummary,
)
from pyclarify.views.signals import (
    SelectSignalsParams,
    SaveSignalsParams,
)


class TestInclusionParams(unittest.TestCase):
    def setUp(self):
        with open("./tests/data/mock-models-request.json") as f:
            self.mock_data = json.load(f)
        self.generic_inclusion_params = self.mock_data["generic_inclusion_params"]

        self.notBefore = (
            (datetime.now() - timedelta(seconds=10)).astimezone().isoformat()
        )  # after
        self.before = datetime.now().astimezone().isoformat()

    # def test_generic_inclusion_params_creation(self):
    #     test_model = InclusionParams()
    #     test_model_default = InclusionParams(**self.generic_inclusion_params)

    #     self.assertEqual(test_model, test_model_default)

    #     # assert plain json
    #     self.assertEqual(test_model.json(), json.dumps(self.generic_inclusion_params))


    def test_select_signals_items_params(self):
        pass


class TestClarifyNamespaceParams(unittest.TestCase):
    def setUp(self):
        with open("./tests/data/mock-models-request.json") as f:
            self.mock_data = json.load(f)
        self.select_items_params = self.mock_data["select_items_params"]

    def test_select_items_params(self):
        # SelectItemsParams
        try:
            SelectItemsParams(**self.select_items_params)
        except ValidationError:
            self.fail("SelectItemsParams raised ValidationError unexpectedly!")

        try:
            SelectItemsParams(query= {"filter": {}}, include=[], groupIncludedByType = False)
        except ValidationError:
            self.fail("SelectItemsParams raised ValidationError unexpectedly!")

        # assert type validation
        with self.assertRaises(ValidationError):
            SelectItemsParams(items="string")
        with self.assertRaises(ValidationError):
            SelectItemsParams(data="string")


class TestIntegrationNamespaceParams(unittest.TestCase):
    def setUp(self):
        with open("./tests/data/mock-models-request.json") as f:
            self.mock_data = json.load(f)
        self.insert_params = self.mock_data["insert_params"]
        self.save_signals_params = self.mock_data["save_signals_params"]

    def test_insert_params(self):
        try:
            InsertParams(**self.insert_params)
        except ValidationError:
            self.fail("InsertParams raised ValidationError unexpectedly!")

        try:
            InsertParams(integration="c618rbfqfsj7mjkj0ss1", data={})
        except ValidationError:
            self.fail("InsertParams raised ValidationError unexpectedly!")

        # assert type validation
        with self.assertRaises(ValidationError):
            InsertParams(integration="string")
        with self.assertRaises(ValidationError):
            InsertParams(data="string")

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


class TestAdminNamespaceParams(unittest.TestCase):
    def setUp(self):
        with open("./tests/data/mock-models-request.json") as f:
            self.mock_data = json.load(f)
        self.publish_signals_params = self.mock_data["publish_signals_params"]
        self.select_signals_params = self.mock_data["select_signals_params"]

    def test_publish_signals_params(self):
        try:
            PublishSignalsParams(**self.publish_signals_params)
        except ValidationError:
            self.fail("InsertParams raised ValidationError unexpectedly!")

        try:
            PublishSignalsParams(
                integration="c618rbfqfsj7mjkj0ss1", itemsBySignal={}, createOnly=True
            )
        except ValidationError:
            self.fail("InsertParams raised ValidationError unexpectedly!")

        # assert type validation
        with self.assertRaises(ValidationError):
            PublishSignalsParams(integration="string")
        with self.assertRaises(ValidationError):
            PublishSignalsParams(data="string")

    def test_select_signals_params(self):
        try:
            SelectSignalsParams(**self.select_signals_params)
        except ValidationError:
            self.fail("SaveSignalsParams raised ValidationError unexpectedly!")

        try:
            SelectSignalsParams(
                integration="c618rbfqfsj7mjkj0ss1",
                query={"filter":{}},
            )
        except ValidationError:
            self.fail("SaveSignalsParams raised ValidationError unexpectedly!")

        # assert type validation
        with self.assertRaises(ValidationError):
            SelectSignalsParams(inputs="string")
        with self.assertRaises(ValidationError):
            SelectSignalsParams(query={})
        with self.assertRaises(ValidationError):
            SelectSignalsParams(integration="string")


class TestJSONRPCRequest(unittest.TestCase):
    def setUp(self):
        with open("./tests/data/mock-models-request.json") as f:
            self.mock_data = json.load(f)

    def test_creation(self):
        empty_request = JSONRPCRequest()
        self.assertEqual(
            empty_request.json(),
            json.dumps(self.mock_data["select_items"]),
        )

    def test_creation_insert(self):
        empty_request = JSONRPCRequest(method=ApiMethod.insert)
        self.assertEqual(
            empty_request.json(),
            json.dumps(self.mock_data["insert"]),
        )

    def test_creation_save(self):
        empty_request = JSONRPCRequest(method=ApiMethod.save_signals)
        self.assertEqual(
            empty_request.json(),
            json.dumps(self.mock_data["save_signals"]),
        )

    def test_creation_params_1(self):
        empty_request = JSONRPCRequest(params={})
        self.assertEqual(
            empty_request.json(),
            json.dumps(self.mock_data["select_items"]),
        )


class TestRequest(unittest.TestCase):
    def setUp(self):
        with open("./tests/data/mock-models-request.json") as f:
            self.mock_data = json.load(f)

        self.insert_params = self.mock_data["insert_params"]
        self.save_signals_params = self.mock_data["save_signals_params"]
        self.select_items_params = self.mock_data["select_items_params"]
        self.publish_signals_params = self.mock_data["publish_signals_params"]
        self.select_signals_params = self.mock_data["select_signals_params"]

    def test_insert_creation(self):
        try:
            req = Request(method=ApiMethod.insert, params=self.insert_params)
        except ValidationError:
            self.fail("Request raised ValidationError unexpectedly!")

        # assert correct params type
        self.assertIsInstance(req.params, InsertParams)

    def test_save_signals_creation(self):
        try:
            req = Request(
                method=ApiMethod.save_signals, params=self.save_signals_params
            )
        except ValidationError:
            self.fail("Request raised ValidationError unexpectedly!")

        # assert correct params type
        self.assertIsInstance(req.params, SaveSignalsParams)

    def test_select_items_creation(self):
        try:
            req = Request(
                method=ApiMethod.select_items, params=self.select_items_params
            )
        except ValidationError:
            self.fail("Request raised ValidationError unexpectedly!")

        # assert correct params type
        self.assertIsInstance(req.params, SelectItemsParams)

    def test_select_signals_creation(self):
        try:
            req = Request(
                method=ApiMethod.select_signals, params=self.select_signals_params
            )
        except ValidationError:
            self.fail("Request raised ValidationError unexpectedly!")

        # assert correct params type
        self.assertIsInstance(req.params, SelectSignalsParams)

    def test_publish_signals_creation(self):
        try:
            req = Request(
                method=ApiMethod.publish_signals, params=self.publish_signals_params
            )
        except ValidationError:
            self.fail("Request raised ValidationError unexpectedly!")

        # assert correct params type
        self.assertIsInstance(req.params, PublishSignalsParams)


if __name__ == "__main__":
    unittest.main()
