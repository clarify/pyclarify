"""
What PyClarify sends, checked against the documented contract of each API version.
"""

import unittest
from datetime import timedelta

import pyclarify
from pyclarify import Calculation, Client, Item, ItemAggregation, Signal
from pyclarify.__utils__.time import parse_datetime
from pyclarify.experimental import ExperimentalClient

from .contracts import violations
from .harness import (
    GTE,
    INPUT_ID,
    ITEM_ID,
    LT,
    MOCK_CREDENTIALS,
    MOCK_TOKEN,
    SDK_CALLS,
    SIGNAL_ID,
    TIMES,
    VersionedCase,
    for_each_api_version,
    group_aggregation,
)

INTEGRATION_ID = "01234567890123456789"  # from mock-clarify-credentials.json


class TestClientApiVersion(VersionedCase, unittest.TestCase):
    """How a Client chooses the API version it sends. Replies come from the 1.1 fixtures."""

    api_version = "1.1"
    __test__ = True

    def sent_version(self, client):
        self.server.requests.clear()
        client.select_items()
        return self.server.requests[0].headers["X-API-Version"]

    def test_defaults_to_the_sdk_default(self):
        client = Client(str(MOCK_CREDENTIALS))
        self.assertEqual(client.api_version, pyclarify.__API_version__)
        self.assertEqual(self.sent_version(client), pyclarify.__API_version__)

    def test_is_chosen_per_client(self):
        default, newer = Client(str(MOCK_CREDENTIALS)), Client(str(MOCK_CREDENTIALS), api_version="1.2")
        self.assertEqual(self.sent_version(newer), "1.2")
        self.assertEqual(self.sent_version(default), pyclarify.__API_version__)

    def test_must_be_a_string(self):
        with self.assertRaises(TypeError):
            Client(str(MOCK_CREDENTIALS), api_version=1.2)

    def pre_release_clients(self):
        """Clients for the 1.2 pre-releases, answered from the 1.2 fixtures."""
        self.server.api_version = "1.2"
        with self.assertWarns(DeprecationWarning):
            experimental = ExperimentalClient(str(MOCK_CREDENTIALS))
        return Client(str(MOCK_CREDENTIALS), api_version="1.2beta1"), experimental

    def test_experimental_client_is_deprecated_and_uses_the_1_2_pre_release(self):
        with self.assertWarns(DeprecationWarning):
            client = ExperimentalClient(str(MOCK_CREDENTIALS))
        self.assertEqual(client.api_version, "1.2alpha1")
        self.assertEqual(self.sent_version(client), "1.2alpha1")
        self.assertEqual(self.server.requests[0].headers["User-Agent"], f"PyClarify/{pyclarify.__version__}/experimental")

    def test_1_2_pre_releases_select_group_items_with_a_query(self):
        """1.2alpha1 and 1.2beta1 only accept the pre-1.2 shape, {"query": {"filter": ...}}."""
        item_filter = {"id": {"$in": [ITEM_ID]}}
        group = group_aggregation(item_filter, timeAggregation="avg", groupAggregation="sum", alias="g1")
        for client in self.pre_release_clients():
            with self.subTest(client.api_version):
                self.server.requests.clear()
                client.evaluate(rollup="PT1H", gte=GTE, lt=LT, groups=[group])
                [sent] = self.server.requests[0].params["groups"]
                self.assertEqual(sent.get("query"), {"filter": item_filter})
                self.assertNotIn("filter", sent)

    def test_1_2_pre_releases_use_their_connect_method_names(self):
        for client in self.pre_release_clients():
            with self.subTest(client.api_version):
                self.server.requests.clear()
                client.connect_signals(item=ITEM_ID, filter={"input": INPUT_ID})
                client.disconnect_signals(filter={"input": INPUT_ID})
                self.assertEqual(
                    [request.method for request in self.server.requests], ["admin.connectSignals", "admin.disconnectSignals"]
                )

    def test_1_2_pre_releases_get_data_frames_without_total(self):
        """1.2beta1 rejects query.total in clarify.dataFrame, even when it is false."""
        for client in self.pre_release_clients():
            with self.subTest(client.api_version):
                self.server.requests.clear()
                client.data_frame(gte=GTE, lt=LT)
                self.assertNotIn("total", self.server.requests[0].params["query"])

    def test_experimental_client_connects_signals_like_the_client(self):
        _, experimental = self.pre_release_clients()
        experimental.connect_signals(item=ITEM_ID, filter={"input": INPUT_ID}, dryrun=True)
        experimental.disconnect_signals(filter={"input": INPUT_ID}, dryrun=True)
        connect, disconnect = self.server.requests
        self.assertEqual((connect.params["item"], connect.params["dryRun"]), (ITEM_ID, True))
        self.assertEqual(connect.params["query"]["filter"], {"input": INPUT_ID})
        self.assertIs(disconnect.params["dryRun"], True)


