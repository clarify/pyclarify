import unittest
import sys
from pyclarify.query.query import ResourceQuery
from pyclarify.views.evaluate import GroupAggregation
from pydantic import ValidationError

sys.path.insert(1, "src/")

from pyclarify import ItemAggregation, Calculation
from pyclarify.fields.constraints import GroupAggregationMethod, TimeAggregationMethod

item1 = ItemAggregation(
    id="cbpmaq6rpn52969vfl00",
    aggregation="max",
    alias="i1"
)

item2 = ItemAggregation(
    id="cbpmaq6rpn52969vfl0g",
    aggregation="avg",
    alias="i2"
)

items = [
    item1, item2
]


step1 = Calculation(
    formula="i1 * i2",
    alias="c1"
)

step2 = Calculation(
    formula="gapfill(i1) / c1",
    alias="c2"
)

calculations = [step1, step2]

class TestItemAggregation(unittest.TestCase):

    def test_item_aggregation(self):
        item = ItemAggregation(
            id="cbpmaq6rpn52969vfl00",
            aggregation="max",
            state=1,
            lead=1,
            lag=1,
            alias="i1"
        )

        self.assertIsInstance(item, ItemAggregation)
        self.assertEqual(item.id, "cbpmaq6rpn52969vfl00")
        self.assertEqual(item.aggregation, TimeAggregationMethod.max)
        self.assertEqual(item.state, 1)
        self.assertEqual(item.lead, 1)
        self.assertEqual(item.lag, 1)
        self.assertEqual(item.alias, "i1")

        p = '{"id":"cbpmaq6rpn52969vfl00","aggregation":"max","state":1,"lead":1,"lag":1,"alias":"i1"}'
        self.assertEqual(item.model_dump_json(), p)

    def test_item_aggregation_invalid_id(self):
        with self.assertRaises(ValidationError):
            ItemAggregation(
                id="cbpmaq6rpn52969vfl00_!",
                aggregation="sum",
                state=1,
                lead=1,
                lag=1,
                alias="i1"
            )
    
    def test_item_aggregation_invalid_aggregation(self):
        with self.assertRaises(ValidationError):
            ItemAggregation(
                id="cbpmaq6rpn52969vfl00",
                aggregation="multiply",
                state=1,
                lead=1,
                lag=1,
                alias="i1"
            )

    def test_item_aggregation_invalid_state(self):
        with self.assertRaises(ValidationError):
            ItemAggregation(
                id="cbpmaq6rpn52969vfl00",
                aggregation="sum",
                state=-1,
                lead=1,
                lag=1,
                alias="i1"
            )
        
        with self.assertRaises(ValidationError):
            ItemAggregation(
                id="cbpmaq6rpn52969vfl00",
                aggregation="sum",
                state=10000,
                lead=1,
                lag=1,
                alias="i1"
            )

    def test_item_aggregation_invalid_lead(self):
        with self.assertRaises(ValidationError):
            ItemAggregation(
                id="cbpmaq6rpn52969vfl00",
                aggregation="sum",
                state=1,
                lead=-1001,
                lag=1,
                alias="i1"
            )
        
        with self.assertRaises(ValidationError):
            ItemAggregation(
                id="cbpmaq6rpn52969vfl00",
                aggregation="sum",
                state=1,
                lead=1001,
                lag=1,
                alias="i1"
            )

    def test_item_aggregation_invalid_lag(self):
        with self.assertRaises(ValidationError):
            ItemAggregation(
                id="cbpmaq6rpn52969vfl00",
                aggregation="sum",
                state=1,
                lead=1,
                lag=-1001,
                alias="i1"
            )
        
        with self.assertRaises(ValidationError):
            ItemAggregation(
                id="cbpmaq6rpn52969vfl00",
                aggregation="sum",
                state=1,
                lead=1,
                lag=1001,
                alias="i1"
            )

    def test_item_aggregation_invalid_alias(self):
        with self.assertRaises(ValidationError):
            ItemAggregation(
                id="cbpmaq6rpn52969vfl00",
                aggregation="sum",
                state=1,
                lead=1,
                lag=1,
                alias=""
            )

        with self.assertRaises(ValidationError):
            ItemAggregation(
                id="cbpmaq6rpn52969vfl00",
                aggregation="sum",
                state=1,
                lead=1,
                lag=1,
                alias="a_very_long_alias_that_cant_be_used_in_item_aggregation"
            )


