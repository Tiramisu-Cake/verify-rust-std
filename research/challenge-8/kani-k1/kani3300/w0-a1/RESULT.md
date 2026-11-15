# W0-A1 result template — NOT_RUN

Preparation only. No local Rust/Kani/CBMC/Miri/build, push, dispatch or publication.
Cloud $0. No new bounded or full proof credit. Historical replay results are references only.

| Required field | Value before coordinator dispatch |
|---|---|
| CI run URL / trigger SHA / package SHA / attempt | NOT_RUN / UNKNOWN / see CI-OVERLAY.json / UNKNOWN |
| Actual source pin/tree/setup/submodules | UNKNOWN (expected identities in INPUTS.json and ci bindings) |
| Actual std HEAD/tree/library/overlay bytes, before/after | UNKNOWN |
| Native isolated cwd/input hash/mode/selector | UNKNOWN |
| Actual argv/environment allowlist/target/types/root | UNKNOWN |
| Binary/driver/compiler/runtime/sysroot/solver hashes | UNKNOWN |
| Begin/end phase, original exit/signal, failed properties/statuses | UNKNOWN |
| Reached entry/return/readbacks, frame/unwinding checks | UNKNOWN |
| Elapsed: complete maximum and censored caps separately | UNKNOWN |
| wait4 raw RSS KiB; bytes/MiB/GiB; driver/backend/group current RSS | UNKNOWN |
| Available RAM, OS reserve, frozen watchdog threshold | UNKNOWN |
| Missing/truncated artifacts, OOM/runner loss, coverage | UNKNOWN |
| Generated selected-body/property/source binding | UNKNOWN |
| B1 bounded evidence / B2 full proof | NOT_ESTABLISHED / NOT_ESTABLISHED |

R1 has eight exact roots in ci/CI-REQUEST.json, three N32 first. Every row needs its own
complete receipt, useful zero-failure safety checks and all four mandatory covers (entry/comparator/return/readbacks); retain the separate conditional order-boundary cover.
Report timeout/OOM as censored observations; do not rank unknown total times as measured.
Arbitrary-bool normal-return safety is separate from lawful sortedness/multiset cost in S.

R2 has six independent cases per pin, twelve invocations. Retain every failed property,
phase and exit even for an intended negative. Baseline issue claims are hypotheses:
classify BASELINE_NOT_REPRODUCED if absent at frozen0aac, never silently change the pin.
#5020 and #5151 candidate unexpected SUCCESS => MISSED_CHECK / STOP.
#4854 no ICE plus Unsupported is diagnostic improvement, not support; original autoharness
NOT_RUN/BLOCKED cannot be discharged by explicit-proof companion.

First named blocker: UNKNOWN. Coordinator's decision on optional one OFF N32 companion:
NOT_REQUESTED. R3 reserve: UNUSED; requires explicit coordinator decision after R1/R2.
No automatic retry or compiler patch. Dispatch ledger entries: NONE from this preparation.
