# RESULT WRAPMORE — wrapper contracts on the two uncovered impls and N4 (phase D1)

Runtime Claude Code, owner k1-merge, branch `experiment/kani-k1-wrapmore-20261103` from 2104e7a596 (v6 tree d4ec476a7a).
Library: G1 `0bf64c1c32` (tree b9be6513e7), G2 `716e094b61` (tree **7cdb7ee5eb**): only `wrap.rs` + cfg-gated `mod more;`
and the new opt-in child `verify/wrap/more.rs`. Ordinary 202 unchanged; cfg-on 384 → 392 (exact +8 names, static gate).
Builds: G1 b896b36d SUCCESS 3/3 ($0.1890), G2 b814c784 SUCCESS 5/5 ($0.4185); own $0.6075 ≤ $1.95; no repair/retry.
Packet max RSS (kani-compiler) G1 1.91 / G2 2.16 GiB, wall 5:51 / 23:46. GCB e2-standard-4, controls on, jobs 1, uninit off, 10 min, Kani 9461e07a, check-tooling vs 30f77e85 ok, no OOM.
## Matrix: 6 impls × {N2, N4} — wrapper contract (PFC SUCCESS, real body, no stub) on concrete type/N
| Impl (smallsort.rs) | Domain → route | N2 | N4 |
|---|---|---|---|
| Stable blanket `default fn` | Cell<u8> → insertion | `wrap::stable_cell_n2` (v6) | `stable_cell_n4` ✔ |
| Stable `T: FreezeMarker` | u8 + caller scratch → general_with_scratch | `stable_freeze_byte_n2` ✔ | `stable_freeze_byte_n4` ✔ |
| Unstable blanket `default fn` | Cell<u8> → fallback insertion | `unstable_cell_n2` ✔ | `unstable_cell_n4` ✔ |
| Unstable `T: FreezeMarker` (forward) | u8 → FreezeTypeImpl | `wrap::unstable_byte_n2` (v6) | `unstable_byte_n4` ✔ |
| FreezeTypeImpl Copy | u8 → network | same row (v6) | same row ✔ |
| FreezeTypeImpl default | NonCopyU8 → general, scratch48 | `wrap::freeze_noncopy_n2` (v6) | `freeze_noncopy_n4` ✔ |
Contract: requires region (+ scratch ≥ len+16, disjoint, for Stable Freeze) and canonical fn pointer; modifies
input (+ scratch for Stable Freeze); ensures key-sorted and `old(count)==count` with an independent u8 probe. Backing
frame asserted (N2 backing4, N4 backing6). Stable Freeze rows also assert a scratch route witness (general route
only). Control `rejects_always_true_more`: FAILED, only `wrap canonical comparator required` @ wrap.rs:61, covers 2/2.
## VT and RSS (CBMC row peak, one PID per row, jobs 1)
| Row (`wrap::more::`) | VT s | checks | covers | RSS GiB |
|---|---:|---|---|---:|
| stable_freeze_byte_n2 | 202.3 | 0/518 | 9/9 | 0.79 |
| unstable_cell_n2 | 25.8 | 0/265 | 7/7 | 0.21 |
| stable_cell_n4_backing6 | 152.0 | 0/306 | 10/10 | 0.69 |
| unstable_byte_n4_backing6 | 91.0 | 0/487 | 8/8 | 0.69 |
| freeze_noncopy_n4_backing6 | 402.4 | 0/467 | 8/8 | 1.61 |
| stable_freeze_byte_n4_backing6 | 511.4 | 0/538 | 10/10 | 1.58 |
| unstable_cell_n4_backing6 | 84.4 | 0/271 | 8/8 | 0.67 |
## v7 candidates (≤ 300 s): stable_freeze_byte_n2, unstable_cell_n2, stable_cell_n4, unstable_byte_n4, unstable_cell_n4
(+ 3 v6 N2 rows already ordinary). Over 300 s, keep opt-in: freeze_noncopy_n4 (402 s), stable_freeze_byte_n4 (511 s).
## Still without contract, and why
- Other N (N0/N1/N3, N5..thresholds 16/32) and branches they select: network sort9/sort13/merge (N ≥ 9/18), general
  presorted 4/8 (N ≥ 8/16), FreezeTypeImpl Copy general (size > 8) / fallback and default fallback (size·48 > 4096) —
  not requested; general N4 already 400–511 s, so larger N needs a different (stubbed/compositional) strategy.
- Generic T / arbitrary FnMut, panicking or non-order comparators: guard admits only one pure canonical fn pointer.
- Stability (tie order), panic/unwind, uninit (checks off), Cell interior mutation by the comparator: not specified.
- Contracts are on cfg(kani) wrappers, not on the trait methods (K5); scratch of Stable Freeze is modifies, not framed.
