# Resumed preparation review — worker15

Coordinator accepted section-2 STOP and deferred marker diagnostics to separate work on
2026-11-13; see [REQUIRED-STATE.md](REQUIRED-STATE.md), unchanged. The remaining docs/mode
fixtures are prepared for coordinator review/CI, not claimed verifier acceptance.

Base remains `ee2695e5a2c4c2d8ead7a511e0f3f6f2a9a95677`; isolated source branch
`fix/kani-3300-marker-modes`. Production/compiler/runtime and `contract.rs` are unchanged.
No blanket guard/exemption, new private static/target, any_modifies/Arbitrary(MU) change,
assert-to-assume rewrite, hook pairing, mode selection, checks or S3 change was made.
Worker14's scopes and shared compiletest/schema were not touched.

Exact source changed files:

- docs/src/reference/experimental/contracts.md
- tests/json-handler/uninit-contract-mode-boundaries/README.md
- tests/json-handler/uninit-contract-mode-boundaries/config.yml
- tests/json-handler/uninit-contract-mode-boundaries/observe.py
- tests/json-handler/uninit-contract-mode-boundaries/recursive.rs
- tests/json-handler/uninit-contract-mode-boundaries/replace.rs
- tests/json-handler/uninit-contract-mode-boundaries/roots.json
- tests/json-handler/uninit-contract-mode-boundaries/run.py
- tests/json-handler/uninit-contract-mode-boundaries/test.sh
- tests/json-handler/uninit-contract-mode-boundaries/test_observe.py

Validation: 13 synthetic Python observer/collector tests PASS, including missing export/build,
partial/crashed/OOM/timeout, stale evidence, selection/metadata drift, status/count mismatch,
weakened checks/profile and process-group cleanup. Invocations are mocked; no Rust/Kani/CBMC
is executed by these tests. Python AST/static source/manifest checks PASS. Scratchpad rustfmt
PASS for both Rust files with repository config. Initial formatter invocation lacked its shared
library path; corrected invocation succeeded. Formatter is not a typecheck. TYPE-AUDIT.md maps
Rust/macro/CLI/JSON APIs and safe source payload guards.

Six verifier roots: NOT_RUN; source→transformed body/mode/transfer binding, lawful prefix and
per-root property mapping: BINDING_PENDING. No negative golden is invented. Collector PASS means
only complete observations plus successful legal companions; target modes remain unqualified,
even with particular SUCCESS. Unsupported/frame/path gaps are explicit, not qualifying negatives.

Public docs/fixture README link the accepted note at research commit cee401ec22bd96e2b91733e6e2a275618b55f37e.
It is a prepared cross-repository reference; publication remains coordinator-owned (no push here).
Source/changed-file hashes are in INPUTS.json; CI-REQUEST.md proposes six roots/caps for approval.
Quick r6 remains coordinator-reported history. Common gate, M3/platform/SmallSort: NOT_RUN here.
No local cargo/rustc/Kani/CBMC/Miri/builds, CI, raw evidence reads or push occurred. Cloud $0.
