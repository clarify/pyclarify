"""
Live compatibility tests against a real Clarify organisation.

Skipped unless PYCLARIFY_LIVE_CREDENTIALS points to a clarify-credentials.json. The same calls
run under every version in PYCLARIFY_API_VERSIONS and the results are compared. This is how to
confirm the server behaviour that the offline suite can only assume.

    PYCLARIFY_LIVE_CREDENTIALS=clarify-credentials.json \\
        python -m unittest discover -s tests/api_versions -t tests -p "test_live.py" -v

Read-only by default. PYCLARIFY_LIVE_WRITE=1 also runs tests that save signals and insert data
in the credentials' integration, under input IDs starting with "pyclarify-api-compat/", and
publish them as hidden items.

With PYCLARIFY_RECORD_DIR=<dir>, the first successful response of each method per version is
saved as <dir>/<version>/<fixture>.json, to compare with the fixtures in fixtures/. Recorded
responses contain the organisation's data, so don't commit them as they are.

The versions under test must be enabled on the API behind the credentials; an unknown version
fails every call with HTTP 400 "Version matching X-API-Version header not found".
"""

import json
import os
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pyclarify import Calculation, DataFrame, Item, ItemAggregation, Signal
from pyclarify.fields.constraints import TimeAggregationMethod

from .contracts import CONTRACTS
from .harness import API_VERSIONS, FIXTURE_BY_METHOD, group_aggregation, make_client

CREDENTIALS = os.environ.get("PYCLARIFY_LIVE_CREDENTIALS")
WRITE = os.environ.get("PYCLARIFY_LIVE_WRITE") == "1"
RECORD_DIR = os.environ.get("PYCLARIFY_RECORD_DIR")

# A closed window in the past, so the data cannot change between the calls being compared.
LT = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
GTE = LT - timedelta(days=7)

UNSET = (None, timedelta(0))  # the API returns unset durations as PT0S
ITEM_DEFAULT_GAP_DETECTION = timedelta(hours=1, minutes=30)


def live_client(api_version):
    client = make_client(api_version, credentials=CREDENTIALS)
    if RECORD_DIR:
        record_responses(client, api_version)
    return client


def record_responses(client, api_version):
    """Save the first successful response of each method under RECORD_DIR, in the fixture format."""
    send = client.make_request

    def make_request(payload):
        response = send(payload)
        name = FIXTURE_BY_METHOD.get(json.loads(payload)["method"].lower())
        path = Path(RECORD_DIR) / api_version / f"{name}.json"
        if name and response.ok and not path.exists():
            body = response.json()
            if not body.get("error"):
                path.parent.mkdir(parents=True, exist_ok=True)
                provenance = f"Recorded from {client.base_url} with X-API-Version {api_version} on {datetime.now():%Y-%m-%d}."
                document = {"_provenance": provenance, "response": body}
                path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return response

    client.make_request = make_request


class LiveCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clients = {version: live_client(version) for version in API_VERSIONS}

    def result_everywhere(self, call):
        """Run `call(client)` under every API version and return the results by version."""
        results = {}
        for version, client in self.clients.items():
            response = call(client)
            self.assertIsNone(response.error, f"API {version}: {response.error}")
            results[version] = response.result
        return results

    def assertSameEverywhere(self, results, view):
        """`view(result)` must be equal for every API version."""
        (baseline, expected), *others = ((version, view(result)) for version, result in results.items())
        for version, actual in others:
            self.assertEqual(actual, expected, f"API {version} differs from API {baseline}")


