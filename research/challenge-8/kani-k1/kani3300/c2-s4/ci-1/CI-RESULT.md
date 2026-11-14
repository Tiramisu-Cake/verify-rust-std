# C2-S4 CI — coordinator (2026-11-14)

Baseline ad324418cd + baseline-tests.patch (tree 6bed3373b8, matches expected) + CI-only 51b1707e71, run 43621472749:
build PASS; composition capture (11 fresh invocations, jobs 1) exit 2 = UNBOUND_CAPTURE; mixed_root_oracle **MISMATCH**:
6 of 18 mixed-vs-own-isolated comparisons differ, all **additions only** (removed = 0) of `std::ptr::read::<u8>.safety_check.N`:
immutable_legal +6, immutable_hole_negative +9, unrelated_legal_after_cycle +3 — each in both all_A_then_B and all_B_then_A.
The other 12 comparisons are exact. → F7 accumulation reproduced fresh (not from historical C1b data).

Candidate 3b382c812a + CI-only db76eced8f, run 43621476331:
format PASS, build PASS, clippy PASS; unit delayed_cache::tests 6/0, delayed_scope_tests 2/0, immutable_allocations::tests 9/0;
composition capture exit 2, mixed_root_oracle **EXACT_MATCH**: 18/18 accepted, exact_match, no differences;
uninit suites: kani 24/0, expected 213/0 (2 ignored), ui 17/0, script 2/0, json oracles/mode ok,
composition (bound, stale C1b inventories) FAIL = known S5 debt; LLBC feature build (cprover+llbc) PASS.

Files: baseline-capture.json, candidate-capture.json (capture summaries). Unit membership/producer order: KANI_LOG debug was set;
not separately extracted here (order_credit/producer_order fields in capture.json).
=> S4 accepted at 3b382c812a: structural isolation, no T1b allowance needed for these roots.
