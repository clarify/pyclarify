"""
How PyClarify splits large requests, checked against the documented limits of each API
version: resources per call and the longest time window per call.
"""

import copy
from datetime import timedelta, timezone

from pyclarify import ItemAggregation
from pyclarify.__utils__.time import parse_datetime

from .harness import ITEM_ID, VersionedCase, for_each_api_version

START = parse_datetime("2024-01-01T00:00:00Z")


def utc(time):
    return time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def windows(gte, lt, size):
    """The windows [gte, lt) should be split into when each may be at most `size` long."""
    result, start = [], gte
    while lt - start > size:
        result.append((utc(start), utc(start + size)))
        start += size
    result.append((utc(start), utc(lt)))
    return result


@for_each_api_version
class Pagination(VersionedCase):
    def serve_resources(self, sdk_method, total):
        """Serve `total` resources, honouring query.skip and query.limit like the API does."""
        response = self.fixture(sdk_method)
        template = response["result"]["data"][0]
        response["result"].pop("included", None)

        def handler(body):
            query = body["params"]["query"]
            count = max(0, min(query["limit"], total - query["skip"]))
            page = copy.deepcopy(response)
            page["result"]["data"] = [dict(template, id=f"{query['skip'] + n:020d}") for n in range(count)]
            return page

        self.server.handler = handler

    def serve_frames(self, sdk_method="data_frame", items=1):
        """Serve one data point per item and time window, for `items` items in total."""
        response = self.fixture(sdk_method)
        response["result"].pop("included", None)

        def handler(body):
            params = body["params"]
            query = params.get("query") or {"skip": 0, "limit": items}
            count = max(0, min(query["limit"], items - query["skip"]))
            page = copy.deepcopy(response)
            page["result"]["data"] = {
                "times": [params["data"]["filter"]["times"]["$gte"]],
                "series": {f"item-{query['skip'] + n}": [1.0] for n in range(count)},
            }
            return page

        self.server.handler = handler

    def sent_pages(self):
        return [(r.params["query"]["skip"], r.params["query"]["limit"]) for r in self.server.requests]

    def sent_windows(self):
        times = [r.params["data"]["filter"]["times"] for r in self.server.requests]
        return [(utc(parse_datetime(t["$gte"])), utc(parse_datetime(t["$lt"]))) for t in times]

    # Resources per call

    def test_select_items_within_one_page(self):
        self.serve_resources("select_items", total=5)
        response = self.client.select_items(limit=5)
        self.assertEqual(self.sent_pages(), [(0, 5)])
        self.assertEqual(len(response.result.data), 5)

    def test_select_items_beyond_one_page(self):
        per_call = self.contract.limits.select_items
        self.serve_resources("select_items", total=per_call + 100)
        response = self.client.select_items(limit=per_call + 100)
        self.assertEqual(self.sent_pages(), [(0, per_call), (per_call, 100)])
        self.assertEqual(len(response.result.data), per_call + 100)

    def test_select_items_stops_when_the_server_runs_out(self):
        per_call = self.contract.limits.select_items
        self.serve_resources("select_items", total=per_call + 100)
        response = self.client.select_items(limit=3 * per_call)
        self.assertEqual(self.sent_pages(), [(0, per_call), (per_call, per_call)])
        self.assertEqual(len(response.result.data), per_call + 100)

    def test_select_signals_beyond_one_page(self):
        per_call = self.contract.limits.select_signals
        self.serve_resources("select_signals", total=per_call + 100)
        response = self.client.select_signals(limit=per_call + 100)
        self.assertEqual(self.sent_pages(), [(0, per_call), (per_call, 100)])
        self.assertEqual(len(response.result.data), per_call + 100)

    def test_data_frame_pages_items_without_repeating_requests(self):
        per_call = self.contract.limits.data_frame
        self.serve_frames(items=2 * per_call)
        response = self.client.data_frame(limit=2 * per_call, gte=START, lt=START + timedelta(days=1))
        self.assertEqual(self.sent_pages(), [(0, per_call), (per_call, per_call)])
        self.assertEqual(len(response.result.data.series), 2 * per_call)

    # Time window per call

    def test_data_frame_splits_raw_data_into_windows(self):
        size = self.contract.limits.raw_window
        lt = START + 2 * size + timedelta(days=5)
        self.serve_frames()
        self.client.data_frame(gte=START, lt=lt)
        self.assertEqual(self.sent_windows(), windows(START, lt, size))

    def test_data_frame_rollup_splits_into_rollup_windows(self):
        size = self.contract.limits.rollup_window
        lt = START + size + timedelta(days=10)
        self.serve_frames()
        self.client.data_frame(gte=START, lt=lt, rollup="PT1H")
        self.assertEqual(self.sent_windows(), windows(START, lt, size))

    def test_data_frame_rollup_of_one_minute_uses_rollup_windows(self):
        """The longer window applies from a rollup of PT1M and up."""
        lt = START + self.contract.limits.raw_window + timedelta(days=5)
        self.serve_frames()
        self.client.data_frame(gte=START, lt=lt, rollup="PT1M")
        self.assertEqual(self.sent_windows(), windows(START, lt, self.contract.limits.rollup_window))

    def test_data_frame_rollup_window_is_one_request(self):
        lt = START + timedelta(days=1000)
        self.serve_frames()
        self.client.data_frame(gte=START, lt=lt, rollup="window")
        self.assertEqual(self.sent_windows(), [(utc(START), utc(lt))])

    def test_data_frame_window_size_overrides_the_api_limit(self):
        lt = START + timedelta(days=3)
        self.serve_frames()
        self.client.data_frame(gte=START, lt=lt, window_size="P1D")
        self.assertEqual(self.sent_windows(), windows(START, lt, timedelta(days=1)))

    def test_data_frame_daily_rollup_uses_daily_windows(self):
        size = self.contract.limits.daily_rollup_window
        lt = START + size + timedelta(days=10)
        self.serve_frames()
        self.client.data_frame(gte=START, lt=lt, rollup="P1D")
        self.assertEqual(self.sent_windows(), windows(START, lt, size))

    def test_data_frame_monthly_rollup_uses_monthly_windows(self):
        size = self.contract.limits.data_frame_monthly_rollup_window
        lt = START + size + timedelta(days=10)
        for rollup in ("P30D", "P1Y"):
            with self.subTest(rollup=rollup):
                self.server.requests.clear()
                self.serve_frames()
                self.client.data_frame(gte=START, lt=lt, rollup=rollup)
                self.assertEqual(self.sent_windows(), windows(START, lt, size))

    def test_data_frame_calendar_month_rollup_uses_daily_windows(self):
        """A calendar month can be 28 days, shorter than the P30D the monthly window needs."""
        size = self.contract.limits.daily_rollup_window
        lt = START + size + timedelta(days=10)
        self.serve_frames()
        self.client.data_frame(gte=START, lt=lt, rollup="P1M")
        self.assertEqual(self.sent_windows(), windows(START, lt, size))

    def test_evaluate_splits_into_rollup_windows(self):
        size = self.contract.limits.rollup_window
        lt = START + size + timedelta(days=10)
        self.serve_frames("evaluate")
        item = ItemAggregation(id=ITEM_ID, aggregation="avg", alias="i1")
        self.client.evaluate(rollup="PT1H", gte=START, lt=lt, items=[item])
        self.assertEqual(self.sent_windows(), windows(START, lt, size))

    def test_evaluate_monthly_rollup_uses_daily_windows(self):
        """clarify.evaluate has no longer window for monthly rollups."""
        size = self.contract.limits.daily_rollup_window
        lt = START + size + timedelta(days=10)
        self.serve_frames("evaluate")
        item = ItemAggregation(id=ITEM_ID, aggregation="avg", alias="i1")
        self.client.evaluate(rollup="P30D", gte=START, lt=lt, items=[item])
        self.assertEqual(self.sent_windows(), windows(START, lt, size))
