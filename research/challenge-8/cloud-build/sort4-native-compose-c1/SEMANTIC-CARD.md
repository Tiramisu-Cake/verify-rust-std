# Native entry to first comparator: experimental composition card

Status: preimplementation design for independent review. This card grants no
tool-profile acceptance and records no new proof result. The assigned
select-sort4 session begins 2026-10-10 00:34:15 UTC; main deadline 02:34:15,
absolute finishing deadline 03:04:15. The current `WORK-POLICY.md` revision
was read in this worktree at session start; its source revision will be pinned
with the next checkpoint.

## Actual obligation and useful boundary

The actual std source is
`library/core/src/slice/sort/shared/smallsort.rs`, pinned blob
`40939f922bcb6fdc7ee0d30427fa861827043827`. The source caller
`small_sort_general_with_scratch` has the first `sort4_stable(v_base,
scratch_base, is_less)` call at line 254; `sort4_stable` has the first
comparison `let c1 = is_less(&*v_base.add(1), &*v_base);` at line 620.
Fresh 46bb proves the native source/F/current-thread resource subset and
opaque scratch frame; fresh 65d6 proves an actual-source bounded c1 first
callback under a stronger raw contract. Those are separate theorems.

The next useful theorem is an internal, callable *c1-only* function containing
the exact first comparator operation and its checked lifetime/ownership
recovery, with the complete source array/F/thread contract but no destination
permission. It splits source4 from the unchanged tail, recovers and rejoins
the four **CURRENT** values and owners on both outcomes, then appends them to
that tail. Its normal and direct-Continue unwind posts return the complete
current source array/owners, current comparator cell/`F.own`, and thread
token. Stock `produce_type_interp<T/F>` occurs inside this real helper and
both chunks are explicitly leaked after recovery on both outcomes. It neither
reads nor writes `dst`, and its contract does not mention destination storage.
All four source cells and both callback outcomes are retained. No equality to
entry values is assumed after the callback. The unchanged-tail claim requires
an explicit checked assertion of the tail value/owner frame on each outcome;
without it, only the existential CURRENT full-array post is credited. The
checked `recover_pair` and
`join_four_owned_cells` helpers must verify before their caller in the same
exact source unit. The helper's ordinary executable Rust body terminates
after c1; therefore its verified contract can legitimately be used by a
separate caller. The prior AST-truncated actual `sort4_stable` cannot be used
as a callable summary and remains unchanged.

A separate native diagnostic keeps the exact
`small_sort_general_with_scratch<T: FreezeMarker, F: FnMut(&T,&T)->bool>`
signature and its generated complete safe-entry contract. It copies the
original read-only `len`, `v.as_mut_ptr`, `len/2`, and scratch-pointer
operations with byte-exact header/statement offsets against the pinned full
std source, then explicitly checks a restricted non-ZST `len>=8` domain
before calling the verified c1-only helper. This is an artificial diagnostic
branch, **not** the original caller CFG, scratch abort guard, inline-const
selection, or actual sort4 call. Its positive result would show that the
native source4/F resources plus the helper's stock type interpretation
can enter and exit a checked c1 callback while restoring the complete native
normal/unwind return and leak posts. The entire original `MaybeUninit<T>`
scratch array/owners remain opaque and framed through the call. The helper's
raw pointer `dst` argument, if retained solely for source signature mapping,
must carry no T destination heap premise and must not be dereferenced.
The current source draft has no `dst` parameter at all and uses an internal
`len` argument solely to carry the native tail frame across direct unwind;
this is an internal interface, not the actual sort4 signature.

Domain: arbitrary safe native `v`, `scratch`, F and T at function entry;
the diagnostic c1 operation executes only in the stated `len>=8 &&
size_of::<T>()>0` subset. Positive size is explicit and excludes ZST from
the callback proof; the standalone native resource lemma continues to admit
ZST. No `Copy`, purity, callback nonpanic, or entry-value preservation
restriction may be added. The actual sort4 and caller full generic/ZST
obligations stay open. The helper's safety proof must retain all source
pointer provenance/limits and owner resources; a numerical pointer equality
cannot generate permission.

## Semantic boundary and source applicability

Prefer a proof-source-only internal helper and frozen existing translator
profile. If a narrow frontend/projection repair is necessary, it is a new
experimental semantic component: write its exact source/MIR/AST identity,
falsifiable rationale, trust assumptions and affected regression gates here
before implementation, then obtain independent review. The patch may only
recognize the pinned helper and first direct-Continue comparison; it cannot
change stock contract semantics, memory/alias rules, kernel, refinement,
unwind, leak or dead-code checks. Default-off behavior and the existing
whole-sort4/c2 mandatory refusals remain unchanged. An AST transformation
must preserve every reachable prefix path and all original outcome posts;
it must not replace the complete `sort4_stable` proof by a c1 summary.

Exact source binding must compare the helper's single executable comparison
with the pinned original c1 expression and operand order, and separately
retain the previous full `sort4_stable` source/MIR/AST certificate for the
actual bounded theorem. Both normal and readonly typed MIR must show the
single `FnMut::call_mut` from source cells 1,0 with direct `Continue` unwind,
no cleanup/Drop path elision. Normal and unwind proof AST/trace must show
debt close, strict lifetime exit, pair recovery and four-cell join before
their respective posts; same-unit callee verification precedes native use.

## Falsifiable test and decision

Positive: source-linked c1-only helper VF0 with full CURRENT normal/unwind
posts, and native diagnostic VF0 with complete generated normal/unwind posts,
return, leak and intact opaque MU frame. The stock callback and helper
verification logs, paired MIR, refinement, and source/AST mapping are
required evidence. One negative removes a comparison-debt resource and must
fail first at the checked recovery precondition after target entry. Separate
false normal/unwind posts must fail at their respective post obligations;
source owner loss must fail at the four-cell join or native post, not in
setup. Mutated source operands, call count, unwind edge, or unbound C2
annotation must be refused by admission. Existing C1 strict controls and
default-off full-target behavior remain regression gates when the semantic
overlay changes; tests are isolated so unrelated helpers cannot block the
baseline.

If the helper passes but native entry fails, classify the first source/owner/
type/frame/post blocker and repair only within the scoped profile. If the
native theorem passes, the next work is actual caller CFG guards and eventual
whole `sort4_stable` result; this result alone proves neither. If a new
ownership bridge, MU inverse, ZST model, or unrestricted whole-function
summary is required, stop and return the material decision to the owner.

Compilation, extraction, refinement and proof run only in the assigned
Cloud Build lane with exact proof/infra/tool identities. No Actions dispatch,
local toolchain execution, std runtime edit, or external publication.
