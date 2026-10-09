# Isolated guard construction fragment

Status: prepared, unrun diagnostic. This card precedes code. The exact source
is `smallsort.rs:295-299` (private three-field `CopyOnDrop<T>` declaration) and
the physical statement `:279`, `let drop_guard = CopyOnDrop { src: scratch_base,
dst: v_base, len };`. The fragment deliberately excludes the actual `Drop`
implementation. Its only proposed theorem is that this exact constructor
statement packages separately supplied current resources into a non-False
`CopyOnDrop<T>.own(t, result)` with identical `src`, `dst`, and `len` and
`len >= 2`. It says nothing about destructor behavior, compiler drop glue,
`mem::forget`, the whole caller, or safety of generic Drop. The complete actual
type/Drop compatibility gate remains OPEN and cannot inherit fragment credit.

Input contract: thread token; positive-size T; `2 <= len`; valid aligned,
bounded, disjoint source/destination ranges; `[?f]scratch_base[..len] |->
?src_values`; `v_base[..len] |-> _`; and the **existing**
`foreach(src_values, own::<T>(t))`. The exact non-False `OWN` body in the
parent `prepare.py` is reused verbatim. Neither initialized bytes, pointer
addresses, nor sharing create new T owners. The result contract preserves the
thread token and returns the same payload exactly once inside guard own,
including the equality of all three runtime fields. Unwind post is `false`.

Preparation pins the full repository SmallSort SHA/Git blob, the exact private
struct bytes, and the exact source statement bytes/line. For each case,
original and verified Rust differ only by ghost annotations; stripping them
recovers the identical fragment runtime source. A positive and a matched
`assert false` immediately after construction use the same full pre/post.
No weakened contract or additional trusted tool patch is used.

MIR admission must find one constructor body, one struct aggregate producing
`CopyOnDrop`, the source-located construction line, and a return path. It must
refuse **any** MIR Drop terminator, call terminator, or unwind path in this
fragment. A compiler insertion of such a path invalidates this subset theorem.
AST admission must identify the same runtime constructor body and non-False
own with two array points-to resources, current `foreach` owners, and the
source-located aggregate. The positive requires exporter/decode/VeriFast/
refinement success, body execution, return and leak checks, and no dead-code
record. The negative counts only at its exact false coordinates after entry
and before return/leak; setup, frontend, geometry, or unrelated failures are
inconclusive. Full logs and exact profile/source hashes are required.

Self-review: removing `Drop` changes only this isolated research fragment's
type context, so it cannot be transported to the actual destructor or caller.
The expected useful result is a conditional owner-packaging fact for the
physical constructor statement. It leaves the pinned kernel, frontend,
prelude, copy summary, runtime std source, and original direct Drop proof
untouched. No local fixture generation or verifier execution is permitted.

## Cloud diagnostic integration plan (unrun)

The extracted wrapper is `unsafe fn source_guard_construction`, matching the original constructor statement inside the caller’s `unsafe` block; removing its ghost annotations restores the identical runtime fragment. This does not add runtime behavior or a Drop implementation.

The construction fragment is integrated as two separate opt-in groups,
`guard-construction-fragment-diagnostic` and
`guard-construction-fragment-stock-diagnostic`. They consume only this
fragment's `prepare.py`/`prove.py` pair, run under the existing experimental
six-component and stock profile homes, and publish separate raw evidence
folders. The runner first completes source preparation and the mandatory
profile smoke checks. Each group is capped at 180 seconds overall, with each
exporter/decode/refinement stage capped at 30 seconds and VeriFast at 35
seconds. Tool homes and profile evidence are reused from the same retained
build exactly as for the existing guard diagnostic.

The outer audit must retain both case classifications and all stage reports,
source hashes and ghost-strip equality, MIR and AST admission gates, exact
constructor statement execution, and the intended first-body false target.
Completion means only that all required evidence was collected. The diagnostic
is always `accepted: false`, including if both cases match; an `INCONCLUSIVE`
first diagnostic is reportable and does not invalidate artifact completeness.
It must remain isolated from the existing direct-Drop two-case checker and
must not imply Drop glue, caller, normal `mem::forget`, or unwind compatibility.

The two groups are known to selection validation but remain unselected until
an explicit future selection decision after current Cloud results are
reviewed. Inclusion in the recipe pins only the exact runner, card, preparation
and proof inputs; it does not authorize dispatch. The committed `selection.json` gains no selected group from this integration, and existing group checks or acceptance gates remain unchanged.
