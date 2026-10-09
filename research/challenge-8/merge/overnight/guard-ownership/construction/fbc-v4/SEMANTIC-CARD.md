# Exact construction → full canonical FBC roundtrip fragment V4

Written before implementation in AFTERNOON-MERGE-GUARD-CLOUD-2026-10-09.
Profile `copy-on-drop-source-construction-canonical-fbc-fragment-v4`.

Observed: V3b constructor is PASS_FRAGMENT_ONLY on stock/six with full CURRENT
array-owner roundtrip. The actual Drop geometry diagnostic reaches canonical
FBC/own opens but cannot yet establish root geometry. Canonical post/glue are
separate blockers. No actual Drop-bearing constructor is proved.

This candidate closes one concrete preceding obligation: after the exact
source279 initializer and checked full-own close, close the GENERATED canonical
`CopyOnDrop_full_borrow_content<T>(t, &drop_guard)()` from that existing own and
actual guard field/padding resources; reopen it, then perform the same CURRENT
source/destination/foreach own roundtrip and prove the unchanged full normal
constructor post. Add only two ghost statements; no new runtime operation,
algorithm/signature/model/kernel/prelude/extraction reinterpretation. The ghost
address designates the actual initialized local guard, not an invented object.
If the tool cannot produce its physical memory resources/address provenance,
that is an INCONCLUSIVE blocker; never assume fields/padding from bytes or own.

Generated FBC body remains nonprecise and exactly src/dst/len field chunks,
struct padding and by-value own. Closing consumes exactly those existing
physical resources plus existing full payload-own; reopening recovers them
without copying an owner. The CURRENT array binder must be the same list used
by foreach. All V3b pre/normal/unwind, pointer/nonoverlap/native length facts,
full arrays and owner resources unchanged. Positive-stride generic T/len>=2
supplied entry state only; actual seed/sort4/sort8/insert_tail acquisition OPEN.

Use an isolated constructor fragment with exact private struct and **no Drop
implementation**, exactly as V3b. Success proves construction/FBC packaging only;
it cannot transfer to the actual Drop-bearing type or callable safe Drop until
same-source actual callee/canonical compatibility/full payload post/glue are
proved. Memory resource formation is checked, not inferred from shape support.
Stock/six results and full-profile trust remain separate.

Gates: exact source/blob/block/statement and ghost-stripped runtime; MIR aggregate
from original parameters/no calls/drop/cleanup; non-False full own None and
canonical FBC None/3fields/padding/aggregate-own; exactly own-close → FBC-close →
FBC-open → own-open → CURRENT-array+same-foreach assertion → own-close, using
the SAME t and local-address &drop_guard in both FBC operations. No assume,
leak, extra proof axiom or post weakening. Positive complete normalpost/return/
leak/no-dead/source/refinement. Matched false after allthose transitions must
refuse only at its exact runtime-body location. Setup/precision/header/stack/
address/resource/admission failures remain INCONCLUSIVE, no negative credit.

Self-review: FBC is a definition over physical guard memory plus owned payload,
so ordinary checked close/open suffices if actual constructor produces matching
resources. It neither presumes that condition nor removes payload from own.
This resource transition is useful independently of unresolved self geometry;
it adds no general safe-Drop/compiler glue theorem or entry snapshot identity.
