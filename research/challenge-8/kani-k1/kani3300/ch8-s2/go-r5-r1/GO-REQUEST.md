# S2 R5-r1 — HOLD before final GO

Root chooses **(b), deterministic process test kept in Validate**. The workflow
runs `python3 -m unittest ... test_r5.py`, including
`ProcessTests.test_escaped_setsid_child_found_and_reaped`. The unchanged fixture
failed in the reviewer batch and once in isolation on an early orphan-list
snapshot; scoped diagnostics still observed/signalled/reaped the escaped child
and rejected its PGID. A bounded synchronization/post-cleanup assertion repair
is preferable to a known prebuild CI flake. The test remains in the suite.

Original13 has task `6d7c4739def196654459faf05b7e1c36ace03e93`: tiny test-only
repair plus necessary bindings, immutable `batch-r5-r1-stable/`, production
runtime/source/tool/order/resource caps unchanged. SAME14 then checks exact final
pins, preserved meaningful cleanup/controller coverage, allPASS final Validate
and >=1.5x host margin. No sleeps/retries/skips or weaker assertions.

Prior package `dc8d28b0117737e95ccc9b91eb470c1a3c42a635`, control
`d67bd1ecd555030c46a06b8462d0313ea416711a` and review
`2ed2c8ef2f6b9d6460494b85594e3a5f08387a7f` remain immutable; both01/02 CLOSED.
Root checked23reviewfiles/22hashes. Prior134PASS/409.026897886s is retained
alongside reviewer33PASS/1FAIL and repeatFAIL, without relabeling failed runs.
The old control is **not dispatch-ready under this root decision**.

**Conditional agreement:** one new R5 attempt after exact test-stable candidate
and independent delta APPROVE, final identity/margin checks and separate user
coordinator GO. Future trigger must be a same-tree sibling with sole parent
`9e14e033f9ee31522b571c127609dcdff76d230b`; future tree/head/run remain unknown.
Source `bd62e54df1b4749154790aa3db3cc7978f547f75`, stock
`0aac16ef62da9e9d5645782d458593e5d78143ba`, checkout7/5/2 and selected9/16/5 plus
deferredgeneral32/full11/20/6 remain fixed. No automatic rerun or new proof credit.

Owner ledger87885e4e73: item1 29/30, item2 10/17, total39/47. R5 would be11/17
and40/47 if counted; no reservation/accounting/CI/push action by root. This HOLD
will be finalized only after the exact repair/review. See structured JSON.
