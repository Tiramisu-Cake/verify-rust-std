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

## Gates

The positive case must retain full source and destination lists, prove exact
`swap(vs,i,j)` destination correspondence, and return the same owners exactly
once with all framing resources unchanged. A same-domain entry negative places
its first `assert false` at the predeclared `TARGET` columns 16–21 so the
existing pointer harness can establish reachability independently of the
resource theorem. A second-owner retention assertion is calibration only until
a hosted run shows that its diagnostic is the intended missing `<T>.own` VC;
it is not a required negative result before that calibration.

Acceptance requires every positive/helper body, normal return, leak, source,
and refinement gates; no dead code; exact target locations for the negative
and any later calibrated control; and the native-`usize` bounds above. Even a
green result proves only this conditional transposition of existing resources.
It does not derive destination bytes from the actual merge, establish a caller
Freeze/share bridge, prove callback framing, or establish actual SmallSort
safety.
