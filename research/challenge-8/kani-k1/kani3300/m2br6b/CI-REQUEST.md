# Coordinator-only M2-B/R6b path gate and matched comparison

PREPARED / SOURCE_READY / NOT_COMPILED / NOT_RELEASE_CANDIDATE. Worker15 Cloud$0, dispatch0. No worker Kani push, CI dispatch, phase registration or workflow/runner edit. Existing coordinator owner/lane/ledger/T0/deadline/budget/slots and original stage exits remain authoritative. This request does not itself admit a solver run.

Local clone `/root/kani-fix-3300-m2br6b`; two unpushed branches/commits only. Reconstruct each full-index patch from its own exact parent, verify manifest runtime/compiler/tree/patch hashes. Do not stack candidates. Diagnostic commits have no skip-ci; coordinator owns any authorized fork transport.

| Order | Configuration / exact source | Parent | Tree |
| --- | --- | --- | --- |
| 1 | R6-02b /405c1f059264d8f7cedeeaa01c6d4ad6867a419e | 258d6af1ea44411ec3f3aa0a4921c05c3700d6f9 | 162e8ad1e76e842b18c24a4ac2986335902834d7 |
| 2 | R1+same-skip /56cbc5c4a479bc3fb25310b14fcf279d90581a02 | 1cd96e354ec45346b61c245554a50a8af8cb5ce7 | a97ec3d06efd827829f550f1e7a98f29538758fe |

First build and singleton inventory R6-02b, then admitted solver. Only after eliminating the early initializer Unsupported, use R1+same-skip as the second matched P1 configuration, also build/inventory before admitted solver. At most2 normal solver invocations in total. No P2, new variants, baseline reruns, automatic retries or heavy matrix. Build error => SETUP_FAILURE, solver NOT_RUN; cutoff => INCOMPLETE; incomplete path/comparison => INCONCLUSIVE/NON_COMPARABLE. Parser/job success is separate from proof verdict.

## Frozen input and command contract

Reuse `m2br6/CI-REQUEST.md` at54252f16e48bf5e08f4eaad2fc36ee07a75c4325 without setting changes. P1: `research/challenge-8/kani-k1/kani3300/m2a/cases/scalar-pfc-legal.rs`,774 bytes, SHA256 fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b, singleton root `postcondition_reads_initialized_return`. Keep source bytes unchanged, including useful ensures17/first=true; no cover or source rewrite to expose paths.

```json
["kani", "<isolated-path>/scalar-pfc-legal.rs", "--crate-name", "m2br", "-Z", "uninit-checks", "-Z", "function-contracts", "--output-format=regular", "--harness", "postcondition_reads_initialized_return", "--exact", "--keep-temps"]
```

RUSTFLAGS=`--edition 2021 -D warnings --emit=mir`. Reuse established actual argv/env/target/toolchain/sysroot/CBMC/solver/PFC/uninit/checks/unwind/object-bits/slicing/inlining/defaults. Only compiler source delta and the matched runtime endpoints differ. Record actual expanded compiler/link/goto-cc/goto-instrument/CBMC/solver argv, effective environment/flags, version/hash and host/target/object widths. The JSON above is a command template; actual expanded argv and binary identities are currently UNKNOWN, not reconstructed from source pins. Save them through the existing bounded receipt/Brief interface with file/index/request identities and exact/complete/coverage.

Use existing preflight/build/inventory recipes; only-codegen inventory stays labeled pre-DFCC, retained PFC inventory post-DFCC. Existing bounded property/type/location recipes are allowed, without new exporter/runner/framework or broad traces. Diagnostic show-vcc is not full verification. No raw/full logs, archives, equations or Cloud Logging; follow supported explicit pagination. Missing/capped fields stay UNKNOWN; no-match is not NOT_RUN.

Existing timeout300s and watchdog>6GiB unchanged. Preserve sampling interval, timestamps/overshoot, PID versus process-tree scope, RSS units, limiter coverage, original exits/signals/exceptions and phase limits. Do not hide retries, suppress failure statuses, truncate with head/SIGPIPE or alter assigns to hide new failures.

## Mandatory emitted-path gate

For R6-02b bind the harness-entry initialize call, its actual Option=None reset and continuation through retained target/select/store/load/return0 to the useful ensures payload read/assertion **after reset**. For R1+skip bind the corresponding active=false reset and same useful transfer/postcondition path. Preserve actual reset position relative to frame/havoc/snapshot. The artificial initializer Enum Unsupported must disappear; any remaining frame/Unsupported/invalid-source failure must be visible.

Obtain function/block/instruction/location/property IDs and guards plus available path feasibility/reachability evidence. Source call presence, retained locations or property listings alone do not establish execution/feasibility. If no stronger evidence is available, mark the gate UNKNOWN and resource comparison incomplete. If the ensures assertion simplifies away, give an explicit simplification/path binding to the original payload-read/postcondition; silent missing property is not acceptance.

Bind mandatory selected_argument==0 branch and continuation, store/load index and layout checks, false-state transfer, pointer-versus-ID consumption and source validity/lifetime. Bind retained DFCC targets and marked/unmarked write/assigns ranges: this compiler skip does not make ARGUMENT_BUFFER automatically verifier-private. User uninit/pointer/valid-value checks must remain under their original policy; distinguish removed initializer instrumentation from useful target checks.

Counts are sanity indicators, not exact equality gates: full prior P1 models had order10^4steps and hundreds of properties/VCC (R5-01 11639steps,476→182VCC; R6-01 11167steps,563→162VCC). Removal of private instrumentation can change counts. Repeating approximately1049steps and the sole Unsupported fails the path gate; it is not a cheap comparable model. Low counts with missing/early paths also require explanation before attribution.

## Required bounded report per configuration

| Field group | Required receipt / current worker observation |
| --- | --- |
| Source/input/build | Full source/tree/runtime/compiler/patch/P1/root/recipe/toolchain/target identities; build exit/status and stage identity. Current build NOT_RUN. |
| Emitted artifacts | GOTO hash/bytes/units, function/property counts/classes/eloc, pre/post-DFCC labels, artifact/index/file hashes and coverage. Current UNKNOWN. |
| Path gate | Initialize/reset/guard/continuation/ensures/transfer/frame bindings, simplification if relevant, available feasibility evidence and gate verdict. Current UNKNOWN. |
| Resource milestones | Symex steps, VCC before→after, ConvertSSA start/end/runtime, printed vars/clauses, SAT-entry separately, peak RSS/units, PID/scope/limiter/exit/last phase. Current UNKNOWN, solver NOT_RUN. |
| Failure inventory | Bounded complete Failed Checks IDs/location/class/status plus total/exact/complete/coverage/cap; preserve frame/Unsupported/invalid-source/overflow/UB/uninit failures. Current UNKNOWN. |

Source predictions are in REPAIR-BINDINGS; historical R6 outcomes in INPUTS are coordinator-reported, not new observed evidence. Do not overwrite historical verdicts or infer independent B1/B2 credit from archive integrity, exit0, counts or parser success.

If R6-02b converts while comparable R1+skip stays heavy, the distinguishing Hrepr experiment is restored, without identifying which representation/lifetime/private-membership component causes it. If both convert, self-instrumentation is substantial or changes paths and prior Hrepr attribution must be reconsidered. If repaired candidate still stops early, investigate that new boundary in a separate handoff, without continuing bisect. Early failure/missing feasibility makes semantic/resource comparison incomplete in every case. M3/integration/heavy M2/P2 HELD, proof credit0; STOP after this reviewed pair.
