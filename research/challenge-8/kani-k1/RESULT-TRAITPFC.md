# RESULT-TRAITPFC — G1 PASS (B1 bounded calibration)

Build `e77f402e-95bf-400b-994e-a86fe57bd72c`: Cloud SUCCESS; summary COMPLETE; gate/expectations true; expected Kani exit 1.
Source `ac1a18c84f39ed9c5ce3ecf95bf7b84e67908e3f`; library commit `ea4528ac91bf715b9477c263495e0db325957923`; tree `7fd692282cc522f3d12c2f1c00fc25f5557884f6`.
Base/tooling `9b1758ab817af005e96fd52a5fc940d4b6acf984`; library diff only `smallsort.rs`, `smallsort/verify.rs`, `smallsort/verify/trait_contracts.rs`.
Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`; nightly-2026-10-23. Exact request/T/F/N/scratch/geometry/covers: [packet](traitpfc/PREBUILD-TRAITPFC.md), [rows](traitpfc/expected-rows.json).
Flags: diagnostic, controls=true, inventory=false, standard4, jobs=1, timeout 5m; unwind new=32/R1=34/R2=16; no-assert-contracts, object-bits 12; uninit/value-validity off.
Added attributes verbatim (no ensures); T1:
```rust
    #[safety::requires(
        v.len() < 2 || scratch.len().checked_sub(16).is_some_and(|capacity| v.len() <= capacity)
    )]
    #[cfg_attr(kani, crate::kani::modifies(v, scratch))]
// T2 and T3 have identical attributes:
    #[safety::requires(
        <T as UnstableSmallSortFreezeTypeImpl>::small_sort_threshold()
            == SMALL_SORT_FALLBACK_THRESHOLD
            || v.len() <= <T as UnstableSmallSortFreezeTypeImpl>::small_sort_threshold()
    )]
    #[cfg_attr(kani, crate::kani::modifies(v))]
```
| Row | Status | Seconds | Failed/total | Covers |
|---|---|---:|---:|---:|
| P1 | SUCCESS | 61.873463 | 0/371 | 3/3 |
| P2 | SUCCESS | 8.339401 | 0/409 | 3/3 |
| P3 | SUCCESS | 16.11834 | 0/446 | 3/3 |
| S0 | SUCCESS | 1.5168791 | 0/375 | 0/0 |
| S1 | SUCCESS | 1.5670406 | 0/473 | 0/0 |
| S2 | FAILED | 1.6120687 | 1/488 | 0/0 |
| R1 | SUCCESS | 3.794201 | 0/427 | 2/2 |
| R2 | SUCCESS | 31.778137 | 0/509 | 7/7 |

Only failed check, in full: `forwarded output is sorted` — `/workspace/src/library/core/src/slice/sort/shared/smallsort/verify/trait_contracts.rs:81`, `rejects_verified_forwarding_sorted_u64_backing4`; expression `v[0] <= v[1]`.
S1/S2 diagnostic verbatim: `Verified stub: <T as core::slice::sort::shared::smallsort::UnstableSmallSortFreezeTypeImpl>::small_sort`; T3 binding confirmed; S0/S2 bodies identical, S1 omits only sortedness.
Classes: frontend/resolution 0; unsupported 0; TIMEOUT 0; ordinary FAILED 1 (the sole designated S2 check). Warnings: manifest/unstable-feature warnings present; no SmallSort warning locations reported.
Static: 235 ordinary unchanged; cfg-on 248+6=254; 571 old items/248 closures unchanged; methods unchanged except attributes; rustfmt zero diff; no new >100 lines (three upstream exceptions accepted). Native inventory not requested.
Unreachable checks P1/P2/P3/S0/S1/S2/R1/R2: 8/19/21/18/21/21/76/18; every required cover satisfied. No generic-domain, initialization-validity or substantive sorting-contract claim.
Expense $0.1755 (13 billed minutes), reserve released; own cap $2.00; project used $109.3740/$118.96, unfinished reserve $0; one build, no repair/retry; paid timeout 70m. T0 15:00Z, finish 15:14:30Z; main deadline 20:00Z, closeout 20:30Z.
G2: `kani::ensures(|_| ...)` is a candidate (as in existing wrapper contracts); pure order/full-value models for generic T and comparator binding remain to design. Direct-trait postconditions and full-value ensures are untested; no G1 resolution blocker remains.
Evidence and exact check counts: [verification report](traitpfc/g1-evidence/verification-report.json); library/tooling/request identities remain frozen; no further build authorized.