@unittest.skipUnless(CREDENTIALS, "set PYCLARIFY_LIVE_CREDENTIALS to run tests against a real Clarify organisation")
class TestLiveReads(LiveCase):
    """The read methods must work, and return the same data, under every API version."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        version, client = next(iter(cls.clients.items()))
        response = client.select_items(filter={"valueType": "numeric"}, limit=5, sort=["id"])
        if response.error:
            raise AssertionError(f"API {version}: could not select items: {response.error}")
        cls.item_ids = [item.id for item in response.result.data or []]
        if len(cls.item_ids) < 2:
            raise unittest.SkipTest("the organisation needs at least two numeric items")

    def test_select_items(self):
        results = self.result_everywhere(lambda client: client.select_items(limit=50, sort=["id"]))
        self.assertSameEverywhere(results, lambda r: [(i.id, i.attributes.model_dump(mode="json")) for i in r.data])

    def test_select_signals(self):
        results = self.result_everywhere(lambda client: client.select_signals(limit=50, sort=["id"]))
        self.assertSameEverywhere(
            results,
            lambda r: [(s.id, s.attributes.model_dump(mode="json"), s.relationships.model_dump(mode="json")) for s in r.data],
        )

    def test_select_signals_with_items(self):
        """
        include=["item"] is documented for 1.1 and 1.2, but 1.1.2 and 1.2.0 rejected it on
        2026-09-29 with "no enum values registered".
        """
        results = self.result_everywhere(lambda client: client.select_signals(limit=50, sort=["id"], include=["item"]))
        self.assertSameEverywhere(results, lambda r: sorted(item.id for item in (r.included.items or [])) if r.included else [])

    def test_data_frame(self):
        item_filter = {"id": {"$in": self.item_ids}}
        # Client.data_frame rejects an explicit rollup=None, so raw data is requested by omitting it.
        for gte, extra in ((LT - timedelta(days=1), {}), (GTE, {"rollup": "PT1H"})):
            with self.subTest(**extra):
                results = self.result_everywhere(
                    lambda client: client.data_frame(filter=item_filter, gte=gte, lt=LT, **extra)
                )
                self.assertSameEverywhere(results, lambda r: (r.data.times, r.data.series))

    def test_evaluate(self):
        items = [ItemAggregation(id=item_id, aggregation="avg", alias=f"i{n}") for n, item_id in enumerate(self.item_ids[:2])]
        calculation = Calculation(formula="i0 + i1", alias="c1")
        results = self.result_everywhere(
            lambda client: client.evaluate(items=items, calculations=[calculation], rollup="PT1H", gte=GTE, lt=LT)
        )
        self.assertSameEverywhere(results, lambda r: (r.data.times, r.data.series))

    def test_every_time_aggregation_is_accepted(self):
        """Every aggregation name the SDK can send must be accepted by every API version."""
        for method in TimeAggregationMethod:
            state = 0 if method.value.startswith("state-") else None
            item = ItemAggregation(id=self.item_ids[0], aggregation=method, state=state, alias="a")
            for version, client in self.clients.items():
                with self.subTest(aggregation=method.value, api_version=version):
                    response = client.evaluate(items=[item], rollup="P1D", gte=GTE, lt=LT)
                    self.assertIsNone(response.error)

    def test_group_aggregation(self):
        versions = [version for version in self.clients if "groups" in CONTRACTS[version].features]
        if not versions:
            self.skipTest("no API version under test has group aggregation")
        item_filter = {"id": {"$in": self.item_ids[:2]}}
        group = group_aggregation(item_filter, timeAggregation="avg", groupAggregation="sum", alias="g1")
        for version in versions:
            with self.subTest(api_version=version):
                response = self.clients[version].evaluate(groups=[group], rollup="PT1H", gte=GTE, lt=LT)
                self.assertIsNone(response.error)

    def test_outside_points(self):
        versions = [version for version in self.clients if "outsidePoints" in CONTRACTS[version].features]
        if not versions:
            self.skipTest("no API version under test has outsidePoints")
        item = ItemAggregation(id=self.item_ids[0], aggregation="avg", alias="i0")
        for version in versions:
            with self.subTest(api_version=version):
                response = self.clients[version].evaluate(items=[item], rollup="PT1H", gte=GTE, lt=LT, outsidePoints=True)
                self.assertIsNone(response.error)


@unittest.skipUnless(CREDENTIALS and WRITE, "set PYCLARIFY_LIVE_CREDENTIALS and PYCLARIFY_LIVE_WRITE=1 to run live write tests")
class TestLiveWrites(LiveCase):
    """What the SDK writes under each API version must read back unchanged."""

    def input_id(self, version, name):
        return f"pyclarify-api-compat/{version}/{name}"

    def saved_signal(self, client, input_id, signal):
        # Pass signals_by_input explicitly: the list arguments share state between calls.
        response = client.save_signals(signals_by_input={input_id: signal})
        self.assertIsNone(response.error)
        response = client.select_signals(filter={"input": input_id}, limit=1)
        self.assertIsNone(response.error)
        self.assertEqual(len(response.result.data), 1, f"signal {input_id} was not found after saving it")
        return response.result.data[0]

    def test_signal_metadata_round_trips(self):
        signal = Signal(
            name="PyClarify API compatibility",
            description="Written by tests/api_versions/test_live.py.",
            labels={"source": ["pyclarify-api-compat"]},
            engUnit="°C",
            sampleInterval="PT1M",
            gapDetection="PT10M",
        )
        for version, client in self.clients.items():
            with self.subTest(api_version=version):
                saved = self.saved_signal(client, self.input_id(version, "metadata"), signal).attributes
                for key, value in signal.model_dump(exclude={"annotations"}).items():
                    self.assertEqual(getattr(saved, key), value, key)

    def test_unset_gap_detection_gets_the_api_default(self):
        """
        The SDK sends null for an unset gapDetection. Signals keep it unset. Items get the API's
        default, which Clarify is changing from unset (40 days) to PT1H30M with API 1.2; dev had
        the new default for API 1.1 too on 2026-09-30.
        """
        for version, client in self.clients.items():
            with self.subTest(api_version=version):
                signal = self.saved_signal(
                    client, self.input_id(version, "default-gap-detection"), Signal(name="PyClarify default gap detection")
                )
                self.assertIn(signal.attributes.gapDetection, UNSET, f"API {version} stored signal gapDetection")
                item = Item(name=f"PyClarify default gap detection {version}", visible=False)
                response = client.publish_signals(items_by_signal={signal.id: item})
                self.assertIsNone(response.error)
                item_id = response.result.itemsBySignal[signal.id].id
                response = client.select_items(filter={"id": item_id}, limit=1)
                self.assertIsNone(response.error)
                attributes = response.result.data[0].attributes
                self.assertIn(attributes.gapDetection, (*UNSET, ITEM_DEFAULT_GAP_DETECTION), f"API {version} item gapDetection")
                self.assertIn(attributes.sampleInterval, UNSET, f"API {version} item sampleInterval")

    def read_data(self, client, item_id, gte, lt, timeout=60):
        """Inserted data takes a while to become readable, so poll until it shows up."""
        deadline = time.monotonic() + timeout
        while True:
            response = client.data_frame(filter={"id": item_id}, gte=gte, lt=lt)
            self.assertIsNone(response.error)
            if response.result.data.times or time.monotonic() > deadline:
                return response.result.data
            time.sleep(5)

    def test_inserted_data_reads_back(self):
        times = [LT - timedelta(hours=3), LT - timedelta(hours=2), LT - timedelta(hours=1)]
        values = [1.0, 2.0, 3.0]
        for version, client in self.clients.items():
            with self.subTest(api_version=version):
                input_id = self.input_id(version, "data")
                response = client.insert(DataFrame(series={input_id: values}, times=times))
                self.assertIsNone(response.error)
                signal_id = response.result.signalsByInput[input_id].id
                item = Item(name=f"PyClarify API compatibility {version}", visible=False)
                response = client.publish_signals(items_by_signal={signal_id: item})
                self.assertIsNone(response.error)
                item_id = response.result.itemsBySignal[signal_id].id
                data = self.read_data(client, item_id, gte=times[0], lt=LT)
                self.assertEqual(data.times, times)
                self.assertEqual(data.series[item_id], values)
