# Current-owner transposition resource fixture

## Contract and scope

This fixture targets one conditional ghost resource operation, not the
SmallSort caller or actual merge. For native mathematical `usize` indices
`0 <= i < j < n`, an already-owned source array with its **current** value list
`vs`, and an initialized disjoint destination whose current list is exactly
`swap(vs, i, j)`, transfer the existing `foreach(..., own::<T>(t))` sequence
once from source to destination. The source post retains its exact bytes
without the owner sequence; the destination post retains its transposed bytes
and has exactly that owner sequence. Equal-valued elements remain allowed. This is a full-value
transposition, not key equality, a callback snapshot, or a runtime copy.

The positive domain requires positive `size_of::<T>()`, valid alignment,
non-null/in-limits pointers and one-past endpoints, checked `n * size_of::<T>()
<= isize::MAX`, nonwrapping byte-span endpoints, and disjoint source/destination
ranges. It carries `type_interp<T>`, `type_interp<F>`, current `F.own`, thread
token, and all domain/frame resources through both normal and unwind posts;
unwind is false because the body is ghost-only. Generic `T` remains in scope,
but ZST is explicitly excluded.

The proof uses the source and destination `array<T>` predicates for their
unchanged byte lists and a separate `foreach(vs, own::<T>(t))` for the linear
owner sequence. Checked list recursion replaces one owner at `j` with the
current owner from `i`, returns the displaced current owner in a singleton
`foreach`, then closes the transposed sequence. Every helper must have an
expected body. No helper may assume list permutation, key equality, or a
trusted ownership bridge. Keep source bytes separate from owner resources
throughout.

The first full f0b1ff62 attempt reached `transposition_owner_replace_at` in
both stock and experimental profiles, then refused while closing the first
`foreach` head: `No matching heap chunks: own0(T_typeid, t)(h0)` at pinned
`list.rsspec`'s recursive `foreach` expansion. The follow-up draft removes the
two unsupported wrapper/direct-owner adapters. `transposition_owner_replace_at`
now consumes and returns the canonical `foreach` resource, with incoming and
displaced owners represented as singleton `foreach` values. Exchange packages
the existing head as a singleton, moves it through the checked replacement
helper, then rebuilds the transposed list. The calibration case requests the
same singleton twice after extracting the current head. No owner conversion or
duplication is assumed. This draft is untested; a fresh hosted run must
regenerate and match its expected-body inventory.

## Gates

The positive case must retain full source and destination lists, prove exact
`swap(vs,i,j)` destination correspondence, and return the same owners exactly
once with all framing resources unchanged. A same-domain entry negative places
its first `assert false` at the predeclared `TARGET` columns 16–21 so the
existing pointer harness can establish reachability independently of the
resource theorem. A second-owner retention assertion is calibration only until
a hosted run shows that its diagnostic is the intended missing-owner VC;
it is not a required negative result before that calibration.

The f0b1ff62 `current_owner_transposition_double_owner_calibration` case was
blocked earlier by a multiline annotation parse error, before its intended
duplicate-owner assertion. Its multi-command body now uses one block annotation
instead of continuation lines of `//@`; the target duplicates a singleton
`foreach` request for the same current owner. It remains calibration-only until
the intended missing-owner VC is observed.

Acceptance requires every positive/helper body, normal return, leak, source,
and refinement gates; no dead code; exact target locations for the negative
and any later calibrated control; and the native-`usize` bounds above. Even a
green result proves only this conditional transposition of existing resources.
It does not derive destination bytes from the actual merge, establish a caller
Freeze/share bridge, prove callback framing, or establish actual SmallSort
safety.

The follow-up avoids the rejected nested `own::<T>(t)(value)` syntax and the
unsupported wrapper-to-direct conversion. Both helper contracts use
`foreach(..., own::<T>(t))`; singleton resources make movement of existing
owners explicit. Fresh helper-body PASS is required before any wrapper or
negative credit. If the pinned parser rejects singleton `foreach` operations,
retain the exact failure and revisit the resource representation without
adding an ownership axiom or dropping resource posts.
