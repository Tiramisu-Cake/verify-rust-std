# RESULT-TRAITPFC-G2 — PASS (B1 bounded)

Build `fd40d716-e18d-4eb9-ae56-a15cd767147d`: Cloud SUCCESS, summary COMPLETE, gate/expectations true, expected Kani exit 1; source `344daafe1d77694bba095a6c87b3c05f9aeba77b`.
Library commit `fbb5aee754f7b49e0a7c963e581f228ce6d1a452`; tree `85f5f434528b3843ab91586b8f850026e3d77be9`; request `traitpfc-g2-20261110-01`, SHA256 `6c9eff4747907fac91b26cb072af33a007d7f7eaa480f25314266b2627099145`.
Tooling `9b1758ab817af005e96fd52a5fc940d4b6acf984` unchanged (check-tooling PASS); Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, nightly-2026-10-23.
Flags: rows controls-on, standard4/jobs1, timeout5m, unwind new32/R1=34/R2=16, no-assert-contracts/object-bits12; uninit/value-validity off.
Model: `pub(crate) type U64Cmp = fn(&u64, &u64) -> bool;`; `pub(crate) fn canonical_less_u64(a: &u64, b: &u64) -> bool`; `pub(crate) trait PairModel<T, F>`; `fn enabled(cmp: &F, len: usize) -> bool;` `fn snapshot(base: *const T, len: usize) -> (u64, u64);` `fn pair_is_sorted(base: *const T, len: usize) -> bool;` `fn pair_permutation(base: *const T, len: usize, pre: (u64, u64)) -> bool;` Blanket default impl for (); specialization `impl PairModel<u64, U64Cmp> for ()`. Native old captures pre-state enabled and Copy `(u64, u64)`; no fallback/new requires. Identical literal added ensures on T1–T3 below. Brief HTTP404; authorized bounded K-1 evidence in [report](traitpfc/g2/evidence/verification-report.json).
```rust
    #[cfg_attr(kani, crate::kani::ensures(|_|
        !old(<() as verify::trait_model::PairModel<T, F>>::enabled(is_less, v.len()))
            || (<() as verify::trait_model::PairModel<T, F>>::pair_is_sorted(
                v.as_ptr(), v.len(),
            )
                && <() as verify::trait_model::PairModel<T, F>>::pair_permutation(
                    v.as_ptr(), v.len(),
                    old(<() as verify::trait_model::PairModel<T, F>>::snapshot(
                        v.as_ptr(), v.len(),
                    )),
                ))
    ))]
```

| Row | Status | Seconds | Failed/total | Covers | Unreachable |
|---|---|---:|---:|---:|---:|
| E1 | SUCCESS | 69.51902 | 0/472 | 5/5 | 8 |
| E2 | SUCCESS | 20.262255 | 0/559 | 5/5 | 19 |
| E3 | SUCCESS | 20.403618 | 0/557 | 5/5 | 21 |
| C1 | SUCCESS | 2.7244892 | 0/627 | 1/1 | 21 |
| N1 | FAILED | 0.19330244 | 1/48 | 0/0 | 1 |
| N2 | FAILED | 1.8516306 | 1/540 | 0/0 | 21 |
| N3 | FAILED | 1.9880459 | 1/608 | 0/0 | 21 |
| W1 | SUCCESS | 15.698717 | 0/499 | 3/3 | 21 |
| R1 | SUCCESS | 7.667644 | 0/427 | 2/2 | 76 |
| R2 | SUCCESS | 45.22978 | 0/509 | 7/7 | 18 |

Full sole failures: N1: Failed Checks: `high-bit corruption preserves full pair`; File: `/workspace/src/library/core/src/slice/sort/shared/smallsort/verify/trait_contracts.rs`, line 175, in `slice::sort::shared::smallsort::verify::trait_contracts::rejects_high_bit_corruption_u64_pair`; expression `<() as PairModel<u64, U64Cmp>>::pair_permutation(v.as_ptr(), v.len(), pre)`; N2: Failed Checks: `forwarded output is sorted`; File: `/workspace/src/library/core/src/slice/sort/shared/smallsort/verify/trait_contracts.rs`, line 81, in `slice::sort::shared::smallsort::verify::trait_contracts::rejects_verified_forwarding_sorted_u64_backing4`; expression `v[0] <= v[1]`; N3: Failed Checks: `reverse pointer output is sorted`; File: `/workspace/src/library/core/src/slice/sort/shared/smallsort/verify/trait_contracts.rs`, line 196, in `slice::sort::shared::smallsort::verify::trait_contracts::rejects_reverse_pointer_sorted_u64_backing4`; expression `v[0] <= v[1]`. N1 packet line177 is the message literal; native assertion is line175. T3 verified-stub binding confirmed for C1/N2/N3.
Native inventory: cfg-off, all 235 names exactly match (three bounded pages, same tree); rows controls-on. Inventory flag attribution uses bound runner list-before-export and unfiltered 235-root metadata; runtime list argv is not emitted. [Flag attribution](traitpfc/g2/evidence/flag-attribution.json).
Static: 235 ordinary, 254 prior root closures and G1 bytes unchanged, cfg-on260; rustfmt zero diff, no new Rust line>100 (three inherited comments). Classes: frontend/resolution/specialization error0, unsupported0, TIMEOUT0, ordinary FAILED3. Warnings: manifest edition, unstable features, core future-incompatibility; no SmallSort warning locations reported.
Expense $0.7830 (58 billed min), own cap$3; one build, no repair/retry, reserve released; project used$110.1570/$118.96, reserve$0. T0 15:46Z; run 15:48:49–16:46:05Z; main deadline20:46Z/closeout21:16Z, 2026-11-10.
Proved only B1 u64/N2/canonical fn-pointer: T1 array2+scratch18; T2/T3/C1 backing4 active1..3 with exterior frame, sortedness and full-value pair permutation; all required covers. No generic T/F, other lengths, additional UB classes or unwind theorem; no B2 claim.
