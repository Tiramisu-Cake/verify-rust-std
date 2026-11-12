# Coordinator-only first pair: R5-01/P1, then R5-02/P1

PREPARED, SOURCE_READY_NOT_COMPILED, NOT_RELEASE_CANDIDATE. Worker15 Cloud$0, dispatch0; no phase registration or CI authorization created here. Coordinator alone uses the existing authorized probe, owner/lane/queue/T0/ledger/slots/deadline/budget controls. No workflow/runner/backend changes or worker Actions/Cloud dispatch.

| Order | Direct R1 child | Exact tree | Input/root |
| --- | --- | --- | --- |
| 1 R5-01/P1 | `bcc1a2af3fe13599b88acabc78c33e1394407dc5` | `dd0a03763344b2a06a1582797323b90a894bd6f7` | P1 / postcondition_reads_initialized_return |
| 2 R5-02/P1 | `899ffb5f26b79e89cec1b7cc537d54be494ab390` | `67dad348591d0f662b783efc6da3a95a0e69b9ff` | same |

Local clone /root/kani-fix-3300-m2br5; root experiment/kani-3300-m2br5 stays at exact R1 `1cd96e354ec45346b61c245554a50a8af8cb5ce7`. Branches -hbuf/-hcopy and full patches/trees/runtime/patch hashes in DIAGNOSTIC-MANIFEST.json. Independently reconstruct each from R1 plus its patch, require exact tree; do not stack. Diagnostics are unpushed and have no skip-ci. Transport/reconstruction is coordinator responsibility; research push does not authorize Kani push or CI by worker.

Sequential **build/inventory→solver**, one root/process at a time, only this pair. First fork build validates real types, macro expansion, markers and -D warnings; B3 E0308/E0277 means source review/rustfmt cannot substitute. Source-stage-target-input binding must include actual changed path and retained transfer/transition use. Early frame/Unsupported/UB/read termination is recorded as a changed-obligation outcome, never equal-obligation relief; do not silently patch frame/DFCC/compiler or promote solver/job success to proof. A failed build is SETUP_FAILURE, solver NOT_RUN; incomplete binding is INCONCLUSIVE. A diagnostic solver can only be interpreted with those losses and bound actual use, never as release admission.

## Frozen command contract (inherited m2br3 template)

P1 `research/challenge-8/kani-k1/kani3300/m2a/cases/scalar-pfc-legal.rs`,774 bytes, SHA256 `fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b`. Root `postcondition_reads_initialized_return`; unchanged PFC/input/useful ensures17/first=true. P2 and all other inputs/baselines are HELD, no new history runs.

```json
["kani", "<isolated-path>/scalar-pfc-legal.rs", "--crate-name", "m2br", "-Z", "uninit-checks", "-Z", "function-contracts", "--output-format=regular", "--harness", "postcondition_reads_initialized_return", "--exact", "--keep-temps"]
```

RUSTFLAGS=`--edition 2021 -D warnings --emit=mir`. Only source/tree/runtime/patch manifest deltas differ. Match actual argv/env/target/toolchain/sysroot/CBMC/solver/checks/unwind/object-bits/slicing/inlining and defaults across pair and established baseline receipts. Source-built binary identities intentionally differ, record them. Pins in INPUTS are source declarations, not installed-binary receipt. Return actual compiler/link/goto-cc/goto-instrument/CBMC/solver argv and effective env/flags/hash/version. Codegen inventory may add existing --only-codegen, label it pre-DFCC; do not label it post-DFCC. Existing saved post-DFCC inventory only. m2br3/CBMC-RECIPE is non-solving reference, not normal solver argv modification.

Existing timeout300s/watchdog>6GiB unchanged; report sampling interval/overshoot/timestamp/PID vs process tree/raw RSS units/limiter coverage and original exit/signal/exception by stage. No head/SIGPIPE or swallowed exits, no toolchain/flag repair hidden in retry. No raw/full logs or archives downloaded/read; use bounded supported evidence/receipt interface only, explicit pagination/coverage. Missing/capped data UNKNOWN.

## Required bounded receipt per candidate

- Exact source commit/tree/runtime/patch/input/root/toolchain/recipe/target and artifact/index/file identities; total/exact/complete/coverage/cap. Build status separately from job/parser status.
- GOTO bytes/units, functions/property counts/classes and eloc. Actual retained stores/loads/return0/index/layout/normal continuation, by-ID and pointer-wrapper paths, source guard/decline/retarget/bless span, width/operator counts. Bind source-stage-target, not path/hash alone.
- Actual private state/assigns/write/havoc/snapshot ranges. R5-01 unmarked Option buffer/lifetime/reset loss vs R5-02 R1 marked scalar state. No R4 A extension. Inventory false-value preservation/lost paths and early frame/Unsupported/overflow/read termination.
- Symex steps, VCC before→after, conversion entry/end/time, printed variables/clauses only if present, SAT-entry separately. Peak RSS/raw units, exit/signal and last phase. VCC counts are not failed-property totals.
- **Full bounded failure inventory** with IDs/class/location/status and total/coverage/cap, preserving overflow/frame/Unsupported/UB/uninit failures. Missing full inventory/retained paths stays UNKNOWN. Job/parser SUCCESS and archive integrity are not semantic PASS, B2 proof or independent credit.

Compare model size/actual retained use separately from verdict/resource cutoff. No monotonicity, equivalent speedup, causal production fix or group-exclusion inference from early path loss. Task-reported R4 A/B/C and V02 facts are in INPUTS/ABLATION-PLAN; no new evidence claims here.

After this pair return coordinator handoff before choosing/publishing/running any third/fourth candidate. ABLATION-PLAN's second-step tree is unexecuted; no automatic matrix/bisect, unused-slot spending or repeat identical tree/argv. Future compile dependency repair requires explicit new commit/request and scope; diff outside mem_init.rs is STOP. Release/M1/M2/S3/work14 unchanged, M3 HELD; legal-pair+postcondition-hole and frame/false controls await resource gate/current candidate. No diagnostic release cherry-pick or proof credit.
