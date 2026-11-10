# RESULT-KANI5116-KF2 — PASS (N2 diagnostic matrix across two builds)

- Build 1 `a80cfa79-d1e2-44b9-b320-ffa78c7bbe0e`, Cloud `FAILURE`, summary `COMPLETE`, gate false. Head `150626a8b0303923ec43f5e0ea10a0017cb7376a`, request `kani5116-kf2-main-20261111-01`, SHA-256 `43baae98e1f9510a91d23637ac85278df02b6ed188d1f6310730381d2e943606`.
- Repair 1 `88478051-df3e-4543-9437-6f5ab1b38528`, Cloud `SUCCESS`, summary `COMPLETE`, gate and expectation met true, Kani exit 1 with the expected S2 failure. Head `528046c42d9c2b3c1cbd15fd619cf9ce4f6ebb91`, request `kani5116-kf2-repair1-20261111-02`, SHA-256 `452bf67c5f05a6be751be0a6250f600c4d26b7ceab6b53edbbf546df6d509d34`.
- Both match the Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`, Kani 0.68.0 / CBMC 6.11.0, KF1 patch SHA-256 `fd510b8a47ffff2005cc2362af6c25db790d1b579a23c0c990f6d606a983aa71` and applied tree `46f37ae9abe9bb747ec7b7de33212484ed175a1b`.
- Both `check-tooling` PASS against `c98d7cee0d509b1633ab61c9a1ae989e286c8e2a` for pool, lane files, six bound blobs, request and patch.

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

| Row | Build | Status | Time (s) | Failed/total | Covers | Failed checks (verbatim) |
|---|---|---|---:|---:|---:|---|
| P1 `stable_default_n2` | 1 | SUCCESS | 5.9199896 | 0/162 | 3/3 | — |
| P2 `unstable_default_n2` | 1 | SUCCESS | 5.9330516 | 0/162 | 3/3 | — |
| P3 `freeze_default_n2` | Repair 1 | SUCCESS | 86.609215 | 0/561 | 3/3 | — |
| S0 `freeze_forwarder_body_n2` | Repair 1 | SUCCESS | 3.8645368 | 0/574 | — | — |
| S1 `freeze_forwarder_stub_frame_n2` | Repair 1 | SUCCESS | 2.4199998 | 0/666 | 1/1 | — |
| S2 `freeze_forwarder_stub_order_n2` | Repair 1 | FAILED (expected) | 2.1807637 | 1/672 | — | `KF2 S2 weak Freeze stub permits reversed output @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/default_contracts.rs:102` |

Build 1 P3/S0/S1/S2 each failed only on `unwinding assertion loop 0 @ /workspace/src/library/core/src/array/mod.rs:921`. In order, time/checks/covers were 1.383776 s/1 of 562/0 of 3, 1.243515 s/1 of 575/—, 1.3435512 s/1 of 667/0 of 1, and 1.3494735 s/1 of 673/—. Repair raised only their harness unwind from 4 to 8 for the four-element backing array.
The PFC rows passed for the selected default methods. S0 checked frame and order through the real Freeze forwarder, S1 checked frame and return with `stub_verified`, and S2 confirmed that the weak stub permits reversed output. Direct PFC/`Verified stub` target trace `UNCONFIRMED` in bounded `k1g.sh` evidence. `smallsort-brief` returned HTTP 404 for both builds.
Pool elapsed and actual cost were 536.500 s / $0.1215 for Build 1 and 638.658 s / $0.1485 for Repair 1. KF2 ledger $0.2700 actual and $0 reserved within $0.80. Branch actual $0.8505 including KT1/KF1 within $2.30.
Evidence is limited to the selected N2 types, comparators and geometry. After the fix reaches the verify-rust-std pin, recheck the smoke on the updated pin and validate the ordinary 235-harness set with controls off (NOT_RUN here) before submission.
