# Gate B (SmallSort replay on C1 1658f4cad) — run 43533328479

2026-11-14, coordinator. Overlay ci/kani3300-replay-c1-w15 @ ac49cf8f62 (std 70ba5befc6, tree 6ea9d3425f).
Harness preparation, std build and Kani runs completed in all 12 rows; outcomes below are from per-row stdout/receipt
artifacts (only stdout/stderr/receipt kept, coordinator scratchpad).

| Row | Result | Failures (complete set) |
| --- | --- | --- |
| 6 × OFF | PASS (expected) | — |
| raw-legal-on | FAILED, 1 of 387 | `select_unpredictable` Unimplemented (hint.rs:871, `<*const u64>`) |
| raw-negative-on | FAILED, 2 of 387 | **intended** uninit read smallsort.rs:751 (`sort4_stable` safety_check.1) + same `select_unpredictable` |
| sort8-boundary-on | FAILED, 1 of 589 | `select_unpredictable` |
| sort4-pfc-on | FAILED, 1 of 761 | fn-item comparator through `FnMut::call_mut` (function.rs:166) unsupported |
| merge-raw-pfc-on | FAILED, 1 of 573 | same fn-item comparator class |
| merge-profile-pfc-on | FAILED, 1 of 1027 | "checks across calls through function pointers" (function.rs:166) |

Reading:
- No false uninit finding: every ON row has exactly the unsupported construct(s); all other checks SUCCESS.
- The negative control is discriminating: the intended source[1] read at smallsort.rs:751 is reported.
- Two previously known, never-implemented boundaries block positive ON evidence:
  U7/SEL0 `select_unpredictable` (design `kani3300/sel0/DESIGN-SELECT.md`, SEL1 not done) and U4 fn-pointer / fn-item
  comparator calls. The Gate B package expected SUCCESS for legal ON rows without accounting for either.
- Not a harness defect. Gate B is BLOCKED on scope, not GO. Decision (SEL1/fn-pointer in Part 1 vs declared boundary)
  goes to owner + planner; no new CI until then.
