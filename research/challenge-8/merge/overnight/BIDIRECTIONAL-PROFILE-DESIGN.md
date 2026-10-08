# Bidirectional merge length-2 profile — design before implementation

This is an experimental exact-source integration target. It adds no verifier,
exporter, refiner, primitive, or memory-model semantics. The only intended
extension is a hosted-only fixture preparer that inserts contracts and ghost
resource setup around exact function bodies already admitted by the pinned
SmallSort source gate.

## Source and trust boundary

The source authority is the complete `smallsort.rs` SHA-256, the three
function body digests accepted by `research/challenge-8/merge/stock-26.10/prove.py`,
and a separately pinned digest for `panic_on_ord_violation`. One isolated case
must contain the actual `merge_up`, `merge_down`, `bidirectional_merge`, and
`panic_on_ord_violation` bodies from that same file, so case extraction cannot
drop callees. The first two keep their
already accepted bounded C1 and callback-cleanup contracts; neither call may
be replaced with a bodyless summary. Runtime stripping must reproduce all three
merge bodies byte-for-byte. The panic callee carries only `req true`, normal
`ens false`, and unwind `true`, justified by its exact unconditional panic
body; no termination assumption is added. A local empty `FreezeMarker` declaration is a
signature adapter checked against the exact repository trait declaration; it
has no blanket implementation and grants no purity or functional property.

The proof domain is exactly `v.len() == 2`, positive `size_of::<T>()`, positive
alignment, representable source and destination two-element spans, valid
provenance bounds, and numerically disjoint source/destination spans. The
unsafe projection contract states the data pointer and length facts, then
requires two explicit source points-to chunks and one `T.own` for each current
source value; it requires two writable `points_to_<T>` option chunks and one
current `F` owner. Stock translator code lowers slice `as_ptr` to a fat-to-thin
cast `(v as *T)`, and lowers slice `len` to `ptr_len(v)` over pointer metadata.
The safe-caller realization remains separate: stock
`slice_ref_ty_info` represents `&[T]` ownership with `[T].share`, while the
accepted helper contract requires full element resources. This fixture does
not assume a `share`-to-`own` bridge or claim SAFE caller applicability.

Comparator answers and callback state changes are unrestricted. Required posts
retain the current two source values and owners and current `F` state. Normal
completion initializes both scratch cells and retains both source owners. On
panic, the destination option post distinguishes the actual stages: both old
options if the forward callback unwinds; first initialized and second unchanged
if the reverse callback unwinds; both initialized if the final guard panics.
Neither path creates `T.own` for scratch. The body’s odd-length path is still
present and checked as unreachable from the proved `len == 2` premise; it is
not deleted or assumed away. The actual `assume`, range construction,
`is_multiple_of`, terminal wrapping increments, and guard remain in the exact
body and are proof obligations.

This profile proves no ordering, permutation, stability, untouched-entry
equality, or general-length claim. It excludes ZST, aliasing source spans,
arbitrary invalid-byte destination states, and the caller derivation of the
allocation/range premises. It does not prove that every actual `T` satisfying
Rust's `FreezeMarker` bound has an implementation of the local adapter; the
empty marker is only a local type-shape adapter. The repository trait's
`Freeze` blanket implementation and any semantic stability argument remain
separate source-linked obligations.

## Hosted acceptance matrix

1. Source admission pins the source file, exact signatures and all three body
   digests, the exact repository `FreezeMarker` declaration, and the applied
   W1/M2/C1/callback/cleanup profile. Generated runtime bodies must match the
   admitted bodies after ghost stripping.
2. Diagnostic arbitrary-answer `len == 2` proof attempts both actual helper
   bodies, each real callback, both physical copies, and the terminal guard.
   Record current source/F ownership and normal two-cell initialization if
   those obligations pass. Since this domain makes the odd branch dead, a
   strict dead-code finding keeps the case diagnostic/INCONCLUSIVE.
3. A comparator-unwind case reaches the second actual callback after the first
   destination copy; record whether current source/F ownership and the expected
   partial destination post hold. The same restricted-domain dead-code finding
   prevents acceptance even if the unwind posts pass.
4. Negative controls remove one destination write resource and violate the
   explicit source/destination separation premise. Each must reach its named
   intrinsic precondition or target assertion; no guessed diagnostics are
   accepted. The host run records the actual first diagnostic before it is
   pinned.
5. Full combined regression reruns wrapping, pointer bridge, G2/A/B, callback
   cleanup, C1 controls, and unchanged-source identity in the same profile.

The first run must separately classify the real `intrinsics::assume`,
`usize::is_multiple_of`, and `0..len_div_2` Range/Iterator path. Setup or
unsupported-operation failures are not intended proof negatives and do not
justify changing those semantics. A checked loop invariant must preserve both
source owners, comparator owner, destination option resources, and the precise
cursor cases for the sole `len_div_2 == 1` iteration. The generated invariant
is only a candidate until hosted evidence links those cursor cases to
Range/Iterator state. Moreover, `len == 2` makes the odd-length branch
statically unreachable; the strict dead-code gate must report that finding.
This restricted profile is diagnostic only and cannot count as a full positive
while that branch is dead. Positive acceptance needs a broader length domain
that keeps the odd branch live and checks its copy/advance behavior.

The unwind destination-stage relation is expressed by a checked ghost
fixpoint using `match` on the two option values. Pattern variables such as
`some(?written)` are valid when binding a points-to chunk, but not inside a
pure equality expression; the hosted run exposed this syntax boundary at the
first unwind post. The fixpoint encodes the same three allowed cases: both
original options, first option initialized with second unchanged, or both
options initialized. It does not constrain a written value to an input value
yet; that stronger selected-current-value link remains an open obligation.

No fixture is accepted from frontend setup failure, unrelated helper failure,
unsupported syntax, a weakened postcondition, a removed source branch, or an
unintended dead-code result. The first hosted iteration is diagnostic until
every stage and predicate above is established.
