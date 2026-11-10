# PRE-BUILD — KANI5116 KF2 repair 1

Branch `experiment/kani-k1-kani5116-20261110`, owner `k1-merge`, stage `kani5116-kf2`. The original T0 and 300 min main + 30 min closeout apply. Dispatch requires fresh coordinator GO on the exact pushed review SHA.

- Build `a80cfa79-d1e2-44b9-b320-ffa78c7bbe0e` passed P1/P2 with 3/3 covers each. P3 and S0–S2 each failed only on `unwinding assertion loop 0 @ /workspace/src/library/core/src/array/mod.rs:921`. The shared `kani::any()` for `[NonCopyU8; 4]` needs four `try_from_fn_erased` iterations plus the exit check.
- Library commit `1a793275702a51d996db666e39b22d3c03a13154` changes `#[kani::unwind(4)]` to `#[kani::unwind(8)]` on P3 and S0–S2. Byte comparison confirmed those four lines are the full Rust diff.
- Request `kani5116-kf2-repair1-20261111-02`, SHA-256 `452bf67c5f05a6be751be0a6250f600c4d26b7ceab6b53edbbf546df6d509d34`, selects P3 and S0–S2 with their original expectations and the same diagnostic settings. P1/P2 evidence remains from Build 1.
- Tooling base `c98d7cee0d509b1633ab61c9a1ae989e286c8e2a`, Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`, patch SHA-256 `fd510b8a47ffff2005cc2362af6c25db790d1b579a23c0c990f6d606a983aa71`, expected applied tree `46f37ae9abe9bb747ec7b7de33212484ed175a1b`.
- Static checks passed for the exact Rust delta, four request rows, request validator, lane parity, rustfmt, line lengths and `git diff --check`.
- `k1g.sh budget` confirmed KF2 $0.1215 actual and $0 reserved. Four rows × 4 min + 30 min overhead = 46 min at $0.0135/min in standard4. Repair reserve $0.6210 puts KF2 at $0.7425 of $0.80, cumulative branch at $1.3230 of $2.30, and project at $113.0055 of $118.96 at the ledger snapshot. Dispatch rechecks the live ledgers.

## After GO

Run `k1g.sh dispatch experiment/kani-k1-kani5116-20261110` and `k1g.sh watch BUILD`, then end the turn. After wakeup, use bounded `k1g.sh summary BUILD` and `k1g.sh summary BUILD 0 4`, `check-tooling` against the pinned tooling base, and `budget` for both KF2 build IDs. Compare head, request, pin, patch and applied tree.

P3 must pass with zero failures and 3/3 covers. S0 and S1 must pass, including the S1 return cover 1/1. S2 must fail only on `KF2 S2 weak Freeze stub permits reversed output` at `verify/default_contracts.rs:102`. Record direct target trace as `UNCONFIRMED` where absent from bounded evidence. Preserve Build 1 in RESULT.
