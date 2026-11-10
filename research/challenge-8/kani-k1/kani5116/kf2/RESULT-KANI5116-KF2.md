# RESULT-KANI5116-KF2 — FAIL (Freeze unwind bound)

- Build `a80cfa79-d1e2-44b9-b320-ffa78c7bbe0e`, Cloud `FAILURE`, bounded summary `COMPLETE`, Kani exit 1, gate false, expectation met false.
- Approved head `150626a8b0303923ec43f5e0ea10a0017cb7376a`; request `kani5116-kf2-main-20261111-01`, SHA-256 `43baae98e1f9510a91d23637ac85278df02b6ed188d1f6310730381d2e943606`.
- Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`, Kani 0.68.0 / CBMC 6.11.0; KF1 patch SHA-256 `fd510b8a47ffff2005cc2362af6c25db790d1b579a23c0c990f6d606a983aa71`; applied tree `46f37ae9abe9bb747ec7b7de33212484ed175a1b`. All match PRE-BUILD.
- `check-tooling` PASS against `c98d7cee0d509b1633ab61c9a1ae989e286c8e2a` for pool, lane files, six bound blobs, request and patch.

D1 and D2 each carry `#[cfg_attr(kani, crate::kani::modifies(v))]`. D3's attributes follow.

```rust
    #[cfg_attr(
        kani,
        crate::kani::requires(
            size_of::<T>() * SMALL_SORT_GENERAL_SCRATCH_LEN > MAX_STACK_ARRAY_SIZE
                || v.len() <= SMALL_SORT_GENERAL_THRESHOLD
        )
    )]
    #[cfg_attr(kani, crate::kani::modifies(v))]
```

| Row | Status | Time (s) | Failed/total | Covers | Failed checks (verbatim) |
|---|---|---:|---:|---:|---|
| P1 `stable_default_n2` | SUCCESS | 5.9199896 | 0/162 | 3/3 | — |
| P2 `unstable_default_n2` | SUCCESS | 5.9330516 | 0/162 | 3/3 | — |
| P3 `freeze_default_n2` | FAILED | 1.383776 | 1/562 | 0/3 | `unwinding assertion loop 0 @ /workspace/src/library/core/src/array/mod.rs:921` |
| S0 `freeze_forwarder_body_n2` | FAILED | 1.243515 | 1/575 | — | `unwinding assertion loop 0 @ /workspace/src/library/core/src/array/mod.rs:921` |
| S1 `freeze_forwarder_stub_frame_n2` | FAILED | 1.3435512 | 1/667 | 0/1 | `unwinding assertion loop 0 @ /workspace/src/library/core/src/array/mod.rs:921` |
| S2 `freeze_forwarder_stub_order_n2` | FAILED | 1.3494735 | 1/673 | — | `unwinding assertion loop 0 @ /workspace/src/library/core/src/array/mod.rs:921` |

P1/P2 are bounded `Cell<u8>` N2 PFC successes, each with four unreachable checks. The Freeze failure points to the `try_from_fn_erased` loop, consistent with the shared four-element symbolic backing under `#[kani::unwind(4)]`.
S2's assigned check `KF2 S2 weak Freeze stub permits reversed output` at `verify/default_contracts.rs:102` is absent from the failure list. P3 covers, S0/S1 behavior and S2 calibration are unestablished. Direct PFC/`Verified stub` target trace `UNCONFIRMED`.
Evidence from bounded `k1g.sh summary` and rows 0–5. `smallsort-brief` returned HTTP 404 for this build. No raw evidence used.
Pool elapsed 536.500 s, 9 billed min. KF2 actual $0.1215, reserved $0, cap $0.80. Branch actual $0.7020 including KT1/KF1, cap $2.30.
Submission after the fix reaches the verify-rust-std pin requires a passing Freeze rerun with sufficient harness unwind and the assigned S2 failure, plus cfg-off validation of the ordinary 235-harness set (NOT_RUN here). This run supplies N2 diagnostic evidence only. Any repair requires a new GO.