@for_each_api_version
class Transport(VersionedCase):
    def test_every_method_sends_the_selected_api_version(self):
        for sdk_method in self.sdk_calls():
            with self.subTest(sdk_method):
                self.server.requests.clear()
                self.call(sdk_method)
                self.assertTrue(self.server.requests)
                for request in self.server.requests:
                    self.assertEqual(request.headers.get("X-API-Version"), self.api_version)

    def test_requests_identify_the_sdk_and_are_authorized(self):
        self.call("select_items")
        headers = self.server.requests[0].headers
        self.assertEqual(headers["User-Agent"], f"PyClarify/{pyclarify.__version__}")
        self.assertEqual(headers["Authorization"], f"Bearer {MOCK_TOKEN}")
        self.assertEqual(headers["content-type"], "application/json")

    def test_requests_go_to_the_rpc_endpoint_of_the_credentials(self):
        self.call("select_items")
        self.assertEqual(self.server.requests[0].url, "https://api.clarify.io/v1/rpc")

    def test_requests_are_json_rpc_2_calls(self):
        for sdk_method in self.sdk_calls():
            with self.subTest(sdk_method):
                self.server.requests.clear()
                self.call(sdk_method)
                body = self.server.requests[0].body
                self.assertEqual(body["jsonrpc"], "2.0")
                # A null or missing id makes the call a notification, which gets no result.
                self.assertIsNotNone(body.get("id"))
                self.assertIsInstance(body["params"], dict)


@for_each_api_version
class RequestContract(VersionedCase):
    """
    Each request must use the method name and parameters documented for the selected API
    version. Anything else works only while the server stays lenient about it, and that
    leniency is what can change between versions.
    """

    def assertMatchesContract(self, sdk_method, call=None):
        (call or SDK_CALLS[sdk_method])(self.client)
        self.assertTrue(self.server.requests, f"{sdk_method} sent no request")
        method = self.contract.methods[sdk_method]
        for request in self.server.requests:
            found = violations(request.body, method)
            if found:
                self.fail(f"{sdk_method} does not match the API {self.api_version} contract:\n  " + "\n  ".join(found))

    def test_insert(self):
        self.assertMatchesContract("insert")

    def test_save_signals(self):
        self.assertMatchesContract("save_signals")

    def test_publish_signals(self):
        self.assertMatchesContract("publish_signals")

    def test_select_signals(self):
        self.assertMatchesContract("select_signals")

    def test_select_items(self):
        self.assertMatchesContract("select_items")

    def test_data_frame(self):
        self.assertMatchesContract("data_frame")

    def test_evaluate(self):
        self.assertMatchesContract("evaluate")

    def test_evaluate_with_groups(self):
        if "groups" not in self.contract.features:
            self.skipTest(f"API {self.api_version} has no group aggregation")
        group = group_aggregation({}, timeAggregation="avg", groupAggregation="sum", alias="g1")
        self.assertMatchesContract("evaluate", lambda client: client.evaluate(rollup="PT1H", gte=GTE, lt=LT, groups=[group]))

    def test_connect_signals(self):
        if "connect_signals" not in self.contract.methods:
            self.skipTest(f"API {self.api_version} has no admin.signals.connect")
        self.assertMatchesContract("connect_signals")

    def test_disconnect_signals(self):
        if "disconnect_signals" not in self.contract.methods:
            self.skipTest(f"API {self.api_version} has no admin.signals.disconnect")
        self.assertMatchesContract("disconnect_signals")


