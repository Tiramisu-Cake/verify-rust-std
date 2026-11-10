# RESULT-TRAITPFC-G3 — PASS (B1 bounded)

Build 1 `9d94cb84-55e1-4cae-a55b-9597ddd81d87` at `55a7fd1c8ada1590ab571b040a6256219ef75e63` ended Cloud FAILURE / COMPILE_ERROR. Frontend type resolution E0308 in K4/W1 left all 14 rows NOT_RUN. Library `aa0859448612246d0c52e1c59f844e777c8ad3b6`, tree `b6f050a21d2781fcc95a8f7e02bf9154affa560a`, patch SHA-256 `4f877ee8ece2fcad1ed09938470874ba4f6676316d415df924ff95459f3baf6b`. [Build 1 evidence](traitpfc/g3/evidence/verification-report.json)
Build 2 `368b93f4-e7ae-4603-bf41-ea3fb6573e3e` at `2f1c45e519cc89e1dae532ad0f44243255a514d7` ended Cloud SUCCESS / COMPLETE with gate and expectations true and expected Kani exit 1. Library `1aac64c50d69382c8ce90811880225d0a047525f`, tree `6ea9d3425f6d0478cfc2517cbdd2fb7d7b32a53f`, patch SHA-256 `ec6019f2e51b23c331a5fc5d9e190283c81e7ac506ee7bf1fe2c1dc0af85f840`. [Evidence](traitpfc/g3/build2/evidence/verification-report.json) · [Patch](traitpfc/g3/build2/library.patch)
Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, nightly-2026-10-23, tooling base `9b1758ab817af005e96fd52a5fc940d4b6acf984` PASS. Both Brief queries returned HTTP 404. Evidence comes from the authorized bounded K-1 fallback.
Model `pub(crate) trait SortModel<T, F>` with `fn enabled(entry: SortEntry, cmp: &F, len: usize) -> bool;`, `fn snapshot(base: *const T, len: usize) -> SortSnapshot;` and `fn sort_postcondition(pre: SortSnapshot, base: *const T, len: usize) -> bool;`. `pub(crate) type U64Cmp = fn(&u64, &u64) -> bool;` and `pub(crate) fn canonical_less_u64(a: &u64, b: &u64) -> bool`.
T1 literal ensures follows. T2/T3 substitute the entry `Unstable`/`Freeze` respectively. [All three literal attributes](traitpfc/g3/build2/contracts.json)
```rust
    #[cfg_attr(kani, crate::kani::ensures(|_|
        !old(<() as verify::trait_model::SortModel<T, F>>::enabled(
            verify::trait_model::SortEntry::Stable, is_less, v.len(),
        )) || <() as verify::trait_model::SortModel<T, F>>::sort_postcondition(
            old(<() as verify::trait_model::SortModel<T, F>>::snapshot(v.as_ptr(), v.len())),
            v.as_ptr(), v.len(),
        )
    ))]
```
Native old captures enabled and the Copy snapshot `{ len, valid, vals: [u64; 3] }`. The checker uses pure `<=`, one post-snapshot, and full multiplicities, with the exact pair formula at N2. Build 2 uses the approved generic lookup helper in K4/W1.

| Row | Status | Seconds | Failed/total | Covers | Unreachable |
|---|---|---:|---:|---:|---:|
| A1 | SUCCESS | 112.45171 | 0/487 | 5/5 | 16 |
| A2 | SUCCESS | 169.94554 | 0/503 | 5/5 | 16 |
| A3 | SUCCESS | 28.834583 | 0/582 | 5/5 | 29 |
| A4 | SUCCESS | 68.057304 | 0/638 | 5/5 | 29 |
| A5 | SUCCESS | 82.79854 | 0/714 | 5/5 | 29 |
| A6 | SUCCESS | 128.4587 | 0/770 | 5/5 | 29 |
| C1 | SUCCESS | 6.1645646 | 0/762 | 5/5 | 29 |
| K1 | FAILED | 1.9056786 | 1/102 | — | 12 |
| K2 | FAILED | 0.5499438 | 1/58 | — | 10 |
| K3 | FAILED | 2.210697 | 1/633 | — | 39 |
| K4 | FAILED | 2.0546393 | 1/547 | — | 21 |
| W1 | SUCCESS | 35.949974 | 0/492 | 3/3 | 21 |
| R1 | SUCCESS | 3.6611972 | 0/427 | 2/2 | 76 |
| R2 | SUCCESS | 31.68138 | 0/509 | 7/7 | 18 |

K1 sole failed check `high-bit corruption preserves sorted full values` at `/workspace/src/library/core/src/slice/sort/shared/smallsort/verify/trait_contracts.rs:181` in `slice::sort::shared::smallsort::verify::trait_contracts::rejects_high_bit_corruption_u64_len3`, expression `<() as SortModel<u64, U64Cmp>>::sort_postcondition(pre, v.as_ptr(), v.len())`.
K2 sole failed check `same set preserves full multiplicities` at `/workspace/src/library/core/src/slice/sort/shared/smallsort/verify/trait_contracts.rs:197` in `slice::sort::shared::smallsort::verify::trait_contracts::rejects_changed_multiplicities_u64_len3`, expression `<() as SortModel<u64, U64Cmp>>::sort_postcondition(pre, post.as_ptr(), 3)`.
K3 sole failed check `reverse pointer output is sorted` at `/workspace/src/library/core/src/slice/sort/shared/smallsort/verify/trait_contracts.rs:220` in `slice::sort::shared::smallsort::verify::trait_contracts::rejects_reverse_pointer_sorted_u64_backing5`, expression `v[0] <= v[1] && v[1] <= v[2]`.
K4 sole failed check `function item output is sorted` at `/workspace/src/library/core/src/slice/sort/shared/smallsort/verify/trait_contracts.rs:253` in `slice::sort::shared::smallsort::verify::trait_contracts::rejects_function_item_sorted_u64_backing5`, expression `v[0] <= v[1] && v[1] <= v[2]`.
Native cfg-off inventory exactly matches all 242 names on the final tree. Source manifests 235→242 ordinary and 260→260 cfg-on. Inventory flag attribution uses the frozen list-before-export runner. Rows use controls-on, standard4/jobs1, 5m, no-assert-contracts/object-bits12, with uninit/value-validity off. [Inventory evidence](traitpfc/g3/build2/evidence/inventory-check.json)
Code-ready PASS with static, rustfmt and apply-check PASS. B1 bounded proof PASS for canonical U64Cmp/u64 N2/N3. T1 uses array N and scratch N+16. T2/T3 use backing N+2, active 1..N+1, and exterior frame checks. A5/A6 compose matching real A3/A4. C1 N3 matches A4/A6. W1 matches K4 function-item frame. Resource-open empty. New ordinary ΣVT = 596.7109416s.
Cost $0.6615 + $0.8640 = $1.5255 of $3.50, 49 + 64 billed minutes. Project observed $112.2630/$118.96, reserved $0.0000. T0 2026-11-10 19:51:57Z, main deadline 2026-11-11 01:51:57Z. Two builds used.
Evidence covers the listed domains and normal returns under comparators with no external writes. Open scope includes generic T/F, specialization default fn, other lengths/types/geometries, additional UB classes, unwind theorem, B2 and actual PR CI with the pin including kani#5135.