class TestGroupAggregation(unittest.TestCase):
    
    def test_group_aggregation(self):
        group = GroupAggregation(
            query=ResourceQuery(filter={}),
            timeAggregation="max",
            groupAggregation="max",
            state=1,
            lead=1,
            lag=1,
            alias="g1"
        )

        self.assertIsInstance(group, GroupAggregation)
        self.assertEqual(group.query, ResourceQuery(filter={}))
        self.assertEqual(group.timeAggregation, TimeAggregationMethod.max)
        self.assertEqual(group.groupAggregation, GroupAggregationMethod.max)
        self.assertEqual(group.state, 1)
        self.assertEqual(group.lead, 1)
        self.assertEqual(group.lag, 1)
        self.assertEqual(group.alias, "g1")

        p = '{"query":{"filter":{},"sort":null,"limit":null,"skip":null,"total":null},"timeAggregation":"max","groupAggregation":"max","state":1,"lead":1,"lag":1,"alias":"g1"}'
        self.assertEqual(group.model_dump_json(), p)
    
    def test_group_aggregation_invalid_time_aggregation_method(self):
        with self.assertRaises(ValidationError):
         GroupAggregation(
            query=ResourceQuery(filter={}),
            timeAggregation="hey",
            groupAggregation="max",
            alias="g1"
        )
         
    def test_group_aggregation_invalid_group_aggregation_method(self):
        with self.assertRaises(ValidationError):
         GroupAggregation(
            query=ResourceQuery(filter={}),
            timeAggregation="max",
            groupAggregation="hey",
            alias="g1"
        )

    def test_group_aggregation_invalid_state(self):
        with self.assertRaises(ValidationError):
            GroupAggregation(
                query=ResourceQuery(filter={}),
                timeAggregation="sum",
                groupAggregation="sum",
                state=-1,
                lead=1,
                lag=1,
                alias="g1"
            )
        
        with self.assertRaises(ValidationError):
            GroupAggregation(
                query=ResourceQuery(filter={}),
                timeAggregation="sum",
                groupAggregation="sum",
                state=10000,
                lead=1,
                lag=1,
                alias="g1"
            )

    def test_group_aggregation_invalid_lead(self):
        with self.assertRaises(ValidationError):
            GroupAggregation(
                query=ResourceQuery(filter={}),
                timeAggregation="sum",
                groupAggregation="sum",
                state=1,
                lead=-1001,
                lag=1,
                alias="g1"
            )
        
        with self.assertRaises(ValidationError):
            GroupAggregation(
                query=ResourceQuery(filter={}),
                timeAggregation="sum",
                groupAggregation="sum",
                state=1,
                lead=1001,
                lag=1,
                alias="g1"
            )

    def test_group_aggregation_invalid_lag(self):
        with self.assertRaises(ValidationError):
            GroupAggregation(
                query=ResourceQuery(filter={}),
                timeAggregation="sum",
                groupAggregation="sum",
                state=1,
                lead=1,
                lag=-1001,
                alias="g1"
            )
        
        with self.assertRaises(ValidationError):
            GroupAggregation(
                query=ResourceQuery(filter={}),
                timeAggregation="sum",
                groupAggregation="sum",
                state=1,
                lead=1,
                lag=1001,
                alias="g1"
            )

    def test_group_aggregation_invalid_alias(self):
        with self.assertRaises(ValidationError):
            GroupAggregation(
                query=ResourceQuery(filter={}),
                timeAggregation="sum",
                groupAggregation="sum",
                state=1,
                lead=1,
                lag=1,
                alias=""
            )

        with self.assertRaises(ValidationError):
            GroupAggregation(
                query=ResourceQuery(filter={}),
                timeAggregation="sum",
                groupAggregation="sum",
                state=1,
                lead=1,
                lag=1,
                alias="a_very_long_alias_that_cant_be_used_in_group_aggregation"
            )


class TestItemCalculation(unittest.TestCase):

    def test_calculation(self):
        calc = Calculation(
            formula="i1 * i2",
            alias="c1"
        )

        self.assertIsInstance(calc, Calculation)
        self.assertEqual(calc.formula, "i1 * i2")
        self.assertEqual(calc.alias, "c1")

        p = '{"formula":"i1 * i2","alias":"c1"}'
        self.assertEqual(calc.model_dump_json(), p)

    def test_calculation_invalid_alias(self):
        with self.assertRaises(ValidationError):
            Calculation(
                formula="i1 * i2",
                alias=""
            )

        with self.assertRaises(ValidationError):
            Calculation(
                formula="i1 * i2",
                alias="averylongaliasthatcantbeusedincalculation"
            )

if __name__ == "__main__":
    unittest.main()
