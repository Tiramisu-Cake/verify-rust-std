# Snapshot stop — conditional repair design, NOT_APPLIED

Committed W11 intake `ebd77a955b2b8d1b4e8079cfbf569386bcf0b130` establishes
**required AFTER evidence absent** at merge_count, after supervisor
`ProcessLookupError: [Errno 3] No such process`, cutoff supervisor_exception,
cleanup SIGTERM and worker exit-15. The group remains IN_PROGRESS with matching
source_before/request and complete BEFORE binary snapshot; source_after,
tool_fingerprints_after, binary_identity, execution and original group exception
were not durably published. snapshot_errors=[] covers before only. Actual
changed bytes, individual missing/unreadable file, after digests/existence and
throwing syscall/path/traceback remain UNKNOWN. See INTAKE-UPDATE.md. W11 owns
the ONE artifact intake; only its committed summaries were consumed here.

Select the **capture/finalization/error-diagnostic branch** below for a later
candidate. First retain the precise supervisor operation/exception/epochs and
durable interruption/snapshot availability records. A disappearing-process sample
is a source-supported possibility, not an established /proc pathname or race
site. If a specific benign process-lifecycle race is then established, handle
only that case with PID/start-time/ownership checks and rejection of recycled
or unknown identities. Do not blanket-catch ProcessLookupError as success.
Cleanup verified=true does not supply missing after snapshots or qualification.
No generated-output exclusion or broad dirty-check relaxation is justified by
this intake. An unmeasured post-state continues to stop the campaign globally.

Pinned control635 `r5_campaign.root_outcome` (lines166–173) conflates missing or
unequal request/source-before/source-after, binary_identity != MATCH and
snapshot_errors under `source_tool_request_binary_snapshot_drift_or_unavailable`.
It is a fail-closed guard, not proof that a particular immutable file changed.
`runner.verify_source` checks HEAD/tree, clean production checkouts, file digests,
source anchors and gates. Binary captures have BEFORE_CHILD and
AFTER_CHILD_SHUTDOWN phases; `fingerprints_match` rejects absent/malformed/error
records as well as different exact binary path/hash maps. Capture error must not
erase original child/compile exit, signal, timeout or exception.

| W11 establishes | Smallest future response | Admission boundary |
|---|---|---|
| Actual immutable source/tool/request/binary bytes or path binding drift | repair the responsible preparation/mutation or binding; retain global stop and fresh pins | no allowlist of changed executable/source; no retry unchanged |
| An exact legitimately generated output was included in immutable/clean classification | classify ONLY that proven output at its controlled invocation path, preferably place outputs outside immutable checkouts; retain/hash its own manifest | no broad target/**/untracked ignore, no arbitrary path exclusion |
| Required capture missing/unreadable, early-return path skipped after capture, malformed/missing receipt | repair finalization/capture coverage and typed reporting, always after shutdown/reaping | unmeasured identity remains UNKNOWN/global stop |
| Wrong epoch/previous-root receipt used | bind invocation/root/stage and epoch explicitly, compare immutable pins within same invocation; retain prior seals | no copying a prior MATCH or re-baselining changed bytes |
| Generic label plus incomplete before/after (actual R5: after absent) | preserve known before/guard inputs and add bounded operation/exception/epoch diagnostics in next authorized package; state residual UNKNOWN | do not declare exact syscall bug fixed or ask for a run solely to plan |

## Immutable inputs versus generated outputs

Freeze request bytes/digest, control/source/tool commits+trees, tracked source
and model/cfg/recipe files, selected binaries with resolved paths/digests, and
required source-binding anchors. Verify before child and again after full tree
shutdown/reaping; do not let compilation redefine the immutable baseline.

Compilation target directory, dummy crate, export JSON, rich properties, compile
and row receipts, temporary metadata and bounded streams are **potential output
classes**, not diagnosed R5 offenders or automatically safe exclusions. Give
each generated class an exact invocation-owned root, allowed lifecycle and
write scope. Keep it outside pinned inputs where feasible. Resolve path traversal,
symlink/collision and executable substitution fail-closed; check that an output
cannot shadow an input. Seal completed output manifests before later roots;
recheck those seals. Generated does not mean unverified or freely mutable.

Use epochs E0 pinned preparation/installation baseline; Ei.pre before root i;
Ei.post after shutdown/reaping and protected snapshot capture; Ei.seal after
bounded evidence parsing/finalization. Immutable bytes must match E0/Ei.pre/
Ei.post. New outputs are recorded in Ei, never compared to absence at E0 as if
they were immutable binaries. Prior completed seals remain byte-identical.
Current snapshot/identity comparison must succeed before continuation; no local
root-error continuation through actual global drift/unavailability.

## What a future package must retain if absent now

Store a bounded structured diff with campaign/run/attempt and invocation/root/
stage IDs; monotonic capture times and epoch; expected/actual request SHA and
source/tool HEAD/tree; each tested path's logical role, resolved path, existence,
type/symlink state, readable/hash state, expected/actual SHA; binary required set,
capture state and original exception type/message/errno; which condition failed
and which were not evaluated. Preserve source_before/source_after separately,
including capture exception if either is absent. A top-level UNKNOWN must not
replace the known other fields. Record truncation/omission/completeness explicitly.

Keep the child's original exit/signal/termination reason and compilation state,
current supervision/containment/reaping result, completed-prefix seal and
interrupted-root receipt intact. Campaign elapsed is not compile elapsed. Later
roots get explicit NOT_RUN with the stop reason; deferred roots stay NOT_SELECTED.
Never overwrite R5 evidence, fabricate missing before/after, set download_verified
or retrospectively turn STOP into a local timeout/success.

The W11 record gives campaign1372.897125559s, worker3.561063614s and partial
compile-child0.695s; none is an exact successful compile duration. Earlier two
600wall roots had intact after evidence and continued. The snapshot guard fires
before local cutoff classification; supervisor_error would independently be
global even if snapshot checks passed. Preserve both causes, not only the first
generic guard. Durable interruption reporting must not fabricate measurement.

Future synthetic preflight matrix: unchanged inputs+generated output accepted
only in declared output lifecycle; immutable byte/path/binary drift rejected;
missing/unreadable/hash exception; null/array/wrong-type/partial snapshot;
explicit NOT_RUN; receipt missing before child; timeout/compiler error/parser
error; snapshot failure after failed child preserving its original error;
source-stage-target/request/invocation mismatch; same digest at wrong path;
symlink escape; prior seal mutation; disappearing process at each identified
sampling/signalling step with original operation/exception retained; worker
SIGTERM before final publication; cleanup exception and unreaped descendant.
Keep existing success/error/timeout/partial/fallback tests and native profile
gates. These controls are planned, not executed by W13. No check is disabled.
