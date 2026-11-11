# KANI3300 G1R2 — PRE-BUILD REVIEW
PREPARED, NOT AUTHORIZED; Runtime Codex; one static stage; Cloud spent/reserved $0/$0; no build/dispatch.
Research input: `a62ad2d47dafb905e7f70c39199c96634fc15db8`; task TASK-KANI3300-G1R2.md read in full; inherited G1/G1R/planner constraints retained.
Kani test candidate: `02b734151ada1dd0d216b0db329776eb522d2d67`; parent/unchanged production `3d085249c9c6c49a9c2e5747e2167d629748fb70`; author Tiramisu-Cake via -c; local commit, no Kani push.
Test-only delta (5 files, +35/-29): positive/main.rs — 2 unsafe union reads, 15 explicit ManuallyDrop borrows; negative/main.rs — 2 unsafe union reads, 8 explicit borrows.
reject_manuallydrop_union/main.rs — explicit (&*p) retains wrapper guard; reject_union_transmute/main.rs — local same-size union definition retains generic transmute safety guard.
reject_init_predicate/expected — exact observed intrinsic-owned property; same FAILURE/reason/harness/summary; source rationale and coordinates in TEST-SWEEP.md.
All 63/70 harness expectations and aggregate goldens retained; manifest body/hash updates follow repairs; only predicate property binding changed. No assertions/reads/checks removed or lint allows added.
Static sweep covers all 23 G1 fixtures, 154 harnesses and types.inc; TEST-SWEEP.md ≤40 lines; pinned nightly sources identified in RUST-SOURCES.json. Compiler/native/lint execution NOT_RUN; proof credit NONE.
Native pin `f046b70644e113be0df9c22c2e6ea44a65a57566`; tooling KT2 `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c` unchanged; slug kani3300, owner k1-merge, kind kani-tests.
Package A request `kani3300-g1r2-a-targeted-20261111-01`; same 20 selectors, flags, require_success, diagnostic requirements and test_timeout_seconds=150 as G1R A.
RUN-REQUEST.json SHA-256: `dc67daf8fce5fad977c38329133748923ebddd375924275d7537c07205f5f006`.
kani3300-g1r2-a-build.patch SHA-256: `7c277d4226960f7f5907790aa9fe3022dc06567525a2ef33d0fc88747b71153b`.
Applied tree: `f0ac57ef6ddfc8d5b24454faef807439212abc0e`; 48 paths; diffstat 3013 bytes ≤4096; APPLIED-INVENTORY-A.json binds all bytes.
Complete P1 + G1 production against f046 equals unchanged production candidate; every selected source/golden/helper equals test candidate. Explicit git apply --check --index on clean exact f046 PASS.
Unchanged KT2 validate + prepare-kani PASS; preflight-a.json records tree. Permitted rustfmt --check --edition 2024/repository config passed for all 24 Rust/include files; git diff --check PASS.
Timeout proposal 16 min +30 overhead: (16+30) × $0.0135 = $0.6210 ≤ remaining $0.6245; prior G1 spend $0.1755 + proposed reserve = $0.7965 ≤ cap $0.80. No reservation made.
Package B artifacts, request, fixtures and manifest entries remain unchanged; no B preparation, authorization or execution in G1R2; separate owner GO required.
Independent review: Luna HIGH found no static blocker; REVIEW.md binds exact test candidate/spec/packet and TEST-SWEEP.md; compiler/native NOT_RUN. Historical G1A/G1RA evidence and accounting remain unchanged.
No phase/slot/ledger opened, request installed, Cloud reservation/submission, Actions/PR/issue/comment, or Kani publication. Stop here; dispatch awaits coordinator GO.
