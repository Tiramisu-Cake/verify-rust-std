# Isolated guard construction fragment

Status: Build 742d inconclusive; reassessment below. This card preceded code. The exact source
is `smallsort.rs:295-299` (private three-field `CopyOnDrop<T>` declaration) and
the physical statement `:279`, `let drop_guard = CopyOnDrop { src: scratch_base,
dst: v_base, len };`. The fragment deliberately excludes the actual `Drop`
implementation. Its only proposed theorem is that this exact constructor
statement packages separately supplied current resources into a non-False
`CopyOnDrop<T>.own(t, result)` with identical `src`, `dst`, and `len` and
`len >= 2`. It says nothing about destructor behavior, compiler drop glue,
`mem::forget`, the whole caller, or safety of generic Drop. The complete actual
type/Drop compatibility gate remains OPEN and cannot inherit fragment credit.

The initial v1 input contract was: thread token; positive-size T; `2 <= len`; valid aligned,
bounded, disjoint source/destination ranges; `[?f]scratch_base[..len] |->
?src_values`; `v_base[..len] |-> _`; and the **existing**
`foreach(src_values, own::<T>(t))`. The initial v1 experiment reused the exact
non-False `OWN` body in the parent `prepare.py` verbatim. V2 changes only the
source-array permission to full, as specified below. Neither initialized bytes, pointer
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

## Build 742d reassessment before any repair

Both profiles' positive and first-body-false cases exported and decoded MIR,
and refinement succeeded. VeriFast failed first at `verified/lib.rs:33,5-6`:
`Precision check failure: variable patterns not supported as coefficients`.
The location is `[?f]v.src[..v.len] |-> ?src_values` in the precise custom
`own(t,v;)`, before entry to the constructor body. Thus all four classifications
are correctly `INCONCLUSIVE`; neither negative is at its target. No
proof-level construction conclusion follows.

The custom own is precise because its generated field/padding/FBC use requires
two input parameters. Its arbitrary existential source-read fraction in the
body is incompatible with this frontend precision check. A fixed/full fraction
would narrow the supplied source resource, and a nonprecise predicate changes
the type-own interface; neither is silently substituted. An `exists(?f)`
assertion followed by `[f]` might change only binding syntax, but its
precision/admissibility is unestablished and would be a calibration probe,
not evidence of a bridge. Exact original own remains unchanged pending a
phase decision on that probe or architecture.

The evidence also exposed two *admission-only* mismatches independent of this
precision failure: compiler MIR creates `_5`, `_6`, `_7` from the three
parameters before the exact `CopyOnDrop` aggregate; the gate compared them
directly with parameter locals `_1`, `_2`, `_3`. The AST lowers the aggregate
to three source-located `AssignExpr` field initializations, not a
`CastExpr/InitializerList`; the returning own is `ExprCallExpr(TypePredExpr)`,
not `CallExpr`. Gate repairs may trace exact ordered local origins,
initializer fields, and returning own structurally without changing any
source annotation, target post, or proof claim. All four saved cases must
show the same shapes before changing the gate; any new shape fails closed.

## V2 scoped full-source proposal (recorded before preparation change)

The next independently named profile supplies the **full initialized source
array permission** at entry. Its local precise own stores that same full
source array, the entire writable destination array, and the unchanged
current-element `foreach` owners. The constructor pre replaces only
`[?f]scratch_base[..len]` by the full source array, with every other pure
premise/resource and the complete normal/unwind posts retained. This is a
strictly narrower, conditional constructor fragment, not a result for
arbitrary source fractions. The old v1 source/evidence remain identifiable
through their hashes; the parent fractional own and direct Drop contract are
unchanged. No source-array permission or owner is discarded, fabricated, or
inferred from bytes. Whether the actual caller can supply the full source
array remains OPEN. Generic Drop/FBC and original complete caller remain
OPEN as above. Positive and first-body-false controls rerun on Cloud with a
new profile identity; the first error and all full stage logs determine the
next decision.

## Build 9ed4 outcome: V2 remains at the precision interface

All four V2 cases (experimental/stock × positive/first-body-false) have
exporter, MIR decoder, and refinement exit 0, unchanged source hashes at
every stage, and VeriFast exit 1. Each has the same first and sole error at
`verified/lib.rs(35,5-12)`: `Preciseness check failure: callee is not precise.`
Line 35 is `foreach(src_values, own::<T>(t))` within the precise custom
`CopyOnDrop<T>.own(t,v;)`. The full source-array permission removed V1's
coefficient-pattern error, but did not make the generic element-owner
iteration precise. No constructor body segment or source statement executed;
both matched-false controls fail before their intended assertion. All four
are `INCONCLUSIVE`, and there is no owner-packaging theorem.

The saved MIR and AST admissions are true in each case: exact three-field
struct and source aggregate; ordered argument-to-temporary-to-field links;
no MIR Drop/call/cleanup path or Drop implementation; non-False own with
both array resources and `foreach`; full supplied pre, full normal field
equalities and own, and literal false unwind. These structural gates do not
override the VeriFast precision rejection. The V1 fractional case and V2
full-source case are both open at different precision checks.

A future admissible route must first define a precise, generic representation
of **all current element owners** that preserves their identity and
one-time transfer, with a separately reviewed justification that the
generated FBC can consume and return it. That requires a new semantic/trust
decision and regression gate before any frontend, kernel, or prelude change.
It must then prove the exact physical constructor against its full post and
matched false control; independently discharge the actual Drop callee's
full safety proof and FBC post, self geometry, caller supply of the required
array/owners, normal forget, unwind, and compiler drop-glue paths. None is
established by Build 9ed4. No deletion or replacement of `foreach`, owner
assumption, imprecise own, or further local proof patch is authorized here.
