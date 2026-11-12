# Coordinator-only M2-B/R4 request

PREPARED / NOT_COMPILED / AWAITING_COORDINATOR. Worker15 Cloud$0, dispatch0, local compiler/verifier/build0; no workflow/runner/backend edits. This package does not register a phase or authorize worker CI. Coordinator uses existing authorized lane/queue with unchanged owner/T0/slots/deadline/ledger/budget restrictions. One P1 root/solver process per admitted variant; max3 modified variants total. No P2, U/R1/V01/V02 reruns, extra baseline solving, M3 activation, model repair or release integration.

First obtain existing V02 complete bounded failures/phase receipt as queried in RUNTIME-MAP; existing metadata response is preserved in V02-BOUNDED-RECEIPT.json. Empty artifacts and step SUCCESS leave semantic gate UNKNOWN, including possible frame/Unsupported/UB. Do not fetch raw logs/archives or new history reruns to fill it. Missing projection stays precise UNKNOWN and does not make changes equivalent.

| Order / variant | Exact local commit, direct child of R1 | Required admission before one normal solver |
| --- | --- | --- |
| A/P1 | 75090c4986016d872976c52ed85a472fab354d44 | Build/types/markers first, inventory both distinct declared private objects and actual emitted lambda targets with extents/write operations; comparable transfer/frame obligations. One missing target, no uninit model, early frame/Unsupported or absent reached delta -> no comparable solver admission |
| B/P1 | 2983edc2a05d95e56889c597ccf0eb1c3c23a0d0 | Build/types then actual changed usize operators, widths/guards and overflow check inventory. Can admit only as explicitly changed-obligation diagnostic, never equal-obligation speedup |
| C/P1, conditional only | 8ebc167850b4f4ff11a940c1bceeb21daff1fa84 | FIRST hunk applicability on existing retained projection, then build/inventory if justified. Establish count and source-match/decline/destination overlap guard. If both changes unreachable/equally simplified, C DEFERRED with no CI solver slot. If projection unavailable, solver remains DEFERRED; do not spend slot merely on speculation |

A's empty assigns list can mean both symbol lookups failed, not just no instrumentation. Its empty-or-two source assertion alone is not admission. Require two independently inventoried targets; zero/one/unresolved/missing target -> SETUP_OR_INVENTORY_FAILURE, no comparable solver admission or resource-relief claim.

All source-ready commits are unpushed in /root/kani-fix-3300-m2br4; root branch experiment/kani-3300-m2br4 is exact R1 `1cd96e354ec45346b61c245554a50a8af8cb5ce7`. Reconstruct siblings independently from R1 + patches/A.patch, B.patch or C.patch and require manifest tree/hash, or use explicitly authorized coordinator-local commit transport. Never stack them. A's runtime delta and ancillary contract.rs delta have separate numstat in manifest; two-target registration is necessary dependency, not a free cost reduction. R1 Uninit emission and existing model marker signatures stay frozen. No diagnostic push, skip-ci diagnostic commit, release cherry-pick or fourth variant.

## Frozen input and command template

P1 source: ../m2a/cases/scalar-pfc-legal.rs,774 bytes, SHA256 `fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b`; exact root `postcondition_reads_initialized_return`. Copy original bytes; useful ensures ==17 and first=true stay unchanged. PFC remains PFC, no alternate no-assert root. P2 root postcondition_reads_returned_hole is HELD.

Validated template inherited unchanged from m2br3/CI-REQUEST.md:

```json
["kani", "<isolated-path>/scalar-pfc-legal.rs", "--crate-name", "m2br", "-Z", "uninit-checks", "-Z", "function-contracts", "--output-format=regular", "--harness", "postcondition_reads_initialized_return", "--exact", "--keep-temps"]
```

RUSTFLAGS=`--edition 2021 -D warnings --emit=mir`. Build first validates actual types, macro expansion and -Dwarnings; source audit/rustfmt/Luna are not compilation. --only-codegen inventory stops before DFCC and must be labelled pre-DFCC. Later inventory must use existing saved post-DFCC model, not relabel codegen as post-DFCC. No compiler/verifier invocation by this worker.

Match actual target/sysroot/toolchain/CBMC/solver/checks/PFC/uninit/object-bits/slicing/unwind/inlining/flags and all input bytes to existing baseline receipts. Source pins declare nightly-2026-10-23 and CBMC6.11.0; installed hashes/version, effective defaults and full argv require coordinator receipts, not inference from pin. Source-built binary hashes intentionally differ by candidate. Record compiler/link/goto-cc/goto-instrument/CBMC/solver argv and env; do not silently repair pins or change flags after setup failure. Separate m2br3/CBMC-RECIPE.md is non-solving only, supports bounded source/VCC/type queries; its --show-vcc/property selection is NOT a modification of normal solver argv.

## Receipt, controls and resource limits

Existing timeout300s/watchdog RSS>6GiB remain. Return sampling interval, overshoot and raw RSS units, process PID vs tree scope, timestamp/milestone, original stage exit/signal, last phase and limiter coverage. Do not stop output with head/SIGPIPE or swallow failure. Keep existing bounded capture cap; report complete inventory via bounded pagination with total/exact/complete/coverage/cap, never a full log/formula. Build failure -> SETUP_FAILURE, solver NOT_RUN. Cutoff -> INCOMPLETE. Missing data -> UNKNOWN; parser/job SUCCESS or simply FAILED is not the semantic gate.

Per variant: source SHA/tree/input/root/recipe/artifact/file identity; GOTO byte size and units, total property count/class inventory and eloc; symex steps and initial/retained VCC; ConvertSSA start/end/runtime; printed variables/clauses (UNKNOWN if not printed), SAT-entry separately from Passing problem to/Running; peakRSS and exit/signal by stage. Return full bounded failed-check inventory with IDs/class/location/status and coverage/cap, including all extra overflow/frame/Unsupported/UB/init checks. Bind actual retained expressions and widths to source as in RUNTIME-MAP, preserving changed guards/counts/paths and many-to-one mappings. Properties and VCC totals are different populations, never subtracted as failed checks. Retained operation/condition loss is diagnostic, not equivalent speedup.

No public/user modifies extension, assume, extra disable_checks, wrapping/saturating arithmetic or layout/object-width truncation. No goldens weakened. Required later release gates remain P1 useful ensures PASS, P2 first payload-read intended uninit FAIL, legal modifies PASS, out-of-frame write frameFAIL, false-source/ordinary/typed controls plus P1/P2/legal/frame matrix. M2-B/S3 restricted Quick reported unit5/0,kani22/0,expected135/0/2ignored,ui14/0,script1/0 at candidate4f64cc617c/run43257528539/CI fc3bccbfff; legal-pair and postcondition-hole were excluded. This is not heavy PFC/full gate. After a separately proved resource repair, current M1/M2/S3 integration and both selectors must be restored in a new task. M3 HELD; proof credit0 here.
