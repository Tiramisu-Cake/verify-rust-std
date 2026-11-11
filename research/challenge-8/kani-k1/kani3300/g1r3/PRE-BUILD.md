# KANI3300 G1R3 — PRE-BUILD REVIEW
PREPARED, NOT AUTHORIZED; Runtime Codex; one static stage; Cloud spent/reserved $0/$0; no build/dispatch.
Research input: `431c8d0d7a7e71e8c0ecba014ff89edbddb2ce42`; full G1R3/G1R2/G1R/G1 tasks and mandatory planner answer read.
Kani local test candidate: `6bb067476116704763502763984b225014dce221`; parent `02b734151ada1dd0d216b0db329776eb522d2d67`; author Tiramisu-Cake via -c; no Kani push.
Production unchanged: `3d085249c9c6c49a9c2e5747e2167d629748fb70`; only two test/golden files changed (+5/-5).
Four negative mem::forget calls → intrinsic forget; moved-from u32 reads and 70-failure golden unchanged; G1 Move source invalidation retained (SWEEP.md).
ManuallyDrop rejection: property owner/index → std::mem::ManuallyDrop::<U>::new.unsupported_construct.1; same reason, FAILURE and 0/1 summary.
All 23 G1 fixtures swept for std/core wrapper paths; intentional G2/unsupported controls retained; B artifacts and all other fixture bytes untouched.
A3 selectors: uninit/g1-union-pointee-negative/main.rs; uninit/g1-union-pointee-unsupported-reject_manuallydrop_union/main.rs; expected native PASS/PASS.
Expected Kani outcomes: negative 0 SUCCESS/70 FAILURE, manuallydrop 0 SUCCESS/1 FAILURE with exact intended diagnostic; actual outcomes UNKNOWN until GO/run.
RUN-REQUEST.json SHA-256: `2f5bdab60569918095f22b818bc403c572b0973f40f11ab6b1051022ddc675c5`; owner k1-merge, kind kani-tests, request kani3300-g1r3-a3-targeted-20261111-01.
Patch kani3300-g1r3-a3-build.patch SHA-256: `59e556e7942bf717107a6ff293fef66b13d3e3994d8c931ec8dba7f8c2e41e87`; full P1+G1 production + only selected fixtures/helper.
Native pin `f046b70644e113be0df9c22c2e6ea44a65a57566`; tooling KT2 `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c` unchanged.
Applied tree `1faeb244d2b054393141ce971180cdc2a5b6e64e`; 12 paths, diffstat 836 bytes ≤4096; inventory binds every production/source/golden/helper byte to candidate.
Explicit git apply --check --index on clean f046, existing KT2 validate/prepare-kani, all G1 rustfmt --check --edition 2024/repo config, git diff --check PASS.
Timeout proposal 5 min +30 overhead: (5+30) × $0.0135 = $0.4725 ≤ $0.476 remainder; prior $0.3240 + proposal = $0.7965 ≤ G1 cap $0.80; no reservation.
Independent review: Luna HIGH, no scoped static findings (REVIEW.md binds candidate/spec/packet/sweep); compiler/native NOT_RUN, proof credit NONE.
No phase/slot/ledger opened, root request installed, build/dispatch/Cloud, Actions/PR/issue/comment or Kani publication. Stop after package publication; await coordinator GO.
