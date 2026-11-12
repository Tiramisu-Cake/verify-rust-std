# Coordinator-only R6 queue

PREPARED / SOURCE_READY_NOT_COMPILED / NOT_RELEASE_CANDIDATE. Worker15 Cloud$0, dispatch0. No phase registration, Actions/Cloud dispatch or workflow/runner/backend changes. Coordinator retains existing owner/lane/ledger/T0/deadline/budget/slot controls.

| Sequential order | Direct R1 child | Exact tree |
| --- | --- | --- |
| R6-01/P1 | 25197eb23e9d4b0d6b69d69ff21c2de135bdda7c | 075e7f06a5ab1ab3a2cac36e866d4413045308f3 |
| R6-02/P1 | 258d6af1ea44411ec3f3aa0a4921c05c3700d6f9 | 4d7d4757bf276f68060c335ebac80922ba00e41f |

Local clone /root/kani-fix-3300-m2br6; root experiment/kani-3300-m2br6 stays at R1 1cd96e354ec45346b61c245554a50a8af8cb5ce7. Siblings -epoch-u/-repr-u are unpushed. Reconstruct independently from exact R1 plus full-index patches, check manifest tree/runtime/patch identities, never stack them. Both diagnostic commits have no skip-ci; transport is coordinator responsibility. Research push does not authorize worker Kani push/CI.

Only this two-run queue, sequential **build/inventory→admitted solver**. Reuse existing R1/R5-01 receipts; no P2/new baselines/retry/full matrix or third candidate. First build checks actual types/macro expansion/-D warnings. Build error is SETUP_FAILURE with solver NOT_RUN; cutoff INCOMPLETE, incomplete binding INCONCLUSIVE. Numeric relief after changed/early failures is not a causal fix.

P1 research/challenge-8/kani-k1/kani3300/m2a/cases/scalar-pfc-legal.rs,774 bytes, SHA256 fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b; root postcondition_reads_initialized_return. Same PFC/input/useful ensures17/first=true as existing receipts. Frozen R5/m2br3 command contract:

```json
["kani", "<isolated-path>/scalar-pfc-legal.rs", "--crate-name", "m2br", "-Z", "uninit-checks", "-Z", "function-contracts", "--output-format=regular", "--harness", "postcondition_reads_initialized_return", "--exact", "--keep-temps"]
```

RUSTFLAGS=`--edition 2021 -D warnings --emit=mir`. Match actual argv/env/target/toolchain/sysroot/CBMC/solver/checks/PFC/uninit/object-bits/slicing/inlining/unwind/defaults with established receipts; only manifest source deltas. Source-built binary identities differ and must be recorded. Return actual compiler/link/goto-cc/goto-instrument/CBMC/solver argv, effective env/flags/version/hash. Source pins are not binary receipts. Existing only-codegen inventory is pre-DFCC; use existing post-DFCC inventory without relabeling. Existing bounded property/type query recipes allowed; no new exporter/runner/framework/broad trace. Diagnostic show-vcc is not full verification.

Existing timeout300s/watchdog>6GiB unchanged. Preserve sampling/overshoot/timestamp, PID versus process tree, raw RSS units, limiter coverage and original stage exits/signals/exceptions. No head/SIGPIPE, swallowed exits or hidden retry repair. No raw/full logs/archives/equations or Cloud Logging; use supported bounded receipt interface/Brief with explicit returned pagination and exact/complete/coverage/cap identities. No-match/cap means UNKNOWN, never NOT_RUN by inference.

Required per candidate:

- Source commit/tree/runtime/patch/P1/root/toolchain/recipe/target and GOTO/artifact/index/file hashes; GOTO bytes/units, function/property counts/classes/eloc, stage identities and coverage. Job/parser status separate from build/solver outcome.
- Retained selection0 guard and continuation, reset actual location relative to frame/havoc/snapshot, store/load match/layout and false transfer; pointer-versus-ID consumption, marked/unmarked write/assigns ranges and retained DFCC targets. Early frame/Unsupported/invalid-source/overflow/uninit paths must remain visible.
- Symex steps/VCC before→after, ConvertSSA start/end/runtime, printed vars/clauses when available, separate SAT-entry; peak RSS/units, limiter/exit/last phase.
- Complete bounded Failed Checks inventory: IDs/location/class/status, total/exact/complete/coverage/cap, preserving frame/Unsupported/invalid-source/overflow/UB/uninit failures. Missing inventory or retained paths UNKNOWN; VCC count is not failure count.

Source predictions, reported R5 endpoints and observed R6 bindings remain separate. ABLATION-PLAN gives conditional intervals only; any follow-up requires new coordinator handoff. M3/integration/heavy M2/P2 remain HELD, no release rollback or proof credit. Stop after this reviewed pair.
