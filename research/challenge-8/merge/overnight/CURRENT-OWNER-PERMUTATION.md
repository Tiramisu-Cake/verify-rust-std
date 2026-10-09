# Current-owner transposition resource fixture

## Contract and scope

This fixture targets one conditional ghost resource operation, not the
SmallSort caller or actual merge. For native mathematical `usize` indices
`0 <= i < j < n`, an already-owned source array with its **current** value list
`vs`, and an initialized disjoint destination whose current list is exactly
`swap(vs, i, j)`, transfer the existing `<T>.own` sequence once from source to
destination. The source post retains its exact bytes without `T.own`; the
destination post retains its transposed bytes and has exactly that owner
sequence. Equal-valued elements remain allowed. This is a full-value
transposition, not key equality, a callback snapshot, or a runtime copy.

The positive domain requires positive `size_of::<T>()`, valid alignment,
non-null/in-limits pointers and one-past endpoints, checked `n * size_of::<T>()
<= isize::MAX`, nonwrapping byte-span endpoints, and disjoint source/destination
ranges. It carries `type_interp<T>`, `type_interp<F>`, current `F.own`, thread
token, and all domain/frame resources through both normal and unwind posts;
unwind is false because the body is ghost-only. Generic `T` remains in scope,
but ZST is explicitly excluded.

The proof uses the source and destination `array<T>` predicates for their
unchanged byte lists and a separate `foreach(vs, <T>.own(t))` for the linear
owner sequence. Checked list recursion replaces one owner at `j` with the
current owner from `i`, returns the displaced current owner, then closes the
transposed sequence. Every helper must have an expected body. No helper may
assume list permutation, key equality, or a trusted ownership bridge. Keep
source bytes separate from owner resources throughout.

The first full f0b1ff62 attempt reached `transposition_owner_replace_at` in
both stock and experimental profiles, then refused while closing the first
`foreach` head: `No matching heap chunks: own0(T_typeid, t)(h0)` at pinned
`list.rsspec`'s recursive `foreach` expansion. The fixture now has two checked
adapters, `transposition_owner_open` and `transposition_owner_close`, to move a
selected resource between the generic `own::<T>(t)` predicate wrapper used by
`foreach` and the direct `<T>.own(t, value)` form. Exchange opens the selected
head before it becomes the displaced owner, and repacks the displaced value
before rebuilding the list predicate. This keeps the same unique current owner
and adds no axiom. A fresh hosted run must include both adapter bodies in the
expected-body inventory; this draft is untested.

## Gates

The positive case must retain full source and destination lists, prove exact
`swap(vs,i,j)` destination correspondence, and return the same owners exactly
once with all framing resources unchanged. A same-domain entry negative places
its first `assert false` at the predeclared `TARGET` columns 16–21 so the
existing pointer harness can establish reachability independently of the
resource theorem. A second-owner retention assertion is calibration only until
a hosted run shows that its diagnostic is the intended missing `<T>.own` VC;
it is not a required negative result before that calibration.

The f0b1ff62 `current_owner_transposition_double_owner_calibration` case was
blocked earlier by a multiline annotation parse error, before its intended
duplicate-owner assertion. Its multi-command body now uses one block annotation
instead of continuation lines of `//@`, and it explicitly opens the selected
wrapper so a future diagnostic can reach the second direct `<T>.own` request.
It remains calibration-only until the intended missing-owner VC is observed.

Acceptance requires every positive/helper body, normal return, leak, source,
and refinement gates; no dead code; exact target locations for the negative
and any later calibrated control; and the native-`usize` bounds above. Even a
green result proves only this conditional transposition of existing resources.
It does not derive destination bytes from the actual merge, establish a caller
Freeze/share bridge, prove callback framing, or establish actual SmallSort
safety.

Pinned parser review rejects open/close of nested own::<T>(t)(value). The draft
adapter bodies now use its supported direct <T>.own(t,value) family syntax;
req/ens still expose the wrapper-to-direct resource obligation. The translator
constructs its generic owner with that direct type predicate and its foreach
with partially applied own::<T>(t), but their checked conversion is NOT assumed.
Fresh helper-body PASS is required before any wrapper or negative credit. If
that direct open cannot consume the wrapper chunk, localize its exact missing
predicate rather than adding an ownership axiom or dropping resource posts.
