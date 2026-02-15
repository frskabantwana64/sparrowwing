# Sparrowwing: Group Bulk-Buy & Split (MVP Foundation)

This repository contains a lightweight, implementation-ready foundation for a **3–5 household** bulk-buy and split workflow.

## Included in this commit

- A clear technical blueprint aligned to the provided PRD (`docs/mvp-plan.md`).
- A deterministic allocation engine reference implementation (`src/allocation.py`) with:
  - Request-based allocation (with proportional shortage handling)
  - Budget-proportional allocation (largest remainder rounding for integer units)
  - Settlement computation (owed/owes balances)
- Executable unit tests validating core allocation and settlement rules (`tests/test_allocation.py`).

## Quick start

Run tests:

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## Why this shape

The project is intentionally small and transparent so the splitting math is easy to audit and explain to households.
