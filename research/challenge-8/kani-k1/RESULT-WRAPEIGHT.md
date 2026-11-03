# RESULT WRAPEIGHT — wrapper contracts at N8/N9 on the cheap N4 routes (phase D1)

Runtime Claude Code, owner k1-merge, branch `experiment/kani-k1-wrapeight-20261103` from e8e238db9d (v6 tree d4ec476a7a).
Library: WRAPMORE cherry-picks 0fede6d2f9/46464f84ce (tree 7cdb7ee5eb = WRAPMORE G2) + `76219f4b21` (tree **49e5af24f0**),
only appended to opt-in `verify/wrap/more.rs`. Ordinary 202 / ordinary-PFC 36 unchanged; cfg-on 384 → 392 → 396 (exact +4).
Build 5e0d1e04 ([receipt](wrapeight/g1.result.md)), GO e7e2b1390a; own cost $0.7155 ≤ $1.00; no repair/retry; check-tooling ok.
GCB e2-standard-4, controls on, jobs 1, uninit off, 10 min/row, Kani 9461e07a; no smallsort warnings; no OOM.
## Rows (`wrap::more::`)
No failed check and no counterexample reported (terse output: only `CBMC timed out`); symex/solver split UNKNOWN.

| Root | Status | VT s | checks | covers | CBMC RSS GiB |
|---|---|---|---|---|---:|
| stable_cell_n8_backing10 | TIMEOUT | > 600 | n/a | n/a (gate 10) | 2.09 |
| unstable_cell_n8_backing10 | TIMEOUT | > 600 | n/a | n/a (gate 8) | 2.14 |
| unstable_byte_n8_backing10 | TIMEOUT | > 600 | n/a | n/a (gate 8) | 2.02 |
| unstable_byte_n9_backing11 | TIMEOUT | > 600 | n/a | n/a (gate 8) | 4.45 |
## Matrix impl × N — wrapper contract (PFC SUCCESS, real body, no stub); VT s
| Impl (smallsort.rs) | Domain → route | N2 | N4 | N8 | N9 |
|---|---|---|---|---|---|
| Stable blanket `default fn` | Cell<u8> → insertion | v6 ✔ | ✔ 152 | TIMEOUT | — |
| Stable `T: FreezeMarker` | u8 + scratch → general | ✔ 202 | ✔ 511 | not run | — |
| Unstable blanket `default fn` | Cell<u8> → fallback | ✔ 26 | ✔ 84 | TIMEOUT | — |
| Unstable Freeze → FreezeTypeImpl Copy | u8 → network | v6 ✔ | ✔ 91 | TIMEOUT | TIMEOUT |
| FreezeTypeImpl default | NonCopyU8 → general | v6 ✔ | ✔ 402 | not run | — |
## v7 candidates
None from WRAPEIGHT (0 SUCCESS). The ≤ 300 s N4 set from WRAPMORE stays as is (stable_cell, unstable_byte, unstable_cell).
At N8 the monolithic wrapper PFC on the real body exceeds 10 min on every cheap route (N4 84–152 s ⇒ > 4–7×); larger N
needs a split or compositional strategy, not a longer timeout here.
