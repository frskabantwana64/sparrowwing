import unittest

from src.allocation import Household, PurchaseLine, RequestLine, allocate_cycle


class AllocationTests(unittest.TestCase):
    def test_request_method_full_fill(self):
        households = [
            Household(id="h1", name="A", contribution_amount=100),
            Household(id="h2", name="B", contribution_amount=100),
        ]
        purchases = [PurchaseLine(id="p1", item_name="soap", qty_bought=10, unit_price=2.0)]
        requests = [
            RequestLine(household_id="h1", item_name="soap", qty_requested=4),
            RequestLine(household_id="h2", item_name="soap", qty_requested=6),
        ]

        allocations, settlements = allocate_cycle(households, purchases, requests, method="request")

        qty_by_hid = {a.household_id: a.qty_allocated for a in allocations}
        self.assertEqual(qty_by_hid["h1"], 4)
        self.assertEqual(qty_by_hid["h2"], 6)
        self.assertEqual(round(sum(s.allocated_cost for s in settlements), 2), 20.0)

    def test_request_method_shortage_proportional(self):
        households = [
            Household(id="h1", name="A", contribution_amount=100),
            Household(id="h2", name="B", contribution_amount=100),
            Household(id="h3", name="C", contribution_amount=100),
        ]
        purchases = [PurchaseLine(id="p1", item_name="rice", qty_bought=5, unit_price=10.0)]
        requests = [
            RequestLine(household_id="h1", item_name="rice", qty_requested=4),
            RequestLine(household_id="h2", item_name="rice", qty_requested=3),
            RequestLine(household_id="h3", item_name="rice", qty_requested=3),
        ]

        allocations, _ = allocate_cycle(households, purchases, requests, method="request")
        qty_total = sum(a.qty_allocated for a in allocations)
        self.assertEqual(qty_total, 5)

    def test_budget_method_uses_contributions(self):
        households = [
            Household(id="h1", name="A", contribution_amount=300),
            Household(id="h2", name="B", contribution_amount=200),
            Household(id="h3", name="C", contribution_amount=100),
        ]
        purchases = [PurchaseLine(id="p1", item_name="oil", qty_bought=6, unit_price=5.0)]

        allocations, settlements = allocate_cycle(households, purchases, [], method="budget")

        qty = {a.household_id: a.qty_allocated for a in allocations}
        self.assertEqual(qty["h1"], 3)
        self.assertEqual(qty["h2"], 2)
        self.assertEqual(qty["h3"], 1)
        self.assertAlmostEqual(sum(s.balance for s in settlements), 570.0)


if __name__ == "__main__":
    unittest.main()
