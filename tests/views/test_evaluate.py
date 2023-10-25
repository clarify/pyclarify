import unittest
import sys
import json
from pydantic.error_wrappers import ValidationError

sys.path.insert(1, "src/")

from pyclarify import ItemAggregation, Calculation
from pyclarify.fields.constraints import DataAggregation

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
        self.assertEqual(item.aggregation, DataAggregation.max)
        self.assertEqual(item.state, 1)
        self.assertEqual(item.lead, 1)
        self.assertEqual(item.lag, 1)
        self.assertEqual(item.alias, "i1")

        p = '{"id": "cbpmaq6rpn52969vfl00", "aggregation": "max", "state": 1, "lead": 1, "lag": 1, "alias": "i1"}'
        self.assertEquals(item.json(), p)

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


class TestItemCalculation(unittest.TestCase):

    def test_calculation(self):
        calc = Calculation(
            formula="i1 * i2",
            alias="c1"
        )

        self.assertIsInstance(calc, Calculation)
        self.assertEqual(calc.formula, "i1 * i2")
        self.assertEqual(calc.alias, "c1")

        p = '{"formula": "i1 * i2", "alias": "c1"}'
        self.assertEquals(calc.json(), p)

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
