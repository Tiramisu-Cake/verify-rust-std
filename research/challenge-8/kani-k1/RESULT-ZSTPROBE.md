# RESULT ZSTPROBE — stable unit-ZST pointer checks: any `read_volatile::<()>` fails in Kani; `zst_aware_less` root SUCCESS
GO debceddeba (coordinator). Build 8922abbc-a604-46ce-adee-fa919ada629b @debceddeba, k1-standard4, kind diagnostic,
request zstprobe-diag-zst-dispatch-volatile-20261103 (sha256 6a1d2d15…ad09), controls on, jobs 1, uninit off, 10 min/row;
Kani 9461e07a; check-tooling vs e8e238db9d: pool, lane files, 6 bound files ok. Build FAILURE = Kani exit 1 (3 FAILED rows),
not a setup failure: compile ok, all 4 rows reported. Compile warnings: none pointing at smallsort sources (log-grep).
| # | Root (`verify::network::zstprobe::`) | Status | VT s | failed/total (unreach.) | covers | failed checks (terse, no location) |
|---|---|---|---:|---|---|---|
| 1 | zst_stable_dispatch_aware_n0_1_2_7_8_15_16_17_31_32 | SUCCESS | 194.8 | 0/391 (5) | 11/11 | — |
| 2 | zst_stable_dispatch_volatile_n2 | FAILED | 1.2 | 4/356 (12) | 2/2 | pointer NULL / invalid / outside object bounds / invalid integer address |
| 3 | zst_read_volatile_dangling | FAILED | 0.07 | 5/32 (2) | 1/1 | pointer NULL / deallocated dynamic object / dead object / outside object bounds / invalid integer address |
| 4 | zst_read_volatile_local | FAILED | 0.06 | 4/16 (2) | 1/1 | pointer NULL / invalid / outside object bounds / invalid integer address |
## Classification: (c) — artifact pattern, but wider than (a): the control (4) fails too
- Root 1 changes only the comparator and drops the original's 4/391 to 0/391 (same total, covers 11/11): the
  failures come from `volatile_reading_less`, not from `core`'s stable dispatch.
- Root 2 reproduces the SAFETYGAPS set exactly (same four descriptions) at N2 alone: the shortest path with comparisons
  (one `merge_up` + one `merge_down` on scratch-derived references) suffices.
- Root 4: `read_volatile(&x)` with `x: ()` a live local — valid in Rust — gets the same four checks. Root 3 (dangling,
  non-null aligned — also valid for a zero-byte read) fails with the dead/deallocated variants. So Kani 9461e07a flags
  every volatile unit read regardless of pointer origin; not a dangling-pointer or scratch-specific effect.
- Not determinable from terse output: whether the checks come from `read_volatile`'s `#[safety::requires(
  can_dereference(src))]` or from the `volatile_load` codegen. Peak CBMC 3.30 GiB (root 1); OOM none_seen.
## Fixed-root candidate and minimal repro (for a possible Kani issue; NOT published)
Root 1 is the candidate replacement for `dispatch_safety_stable_zst_n0_1_2_7_8_15_16_17_31_32` (VT 194.8 s GCB jobs1;
macOS not measured). Repro (Kani 9461e07a, verify-rust-std core; expected SUCCESS, observed 4 dereference failures):
`#[kani::proof] fn zst_read_volatile_local() { let x = (); let _u: () = unsafe { core::ptr::read_volatile(&x) }; }`
Variant: `core::ptr::NonNull::<()>::dangling().as_ptr()` instead of `&x` → 5 failures. `ptr::read` path (zst_aware_less) ok.
Cost: build $0.1620 (own spent $0.1620 of cap $1.00, reserved $0); project used $88.0575, reserved $0, cap $93.96.
Receipts: zstprobe/{PREBUILD.md, summary.md, tooling.txt, log-grep.txt, log-grep-warnings.txt, cost.txt, budget-final.txt}.
