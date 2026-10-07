# Pointer MaybeUninit ownership and actual callee phase

Owner authorization 2026-10-07; entry e0920ecb07cd05ef08acd6fb5a2fb228af9a1f98.
IN PROGRESS. This is a NEW phase; previous 4584 unused seconds are retired.
New budget 5400 summed hosted job seconds, <=1800/job, <=300/proof;
one active relevant workflow_dispatch. Initial spend 0; no active run.

Scope: checked value ownership for MaybeUninit<*const Element>, SAFE actual
source-local constructor body, exhaustive typed MIR applicability, full intended
positive/negative/classifier/stock-experimental Rust/C/C++ regression matrix,
then source-linked actual select_unpredictable diagnostic. Runtime std, generic
signatures and other specializations remain unchanged. No general unions,
alias/borrow, copy, FnMut, Drop or unwind outside the constructor extension.

## Definition and trust review BEFORE ownership implementation

For this exact thin raw-const-pointer specialization, define resource ownership
of wrapper v by examining the EXISTING logical option inner(v):
none => emp; some(p) => raw_ptr_own<Element>()(t,p).
Stock rust_belt/general.rsspec defines raw_ptr_own<T>()(t,v;) = true;
translate_raw_ptr_ty likewise interprets raw pointer value ownership as True.
Thus each branch has empty resource content. The branches do not equate values:
inner(new_maybe_uninit(some(p))) is some(p), and inner of the same constructor
with none is none. No initialization axiom for the existing opaque uninit()
is added. A value with unknown inner remains unknown, never assumed initialized.

The constructor returns exactly some(input POINTER VALUE), including whatever
provenance the frozen pointer model represents; no conversion to address-only
integers is permitted. Owning this value grants no pointee cell, nonnullness,
alignment, read/write permission, allocation or lifetime. Thread token is a
separate generated SAFE obligation, not part of wrapper ownership. Element has
no Copy/Freeze or pointee premises. The imported ManuallyDrop expression uses
the existing pinned wrapper identity rule, not a new memory bridge.

Implementation choice: a named DEFINED predicate in the experimental lib.rsspec
and exact type-wide translator ownership dispatch (not a function exception).
Only std::mem::MaybeUninit with the sole *const Element argument in the certified
unit uses it; all other applications keep the existing opaque own behavior.
The legacy explicit generic type-predicate interface stays conservative/opaque;
this phase does not introduce generic ownership of MaybeUninit<T>. The automatic
SAFE ownership dispatch itself must require the defined predicate and prove it.
No opaque introduction lemma, unsafe signature or removed safety template.

New trust delta from translator-only cbf7b7da: this ownership definition and
exact-type dispatch, plus exhaustive MIR dataflow admission. Existing kernel,
memory/provenance model, prelude, exporter/schema/refinement checker and frozen
26.09 source809de459/nightly-2026-02-05 target x86_64 remain unchanged. The new
patch/profile has its own hash and never combines the fieldless-layout or old
FnMut/Drop/tuple patches. Acceptance is experimental component acceptance,
not organizer admission or whole-model soundness.

## Acceptance and decisions

Source SHA/blob, exact copied body/fields/signature/SAFE contract and source
spans bind local copy to pinned repository. Exporter path strings do not encode
crate hash/opaque DefId identity: this is a declared source-equivalence trust
link. Full MIR gate must check identities/types/generics/params/operands/active
field/calls/local declarations and exact acyclic call-to-return graph, rejecting
unknown/additional forms BEFORE enabling any new rule.

Positive: SAFE prototype compatibility; named body execution; exact inner;
thread token; no unwind; return/leak checks; call without pointee permissions;
separate fractional pointer and independent scalar frame preserved. Initialization
distinction and unaffected unrelated specialization controls supplement this.
Proof negatives (valid certified body): wrong inner, assert false, false post,
duplicated permissions, each solely at its marked predicate/location after body
execution. Applicability negatives: source changes and MIR operand/return/active
field/type/binding/extra operations; each fails its named admission condition,
never counted as a proof negative. Controls run with rule enabled. Classifier
mutants must fail closed. Stock/experimental Rust/C/C++ regressions stay separate.

Only full acceptance removes feasibility-only and permits the dependent actual
callee. Then retain N6 body, two external constructor sites, three intrinsics,
guards/drop/forget/assume_init, full selected-pointer/frame/no-unwind posts.
Report first actual remaining blocker and stop if outside this scope. Routine
implementation/harness fixes authorized autonomously; every new run tests a
specific correction/hypothesis. Source change requires NEW exact-SHA dispatch.
No SWO/layout repetitions without dependency. RAPx CLOSED/NO-GO; B/C NOT RUN.

Results and ledger: [results](SORT4-POINTER-OWNERSHIP-RESULTS.md), STATUS and
EXPERIMENT-LOG; full logs/artifacts outside git. Final commit/push required.

Implementation O1 profile patch SHA256
`31d3ca507cc7ec4a090ef45330b0f3758c1fbcdbbb4c68d66c256166801d6aea`: translator
and bin/rust/std/lib.rsspec only; complete MIR typed two-block graph and full
source-span endpoints; no parser/kernel change. Acceptance pending hosted run.

O2 correction: explicit own in constructor post plus an ordinary kernel-checked
introduction lemma WITH BODY against the same defined predicate. Its exhaustive
option split closes raw_ptr_own only for some; no pointee access. Certified
aggregate emits ghost call after assignment, leaving runtime/MIR graph untouched.
This is proof annotation in translation, not an assumed opaque bridge. Acceptance
requires named lemma/body/return/leak evidence and full matrix. Patch023e12f0;
O1 retained at137s, first body not reached. See journal/result identifiers.

O3 completes HIR/plain-parameter kinds/names/drop flags/spans, union variance/
Sized/variant/field kinds/visibility/spans and exact exported SAFE contract text
and all source coordinates. Complete operation graph remains unchanged. New MIR
controls directly mutate HIR/contract/binding in addition to operations/types.
Classifier distinguishes precise applicability exit2 from proof exit1 and requires
exact reason/frontend/refinement/integrity; integer positive transports original
opaque ownership, integer missing-own negative targets SAFE prototype. Semantic
predicate/checked introduction unchanged. Profile patch325af428 (full SHA in runner).
