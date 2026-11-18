# Snapshot stop — conditional repair design, NOT_APPLIED

Actual changed field/path, before/after digests, missing snapshot or original
capture exception: **UNKNOWN pending committed W11 intake**. No current filename
or causal diagnosis is asserted here. W11 owns the ONE compact artifact intake;
this source-level proposal does not duplicate it.

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
| Only generic label survived, no exact before/after | add bounded structured mismatch/error record in next authorized package; state residual UNKNOWN | do not declare known bug fixed or ask for a run solely to plan |

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

Future synthetic preflight matrix: unchanged inputs+generated output accepted
only in declared output lifecycle; immutable byte/path/binary drift rejected;
missing/unreadable/hash exception; null/array/wrong-type/partial snapshot;
explicit NOT_RUN; receipt missing before child; timeout/compiler error/parser
error; snapshot failure after failed child preserving its original error;
source-stage-target/request/invocation mismatch; same digest at wrong path;
symlink escape; prior seal mutation; cleanup exception and unreaped descendant.
Keep existing success/error/timeout/partial/fallback tests and native profile
gates. These controls are planned, not executed by W13. No check is disabled.
