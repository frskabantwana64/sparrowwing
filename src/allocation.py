from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Literal
import math


SplitMethod = Literal["request", "budget"]


@dataclass(frozen=True)
class Household:
    id: str
    name: str
    contribution_amount: float


@dataclass(frozen=True)
class RequestLine:
    household_id: str
    item_name: str
    qty_requested: int


@dataclass(frozen=True)
class PurchaseLine:
    id: str
    item_name: str
    qty_bought: int
    unit_price: float

    @property
    def total_price(self) -> float:
        return self.qty_bought * self.unit_price


@dataclass(frozen=True)
class AllocationLine:
    household_id: str
    purchase_line_id: str
    qty_allocated: int
    cost_allocated: float


@dataclass(frozen=True)
class Settlement:
    household_id: str
    contribution_amount: float
    allocated_cost: float
    balance: float


def _largest_remainder_allocation(total_units: int, weights: Dict[str, float]) -> Dict[str, int]:
    if total_units < 0:
        raise ValueError("total_units must be >= 0")

    keys = sorted(weights.keys())
    total_weight = sum(max(0.0, weights[k]) for k in keys)

    if total_units == 0 or total_weight <= 0:
        return {k: 0 for k in keys}

    raw_shares: Dict[str, float] = {
        k: (max(0.0, weights[k]) / total_weight) * total_units for k in keys
    }
    base_alloc: Dict[str, int] = {k: int(math.floor(raw_shares[k])) for k in keys}
    allocated = sum(base_alloc.values())
    remainder = total_units - allocated

    if remainder > 0:
        ranked = sorted(
            keys,
            key=lambda k: (raw_shares[k] - base_alloc[k], k),
            reverse=True,
        )
        for k in ranked[:remainder]:
            base_alloc[k] += 1

    return base_alloc


def _round2(v: float) -> float:
    return round(v + 1e-9, 2)


def _requests_by_household_for_item(
    requests: Iterable[RequestLine],
    item_name: str,
    household_ids: Iterable[str],
) -> Dict[str, int]:
    wanted = {hid: 0 for hid in household_ids}
    for r in requests:
        if r.item_name == item_name and r.household_id in wanted:
            wanted[r.household_id] += r.qty_requested
    return wanted


def allocate_cycle(
    households: List[Household],
    purchases: List[PurchaseLine],
    requests: List[RequestLine],
    method: SplitMethod = "request",
) -> tuple[List[AllocationLine], List[Settlement]]:
    if not households:
        raise ValueError("At least one household is required")

    household_ids = [h.id for h in households]
    contribution_map = {h.id: h.contribution_amount for h in households}

    allocations: List[AllocationLine] = []

    for p in purchases:
        if p.qty_bought < 0 or p.unit_price < 0:
            raise ValueError("Purchase quantities and prices must be non-negative")

        if method == "request":
            requested = _requests_by_household_for_item(requests, p.item_name, household_ids)
            total_requested = sum(requested.values())
            if total_requested <= 0:
                qty_alloc = _largest_remainder_allocation(
                    p.qty_bought, {hid: contribution_map[hid] for hid in household_ids}
                )
            elif p.qty_bought >= total_requested:
                qty_alloc = requested
            else:
                qty_alloc = _largest_remainder_allocation(
                    p.qty_bought,
                    {hid: float(requested[hid]) for hid in household_ids},
                )
        elif method == "budget":
            qty_alloc = _largest_remainder_allocation(
                p.qty_bought, {hid: contribution_map[hid] for hid in household_ids}
            )
        else:
            raise ValueError(f"Unsupported method: {method}")

        for hid in household_ids:
            qty = qty_alloc.get(hid, 0)
            cost = _round2(qty * p.unit_price)
            allocations.append(
                AllocationLine(
                    household_id=hid,
                    purchase_line_id=p.id,
                    qty_allocated=qty,
                    cost_allocated=cost,
                )
            )

    total_cost_by_household: Dict[str, float] = {hid: 0.0 for hid in household_ids}
    for a in allocations:
        total_cost_by_household[a.household_id] += a.cost_allocated

    settlements: List[Settlement] = []
    for h in households:
        allocated_cost = _round2(total_cost_by_household[h.id])
        balance = _round2(h.contribution_amount - allocated_cost)
        settlements.append(
            Settlement(
                household_id=h.id,
                contribution_amount=_round2(h.contribution_amount),
                allocated_cost=allocated_cost,
                balance=balance,
            )
        )

    return allocations, settlements