@for_each_api_version
class RequestContent(VersionedCase):
    """Request details that must not change with the API version."""

    def sent_params(self, sdk_method):
        self.server.requests.clear()
        self.call(sdk_method)
        return self.server.requests[0].params

    def test_selection_format_is_explicit(self):
        """
        Responses are parsed assuming this format, so it must be requested explicitly rather
        than left to server defaults, which differ per method and may differ per version.
        """
        data_as_array = {"select_items": True, "select_signals": True, "data_frame": False, "evaluate": False}
        for sdk_method, expected in data_as_array.items():
            with self.subTest(sdk_method):
                sent = self.sent_params(sdk_method).get("format") or {}
                self.assertIs(sent.get("dataAsArray"), expected)
                self.assertIs(sent.get("groupIncludedByType"), True)

    def test_integration_defaults_to_the_credentials(self):
        methods = ("insert", "save_signals", "publish_signals", "select_signals", "connect_signals", "disconnect_signals")
        for sdk_method in (method for method in methods if method in self.contract.methods):
            with self.subTest(sdk_method):
                self.assertEqual(self.sent_params(sdk_method)["integration"], INTEGRATION_ID)

    def test_connect_signals_sends_the_item_query_and_dry_run(self):
        if "connect_signals" not in self.contract.methods:
            self.skipTest(f"API {self.api_version} has no admin.signals.connect")
        self.client.connect_signals(item=ITEM_ID, filter={"input": INPUT_ID}, limit=5, dry_run=True)
        params = self.server.requests[0].params
        self.assertEqual((params["item"], params["dryRun"]), (ITEM_ID, True))
        self.assertEqual((params["query"]["filter"], params["query"]["limit"]), ({"input": INPUT_ID}, 5))

    def test_connecting_signals_is_refused_without_api_support(self):
        if "connect_signals" in self.contract.methods:
            self.skipTest(f"API {self.api_version} can connect signals")
        for call in (
            lambda: self.client.connect_signals(item=ITEM_ID, filter={"input": INPUT_ID}),
            lambda: self.client.disconnect_signals(filter={"input": INPUT_ID}),
        ):
            with self.assertRaises(ValueError):
                call()
        self.assertEqual(self.server.requests, [], "a request was sent anyway")

    def test_time_window_is_sent_as_requested(self):
        for sdk_method in ("data_frame", "evaluate"):
            with self.subTest(sdk_method):
                times = self.sent_params(sdk_method)["data"]["filter"]["times"]
                self.assertEqual(parse_datetime(times["$gte"]), parse_datetime(GTE))
                self.assertEqual(parse_datetime(times["$lt"]), parse_datetime(LT))

    def test_rollup_is_sent_as_given(self):
        """
        Rollups are calendar durations: P1M is a calendar month, and with a time zone PT24H and
        P1D differ across DST changes. They must reach the API unchanged.
        """
        cases = (("PT5M", "PT5M"), ("PT24H", "PT24H"), ("P1M", "P1M"), ("window", "window"), (timedelta(days=1), "P1D"))
        for rollup, expected in cases:
            with self.subTest(rollup=rollup):
                self.server.requests.clear()
                self.client.data_frame(gte=GTE, lt=LT, rollup=rollup)
                self.assertEqual(self.server.requests[0].params["data"]["rollup"], expected)

    def test_explicit_none_works_like_leaving_the_argument_out(self):
        signal, item = Signal(name="A"), Item(name="A")
        calls = {
            "data_frame": ({"rollup": None, "window_size": None}, lambda c, **kw: c.data_frame(gte=GTE, lt=LT, **kw)),
            "evaluate": ({"window_size": None}, lambda c, **kw: c.evaluate(rollup="PT1H", gte=GTE, lt=LT, **kw)),
            "select_signals": ({"integration": None}, lambda c, **kw: c.select_signals(**kw)),
            "save_signals": ({"integration": None}, lambda c, **kw: c.save_signals(input_ids=[INPUT_ID], signals=[signal], **kw)),
            "publish_signals": ({"integration": None}, lambda c, **kw: c.publish_signals(signal_ids=[SIGNAL_ID], items=[item], **kw)),
        }
        for sdk_method, (nones, call) in calls.items():
            with self.subTest(sdk_method):
                self.server.requests.clear()
                call(self.client, **nones)
                call(self.client)
                with_none, without = self.server.requests
                self.assertEqual(with_none.params, without.params)
        # Without gte and lt the window is relative to now, so only check that None is accepted.
        self.client.data_frame(gte=None, lt=None)
        self.client.evaluate(rollup="PT1H", gte=None, lt=None)

    def test_insert_sends_the_data_frame(self):
        data = self.sent_params("insert")["data"]
        self.assertEqual(data["series"], {INPUT_ID: [1.0, None]})
        self.assertEqual([parse_datetime(t) for t in data["times"]], [parse_datetime(t) for t in TIMES])

    def test_save_signals_sends_only_the_given_signals(self):
        self.client.save_signals(input_ids=["input-a"], signals=[Signal(name="A")])
        self.client.save_signals(input_ids=["input-b"], signals=[Signal(name="B")])
        params = self.server.requests[1].params
        signals = next(params[name] for name in ("signalsByInput", "input", "inputs") if name in params)
        self.assertEqual(list(signals), ["input-b"], "save_signals re-sent signals from an earlier call")

    def test_publish_signals_sends_only_the_given_items(self):
        other_signal_id = "c618rbfqfsj7mjkj0ss2"
        self.client.publish_signals(signal_ids=[SIGNAL_ID], items=[Item(name="A")])
        self.client.publish_signals(signal_ids=[other_signal_id], items=[Item(name="B")])
        items = self.server.requests[1].params["itemsBySignal"]
        self.assertEqual(list(items), [other_signal_id], "publish_signals re-sent items from an earlier call")

    def test_evaluate_sends_items_calculations_and_series(self):
        self.client.evaluate(
            rollup="PT1H",
            gte=GTE,
            lt=LT,
            items=[ItemAggregation(id=ITEM_ID, aggregation="max", lag=1, alias="i1")],
            calculations=[Calculation(formula="i1 * 2", alias="c1")],
            series=["c1"],
        )
        params = self.server.requests[0].params
        [item] = params["items"]
        self.assertEqual(item["id"], ITEM_ID)
        self.assertEqual(item.get("timeAggregation", item.get("aggregation")), "max")
        self.assertEqual((item["lag"], item["alias"]), (1, "i1"))
        self.assertEqual(params["calculations"], [{"formula": "i1 * 2", "alias": "c1"}])
        self.assertEqual(params["data"]["filter"]["series"], {"$in": ["c1"]})
        self.assertEqual(params["data"]["rollup"], "PT1H")

    def test_evaluate_sends_groups(self):
        if "groups" not in self.contract.features:
            self.skipTest(f"API {self.api_version} has no group aggregation")
        item_filter = {"id": {"$in": [ITEM_ID]}}
        group = group_aggregation(item_filter, timeAggregation="avg", groupAggregation="sum", alias="g1")
        self.client.evaluate(rollup="PT1H", gte=GTE, lt=LT, groups=[group])
        [sent] = self.server.requests[0].params["groups"]
        self.assertEqual(sent.get("filter"), item_filter, f"API {self.api_version} selects group items with 'filter'")
        self.assertEqual((sent["timeAggregation"], sent["groupAggregation"], sent["alias"]), ("avg", "sum", "g1"))

    def test_evaluate_rejects_groups_without_api_support(self):
        if "groups" in self.contract.features:
            self.skipTest(f"API {self.api_version} has group aggregation")
        group = group_aggregation({}, timeAggregation="avg", groupAggregation="sum", alias="g1")
        with self.assertRaises(ValueError):
            self.client.evaluate(rollup="PT1H", gte=GTE, lt=LT, groups=[group])
        self.assertEqual(self.server.requests, [], "the request was sent anyway")

    def test_unset_sample_interval_and_gap_detection_are_sent_as_null(self):
        """As in 0.6. The API applies its defaults for null the same as for a missing value."""
        for sdk_method, key in (("save_signals", "signalsByInput"), ("publish_signals", "itemsBySignal")):
            with self.subTest(sdk_method):
                params = self.sent_params(sdk_method)
                resources = params.get(key) or params.get("inputs")
                for resource in resources.values():
                    self.assertIsNone(resource["sampleInterval"])
                    self.assertIsNone(resource["gapDetection"])

    def test_evaluate_sends_outside_points(self):
        if "outsidePoints" not in self.contract.features:
            self.skipTest(f"API {self.api_version} has no outsidePoints")
        self.client.evaluate(rollup="PT1H", gte=GTE, lt=LT, outsidePoints=True)
        self.assertIs(self.server.requests[0].params["data"]["outsidePoints"], True)
