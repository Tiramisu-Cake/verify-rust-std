# Gate B′ — run 43600834435 (C1 1658f4cad, closure comparators, uninit ON)

2026-11-14, coordinator. Package: std branch `prep/kani3300-gateb-prime` @ `01d75b8e83` (worker15,
test-only overlay `933b20a237`); CI overlay `0c1cc8a7d0` on run4 recipe `ac49cf8f62`, branch
`ci/kani3300-gateb-prime-w15`. Std `70ba5befc6`; receipts bind C1 `1658f4cadfa83139e41180ce3865e23f79d889aa`.
Profile: object-bits 12, unwind 34/34/16, default solver/slicing/checks, valid-value OFF, controls cfg ON.
Outcomes are from per-row stdout/receipt artifacts (coordinator scratchpad; only stdout/stderr/receipt/export kept).

| Row | Harness | Result |
| --- | --- | --- |
| merge-raw-closure-on | `helper_contracts_wide::merge_safety_u64_len8_scratch48_src32_dst0` (PFC `bidirectional_merge`, `[MU<u64>;48]`, src[32..40], uninit dst prefix) | **SUCCESS**, 0 of 570 failed (16 unreachable), 5/5 covers incl. "merge length8 returns", "comparator true/false" |
| merge-profile-closure-on | `replay_gateb_prime::merge_profile_closure_scratch48_u8_n9` (PFC concrete `merge_profile_closure_u8`, flat48 / `MU<[u8;48]>`) | **SUCCESS**, 0 of 1028 failed (68 unreachable), 2/2 covers (both scratch backings) |
| sort4-closure-on | `helper_contracts::sort4_safety_u64` (PFC `sort4_stable`) | **BOUNDARY as predicted**: 1 of 758 failed — only `hint::select_unpredictable::<*const u64>.unsupported_construct.1` (hint.rs:871); no comparator/layout/uninit/frame failures |

- In both SUCCESS rows every `unsupported_construct` property (6 each: `intrinsics::unlikely`, `same_allocation`,
  `is_inbounds`, `panic_nounwind_fmt`, `Location::caller` ×2) has status SUCCESS, i.e. is not reached.
- Confirms audit R4 F1: with a closure comparator the comparator boundary disappears; merge needs no SEL1.
  The run4 PFC failure was the fn-item layout in the `FnMut::call_mut` shim, not comparator calls in general.
- Scope: qualifies only these bounded geometries/targets on C1. The concrete profile companion does not
  re-prove the generic fn-pointer `merge_profile<P>`. sort4/swap_if_less remain blocked on `select_unpredictable` → SEL1.
- Receipt `outcome` field is UNKNOWN for all rows (runner leaves it for review); verdicts above are from stdout.
