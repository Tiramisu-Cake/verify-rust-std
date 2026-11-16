# S1 grouped execution supplement

Task note `CH8-RUNNER-BATCH-NOTE.md`, g0 commit `82cc48368e1e3aec544975831bc9595d26f5781d`, replaces LIST2's per-row invocation requirement. Previous no-list control `801c2634cee3f3f39cb20146a1080e016a59e048` is superseded for dispatch. This stage prepares a new local control only; it does not authorize publication or CI.

## Grouping and exact flags

Stock Kani0aac adds every harness selector to compiler-local flags (`kani-driver/src/call_single_file.rs:180-186`), then passes these to all std crates (`call_cargo.rs:84-125`). A changed selector invalidates Cargo fingerprints. The task-supplied approximately5m22s compile observation is not independently re-read CI evidence here.

Retain all23 literal row records, selectors, oracles, source/variant pins and default unwind values. Group by `(variant, unwind)`:

| Group | Rows | Default unwind |
| --- | ---: | ---: |
| production | 15 | 34 |
| production | 3 | 5 |
| production | 3 | 4 |
| activation-default | 1 | 34 |
| activation-override | 1 | 34 |

Each group has exactly one `verify-std` invocation, repeated literal `--harness SELECTOR`, `--exact`, `--jobs=1`, `--harness-timeout 600s`, one export and the same cfg/features/CBMC args as its rows. No list, separate warm-up, only-codegen call or second compiler invocation remains. Variants get separate invocations and guaranteed overlay cleanup. Groups use a job-local Cargo target outside std_project's deleted dummy crate; this does not imply reuse across changed selector lists.

`check_control.py` projects each batch argv back to each old row's argv by removing other selectors and the newly added harness-timeout. The remaining argument list must be exactly identical to the prior pure argv constructor. This checks retained flags without running Kani.

## Compilation cap inside the same process

`main.rs:150-169,193-198` creates `std_project`, determines targets, writes the initial export, then starts harness execution. `frontend/schema_utils.rs:56-64,303-343` atomically emits an INCOMPLETE marker with tool identity, exact selection and harness timeout. Observe that marker as a conservative compilation-and-project-link boundary; do not parse free-form compiler log messages.

Each group starts an atomic `compile/receipt.json` with a900s compile limit. The process monitor accepts the marker only for the exact stock clean tool, schema, selectors/count/exactness, empty unmatched list and600s harness timeout. An observed COMPLETE export before the cap is also a valid upper bound when a very fast child finishes between samples. A missing, invalid or late marker cannot establish completion; the process is killed on the compile deadline and the compile receipt remains FAILED. Marker SHA, observed run state, elapsed upper bound, request/source/tool pins and bounded pipe head+tail previews are recorded. The receipt has no proof credit. Compiler/link diagnostics remain available in the bounded group capture as well.

There is no second invocation for compilation. The stock marker appears after project compilation/linking and before solver execution; the compile timer covers that whole preparation stage, including driver startup. Successful compilation does not validate any proof row. An interrupted proof group may have a COMPLETE compilation receipt and UNKNOWN proof outcomes.

## Per-entry binding and verdict

A terminal export must be COMPLETE with the exact requested filter sequence, exact=true, integer matched_count equal to group size, empty unmatched filters, and exactly one unique harness entry for every requested name. Extra, duplicate, absent or mismatched entries invalidate the group. Export order is irrelevant: map by exact full `name`.

For each row retain the previous manual/core crate, source file SHA and exact source line anchors, PFC target token comparison/generated-wrapper check, or explicitly null proof contract. Retain the existing configuration, effective unwind, tool version/fingerprint, property count, named negative assertion and cover checks byte-for-byte. Only selection/extraction changes. A timed-out, crashed, OOM, NOT_RUN or malformed harness remains UNKNOWN; it cannot satisfy a named negative oracle. In a complete export, unaffected harness records remain independently inspectable.

Driver exit belongs to the **group**, not a root. Record the original group exit/signal, leaving per-root driver exit unavailable. Require exit0 only if all exported harness outcomes are successful; otherwise require stock exit1. A positive root in a group containing an expected negative can still have its own EXPECTED export verdict. No result is inferred from aggregate exit alone. Truncated/partial/INCOMPLETE exports, killed groups, source/tool drift and overlay cleanup failures invalidate affected group rows. Subsequent groups do not launch after an infrastructure-fatal group failure.

The stock schema still lacks resolved PFC target DefId, target definition source location, AST/MIR target binding and named successful assertion descriptions. The explicit source-backed replacement/limits from the earlier no-list design remain. Grouping adds none of these missing forms of independent evidence.

## Wall and memory accounting

Stock `call_cbmc.rs:224-249` applies the600s timeout to CBMC output processing. Instrumentation precedes it (`harness_runner.rs:143-153`), so this is not a measured600s cap over all harness instrumentation/setup wall time. Receipts state that scope explicitly. No fail-fast flag is enabled; stock jobs1 runs harnesses sequentially.

The group budget is `900 + sum(row timeout_seconds)`; every frozen row remains600s. The unchanged4500s shared phase separately bounds total execution, with the existing10s cleanup reserve. Effective group process deadline is the lesser of its group budget and remaining phase. Starting a group with a shorter remaining phase does not lower Kani's per-harness600s timer: an outer phase cutoff kills the group and leaves UNKNOWN. A completed terminal export is still required. The job remains120min (setup30 + phase75 + fallback/upload15). Planning metadata330s compile/group plus2760s rows gives4410s; this is an estimate, not a runtime guarantee. Actual compilation durations and full completion remain unverified.

Before each group calculate available headroom from MemAvailable and, if finite, cgroup memory.max minus memory.current. Cap the sampled process group at `min(12GiB, available-2GiB)`; refuse launch if no positive cap remains. Record that snapshot, cap and sampled process-group peak.

**Per-root RSS is UNKNOWN.** The stock export has no exact link from sampled CBMC processes to source harness names. No sampled group peak is relabelled as a root peak or evidence of the6GiB/root condition. Root resource admission remains pending; observations have proof credit NONE. This is the explicit fallback permitted by the coordinator's supplement. Sampling can miss transient peaks, as with the existing process-group sampler.

## Durable bounded diagnostics and checks

Group, compilation and row receipts are atomic before launch and after observations/errors. The bounded pipe capture now flushes its live head+tail to disk, so a fallback can recover the last observed tail even without normal finalization. Each stream remains capped at1MiB; compile previews are <=2048 input bytes of head and tail. Rows reference/copy the shared group capture with its scope explicitly labelled, rather than claiming individual stdout/stderr. Fallback preserves completed receipts and marks in-progress group/compile/row work INTERRUPTED/UNKNOWN. Existing export8MiB and artifact256MiB caps remain; group-wide output caps are conservative limits.

Validation uses static source/argv/pin comparisons and small Python synthetic subprocesses/mocks only. It covers all23 rows in five calls, reversed export order, mixed positive/negative outcomes, missing/partial/null/wrong-type/duplicate/wrong-selection exports, individual timeout/NOT_RUN/wrong target, original group exits/signals, compile boundary/timeout/launch/RSS failure, source/fingerprint/overlay cleanup failure, memory headroom, phase cuts, fallback and live-tail durability. Actual cargo/rustc/Kani/CBMC and CI remain NOT_RUN; no proof obligations close.
