"""
Responses from a newer API version can contain fields and enum values that PyClarify does not
know yet. Reading them must not fail, or every additive change on the server breaks the SDK.
"""

from pydantic import ValidationError

from .harness import VersionedCase, for_each_api_version

FIRST = object()  # path step: the first key of a mapping
MISSING = object()  # value: remove the key instead of setting it
NEW_VALUE = "added-in-a-later-version"


def describe(error, key):
    """The deepest validation errors about `key`, without pydantic's union member names."""
    related = [e for e in error.errors() if key in map(str, e["loc"])] or error.errors()
    deepest = max(len(e["loc"]) for e in related)
    lines = []
    for e in related:
        if len(e["loc"]) == deepest:
            loc = ".".join(str(part) for part in e["loc"] if not str(part)[:1].isupper())
            lines.append(f"{loc}: {e['msg']}")
    return "\n  ".join(dict.fromkeys(lines))


@for_each_api_version
class AdditiveResponseChanges(VersionedCase):
    def assertTolerates(self, sdk_method, path, key, value=NEW_VALUE, fixture=None):
        """Call `sdk_method` with its fixture changed so that <path>.<key> = value (or is removed)."""
        response = self.fixture(fixture or sdk_method)
        target = response
        for step in path:
            target = target[next(iter(target))] if step is FIRST else target[step]
        if value is MISSING:
            del target[key]
        else:
            target[key] = value
        self.server.reply_with(response)
        where = ".".join("<first>" if step is FIRST else str(step) for step in (*path, key))
        change = f"no {where}" if value is MISSING else f"{where} = {value!r}"
        try:
            result = self.call(sdk_method)
        except ValidationError as error:
            self.fail(f"{sdk_method} raises when the response has {change}:\n  {describe(error, key)}")
        if response.get("error"):
            self.assertIsNotNone(result.error)
        else:
            self.assertIsNone(result.error)
            self.assertIsNotNone(result.result)

    # New fields

    def test_new_item_attribute(self):
        self.assertTolerates("select_items", ("result", "data", 0, "attributes"), "newAttribute")

    def test_new_item_resource_field(self):
        self.assertTolerates("select_items", ("result", "data", 0), "newField")

    def test_new_resource_meta_field(self):
        self.assertTolerates("select_items", ("result", "data", 0, "meta"), "newField")

    def test_new_selection_meta_field(self):
        self.assertTolerates("select_items", ("result", "meta"), "newField")

    def test_new_selection_field(self):
        self.assertTolerates("select_items", ("result",), "newField")

    def test_new_included_resource_type_for_items(self):
        self.assertTolerates("select_items", ("result",), "included", {"newResourceType": []})

    def test_new_signal_attribute(self):
        self.assertTolerates("select_signals", ("result", "data", 0, "attributes"), "newAttribute")

    def test_new_signal_relationship(self):
        self.assertTolerates("select_signals", ("result", "data", 0, "relationships"), "newRelationship", {"data": None})

    def test_new_included_resource_type_for_signals(self):
        self.assertTolerates("select_signals", ("result", "included"), "newResourceType", [])

    def test_new_attribute_on_included_item(self):
        self.assertTolerates("select_signals", ("result", "included", "items", 0, "attributes"), "newAttribute")

    def test_new_data_frame_field(self):
        self.assertTolerates("data_frame", ("result", "data"), "newField")

    def test_new_evaluate_data_frame_field(self):
        self.assertTolerates("evaluate", ("result", "data"), "newField")

    def test_new_insert_result_field(self):
        self.assertTolerates("insert", ("result",), "newField")

    def test_new_insert_summary_field(self):
        self.assertTolerates("insert", ("result", "signalsByInput", FIRST), "newField")

    def test_new_save_signals_result_field(self):
        self.assertTolerates("save_signals", ("result",), "newField")

    def test_new_save_signals_summary_field(self):
        self.assertTolerates("save_signals", ("result", "signalsByInput", FIRST), "newField")

    def test_new_publish_signals_result_field(self):
        self.assertTolerates("publish_signals", ("result",), "newField")

    def test_new_publish_signals_summary_field(self):
        self.assertTolerates("publish_signals", ("result", "itemsBySignal", FIRST), "newField")

    def test_new_error_data_field(self):
        self.assertTolerates("select_items", ("error", "data"), "newField", fixture="error")

    # Optional fields

    def test_resource_meta_without_hash_fields(self):
        """API 1.2 only returns the hash fields when format.includeResourceHashFields applies."""
        self.assertTolerates("select_items", ("result", "data", 0, "meta"), "attributesHash", MISSING)
        self.assertTolerates("select_signals", ("result", "data", 0, "meta"), "relationshipsHash", MISSING)

    # New enum values

    def test_new_item_value_type(self):
        self.assertTolerates("select_items", ("result", "data", 0, "attributes"), "valueType", "new-value-type")

    def test_new_signal_source_type(self):
        self.assertTolerates("select_signals", ("result", "data", 0, "attributes"), "sourceType", "new-source-type")
