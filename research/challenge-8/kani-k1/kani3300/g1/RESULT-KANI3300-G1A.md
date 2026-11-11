# KANI3300 G1A — bounded result

- Build `e35ca11d-307e-46f6-8212-a97e5bbee087`: **FAIL / RUNNER_ERROR**, stage `build`; source `3eff5da19860d6ab920ddd8307ce5fc4f5fd92d9`.
- Request `48bb88e982606c52aef64c5c9f9f3b0be81cb03569764074dffc21f000119ace`; patch `35cae231c17b836a1d0191ee417a6e9a875eb41f2f8cf353ef2b1442bf78e40b`; pin `f046b70644e113be0df9c22c2e6ea44a65a57566`.
- Two E0308 errors in our patch: `uninit_visitor.rs:324:54` and `:617:62`; vector length expects `usize`, receives `MachineSize` (`shape().size`).
- Build wall **273.335 s**, queue 55.339 s; native wall unavailable. Ledger: **$0.0675** (5 rounded minutes × $0.0135), reservation released; cap $0.80.
- All selectors are **NOT_RUN**: native stage requires successful `build.ok`; compilation failed first. Individual PASS/FAIL and wall seconds are unavailable, not counted as test FAIL.
- Evidence Brief returned HTTP 404; results below are source-reported through the watch-requested bounded `k1g.sh summary/status/budget/native` routes. No raw log/archive fallback or proof acceptance.
- Runtime patch/tree/version/build identity is incomplete; expected tree `bb3cb747eab1f81de9511733ec65f21fcff0bbeb` remains preflight-only. Structured receipts: `G1A-OBSERVATIONS.json`.

| # | Selector under tests/expected | Status | Native wall s |
|---|---|---|---|
| 01 | `uninit/g1-union-pointee-positive/main.rs` | NOT_RUN | — |
| 02 | `uninit/g1-union-pointee-negative/main.rs` | NOT_RUN | — |
| 03 | `uninit/g1-union-pointee-unsupported-reject_array_element/main.rs` | NOT_RUN | — |
| 04 | `uninit/g1-union-pointee-unsupported-reject_bodyless_transfer/main.rs` | NOT_RUN | — |
| 05 | `uninit/g1-union-pointee-unsupported-reject_fn_pointer_field/main.rs` | NOT_RUN | — |
| 06 | `uninit/g1-union-pointee-unsupported-reject_foreign_mutation/main.rs` | NOT_RUN | — |
| 07 | `uninit/g1-union-pointee-unsupported-reject_indirect_call/main.rs` | NOT_RUN | — |
| 08 | `uninit/g1-union-pointee-unsupported-reject_init_predicate/main.rs` | NOT_RUN | — |
| 09 | `uninit/g1-union-pointee-unsupported-reject_manuallydrop_union/main.rs` | NOT_RUN | — |
| 10 | `uninit/g1-union-pointee-unsupported-reject_niche_enum/main.rs` | NOT_RUN | — |
| 11 | `uninit/g1-union-pointee-unsupported-reject_select_unpredictable/main.rs` | NOT_RUN | — |
| 12 | `uninit/g1-union-pointee-unsupported-reject_struct_field/main.rs` | NOT_RUN | — |
| 13 | `uninit/g1-union-pointee-unsupported-reject_typed_swap/main.rs` | NOT_RUN | — |
| 14 | `uninit/g1-union-pointee-unsupported-reject_unaligned_read/main.rs` | NOT_RUN | — |
| 15 | `uninit/g1-union-pointee-unsupported-reject_unaligned_write/main.rs` | NOT_RUN | — |
| 16 | `uninit/g1-union-pointee-unsupported-reject_union_in_union/main.rs` | NOT_RUN | — |
| 17 | `uninit/g1-union-pointee-unsupported-reject_union_transmute/main.rs` | NOT_RUN | — |
| 18 | `uninit/g1-union-pointee-unsupported-reject_variant_padding/main.rs` | NOT_RUN | — |
| 19 | `uninit/g1-union-pointee-unsupported-reject_volatile_read/main.rs` | NOT_RUN | — |
| 20 | `uninit/g1-union-pointee-unsupported-reject_volatile_write/main.rs` | NOT_RUN | — |

**Total:** 0 PASS, 0 FAIL, 20 NOT_RUN; Gate A failed during compiler build. No proof obligations closed.
Attempt **1/1** finished; no repair/retry. Kani candidate unchanged and unpushed. **B was not installed or run**; separate GO required. Unused cap is not further build authorization.
