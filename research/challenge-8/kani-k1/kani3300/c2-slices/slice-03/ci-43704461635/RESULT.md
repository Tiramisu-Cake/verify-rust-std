# Slice 03 LAYOUT-RAW — run 43704461635: FAIL (fixture placement, not production)

2026-11-15, coordinator. Overlay `a2a533e087` on source `d0345ddf4f` (parent slice 2 `932fb8395a`).
fmt/build/clippy, ActiveCalls 9, immutable 9, kani 50/0/3, ui 17, script 3, json 17, std-checks 2 — pass.
expected: **220 passed / 18 failed / 6 ignored** (all previous 219 still pass).

The 18 failures are fixtures added by slice 3 that slice 2 had deferred (`integration_status: PENDING`):
`promoted-allocations/{direct,helper}-{legal,left-hole,right-hole}`, `immutable-masks/zero-byte{-hole,s-legal}`,
`mixed-promoted-allocations/{eq,raw}-u8-stack-{left,right}`, `part1-edges/immutable-{relocation,static,subrange}-{hole,legal}`.
Each fails with an early `unsupported_construct`:
"Checking memory initialization of type [std::mem::MaybeUninit<u8>; 3] is not supported…" or
"Interaction between raw pointers and unions is not yet supported." — MaybeUninit storage / projected-raw support
arrives in slice 4. In F (Gate A 43665002636) these fixtures pass. Stage-0 decision 3 ("u8 mixed + promoted raw_eq
qualify at 3") was wrong for these fixtures.

Decision: move the 18 fixtures to slice 4 (first runnable head); slice 3 becomes NO_REGRESSION with integration
PENDING on 4; production hunks of slice 3 unchanged. Returned to worker14.
