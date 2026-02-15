# MVP Technical Plan

## 1) Product scope (MVP)

This plan supports a single buy-cycle workflow:

1. Create cycle
2. Add households and contributions
3. Capture requested list items + priorities
4. Consolidate and shop (actual quantities and prices)
5. Allocate quantities and costs
6. Produce settlement and shareable summary

## 2) Core data structures

Minimal entities:

- `Household(id, name, contribution_amount, paid_status)`
- `BuyCycle(id, name, status, currency)`
- `ListItem(household_id, item_name, category, size, qty_requested, priority)`
- `PurchaseLine(id, item_name, qty_bought, unit_price, category, splittable)`
- `AllocationLine(household_id, purchase_line_id, qty_allocated, cost_allocated)`

## 3) Allocation engine rules

### Request-based allocation (default)

Per purchase line:

- If `qty_bought >= total_requested`: each household receives full requested quantity.
- If `qty_bought < total_requested`:
  - Compute proportional share: `qty_bought * request_i / total_requested`
  - Convert to integers with **largest remainder** method so total allocated equals bought quantity.
- Cost for line is allocated proportional to allocated quantity.

### Budget-proportional allocation

Per purchase line:

- Compute household budget share using contributions.
- Allocate integer quantities by largest remainder using those shares.
- Allocate costs proportionally to allocated quantity.

### Settlement

Per household:

- `balance = contribution_amount - allocated_cost_total`
- `balance > 0`: household is owed credit.
- `balance < 0`: household owes the group.
- Round household totals to 2 decimals at final totals.

## 4) Determinism and auditability

- Largest remainder tie-break: stable household ordering by `household_id`.
- Allocation outputs are reproducible from the same inputs.
- Snapshot final cycle state before close for audit.

## 5) API shape (suggested)

- `POST /cycles`
- `POST /cycles/{id}/households`
- `POST /cycles/{id}/requests`
- `POST /cycles/{id}/purchases`
- `POST /cycles/{id}/split` (returns allocation + settlement)
- `GET /cycles/{id}/export.csv`

## 6) UX notes

- Mobile-first forms with quick-add chips for common items.
- Shopping mode optimized for fast editing: qty and unit price inline.
- Split screen includes explainability panel:
  - method used
  - shortage handling
  - rounding notes

## 7) Acceptance checks

- Consolidation sums requested quantities by merged item key.
- Allocation totals must exactly match each purchase line's bought quantity.
- Sum of household allocated costs must equal total spend.
- Sum of settlement balances should equal zero (within rounding tolerance of 0.01).
