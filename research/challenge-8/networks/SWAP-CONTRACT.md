# `swap_if_less`: compositional contract and proof boundary

This note specifies the actual helper at
[`smallsort.rs`](../../../../library/core/src/slice/sort/shared/smallsort.rs:386)
as the component needed by `sort9_optimal` and `sort13_optimal`. It is a
research contract, not a verified Rust summary. The adopted `sort4_stable`
contract in [`../SORT4-CONTRACT.md`](../SORT4-CONTRACT.md) is useful precedent
for separating unrestricted safety from conditional ordering, but its scratch
copy protocol does not prove this helper's read-and-two-copy implementation.

## Actual body and state transition

For `p = v_base.add(a_pos)` and `q = v_base.add(b_pos)`, the body first calls
`is_less(&*q, &*p)`, obtaining `swap`. It then selects `q,p` for the first
source and `p,q` for the second source when `swap` is true, and selects `p,q`
for both when false. It performs, in order:

```text
tmp = ManuallyDrop::new(ptr::read(second_source))
ptr::copy(first_source, p, 1)
ptr::copy_nonoverlapping(&*tmp, q, 1)
```

For distinct non-ZST slots and unchanged values, `swap == false` leaves `(p,q)`
as `(old_p,old_q)` and `swap == true` leaves them as `(old_q,old_p)`. The first
copy permits overlap and is a self-copy in the false case. The second copy is
from the local temporary to `q`; its non-overlap with that local object is a
separate memory premise. The temporary is deliberately not dropped. This
description follows the body; it does not replace `select_unpredictable` with a
source rewrite in a proof.

## Unrestricted safety contract

Safety has no ordering, purity, `Copy`, or `Freeze` premise. Let `n` be the
logical length of the allocation addressed by `v_base`. A sufficient
precondition is:

* `a_pos < n` and `b_pos < n`; both `add` operations are in-bounds for this
  allocation, and each resulting pointer is aligned and valid to read as an
  initialized `T` and to write as one `T` representation. The storage is live
  for the entire call. Both pointers derive from the same allocation. Positions
  may be equal.
* The caller owns or otherwise has the permissions required to access the two
  logical slots. The comparator may hold shared references to them for the
  call, and all such references/borrow obligations end before the raw writes.
  `F: FnMut(&T, &T) -> bool` is used exactly as declared; legal aliasing and
  lifetime rules apply. No validity of arbitrary bit patterns is assumed.
* `is_less` may return either Boolean, may update its own state, and may perform
  any legal effects available through its references or captures, including
  permitted `UnsafeCell` mutation. Those effects need not preserve either key
  or the other collection elements. Its normal and unwind transitions must
  leave the current `T`, `F`, and frame resources valid for subsequent use.
  Captured-resource effects are described by a callback relation, not by an
  unchanged-state/purity assertion.

The remaining statements are **body proof obligations**, not caller assumptions
about an internal temporary. The selected source representations must remain
readable and valid until copied. The local `ManuallyDrop<T>` temporary must be a
valid representation holder; the final destination slot must be writable, and
the local temporary's storage must not overlap `q` for the final
`copy_nonoverlapping`. The body's control flow and callees must establish that
no operation after the successful comparator unwinds while the temporary owns
the logical value. In particular the actual `select_unpredictable` call needs
verified no-unwind behavior and an exact selected-pointer result at *mut T.

The overlapping `ptr::copy` obligation includes that its destination remains
writable when its source is read: equality of numeric addresses alone does not
establish this alias/provenance condition. Both copy primitives preserve the
source representation's initialization state, including unspecified padding;
they do not require every padding byte to be initialized. These are obligations
of the body/caller ownership protocol, not additional Copy or Freeze bounds.

The output is not promised to be a permutation of the values at function
entry: legal comparator effects can mutate values or other reachable state.
The helper itself accesses only the two indexed slots after the comparison.
Every other slot is unchanged by the helper, modulo comparator effects that
are legal and reachable through its references/captures. Likewise, the
post-state of `F` is its actual current normal state, not its entry state.

### Panic post

If the comparator unwinds, it does so before `select_unpredictable`, `read`, or
either copy. Thus the helper has not moved or copied a `T` representation. The
unwind post is the caller's current ownership/resource state for all slots and
the callback/frame state produced by the comparator's unwind effects, with
temporary shared borrows recovered. It does not roll back legal interior
mutations, captured-state updates, or other comparator effects. There is no
sortedness or entry-value permutation guarantee on unwind.

This post relies on the actual called comparator unwinding with its own
well-formed resource protocol. It does not silently require a no-panic
comparator. The body after the callback must be shown not to unwind for the
normal path to avoid a stranded `ManuallyDrop` temporary or partial ownership
transition.

### Normal post and ownership accounting

After a successful callback, let `V'` be the current slot state after all legal
callback effects, and let `b` be the returned Boolean. The normal post says
that the logical contents of the two slots are `V'` when `b == false`, and
`swap(V')` when `b == true`; all other locations retain their post-callback
state. The ownership/resource post contains exactly one logical ownership
sequence for the `T` values, the current callback state, the frame, and no
outstanding temporary borrow or local `T` ownership debt. The temporary's
`ManuallyDrop` wrapper does not create a second droppable owner. There is no
extra `Drop` of either original value.

For non-Copy or destructor-bearing `T`, this is an ownership transition, not a
claim that byte copies clone ownership. Proof must account for `ptr::read`
temporarily moving logical ownership out of its source, the first `copy`
writing a representation, and the second copy restoring the other slot. It
must establish that no unwind/early return occurs between those steps and that
the final slots again carry one ownership occurrence each. It must also
preserve padding/validity correctly; unspecified padding is not required to
become initialized data.

For `a_pos == b_pos`, `p == q`: the comparator sees two shared references to
the same logical slot and may return either Boolean. Both selection results
then identify that same location, the first copy is a self-copy, and the final
copy restores the temporary to the same slot. The functional result is the
same one slot value, and there must still be exactly one ownership occurrence.
The implementation's aliasing and ownership proof must cover this case rather
than assuming distinct indices.

For ZST, distinct logical indices may have the same numerical pointer and all
byte regions are empty. The proof must use logical slice positions and
ownership occurrences, not address inequality, to justify the operation.
Pointer validity/alignment, in-bounds logical indices, initialized valid
references, and one owner per logical slot remain required. Zero byte length
does not create additional owners, nor does it waive Rust's pointer/add or
reference rules. No non-ZST-only disjoint-address premise is applicable.

There is no independently initialized destination range in this operation:
the helper updates its two live slots in place. Other slots are framed at
their post-callback state. Any callback-accessible frame mutation is retained
in the postcondition rather than restored to its entry value.

## Separate functional theorem for sorting networks

The safety contract above permits stateful, inconsistent, or value-mutating
comparators. It therefore cannot establish sorting. To compose a network, use
a separate functional contract with the following premises:

1. Each callback returns normally and preserves the ordering key of **every**
   occurrence throughout the network, including occurrences not passed to that
   callback but reachable through captures or interior shared state. Its Boolean
   equals `key(q) < key(p)` on those fixed keys. Whole-value snapshot preservation
   is a stronger, optional premise for an entry-value multiset post; key-only
   preservation permits valid non-key field effects and still preserves logical
   occurrence identity and key multiset.
2. The comparator implements one fixed strict total order on keys (or a
   fixed strict weak order with equivalence defined by neither key being less).
   In particular, it is irreflexive and transitive and its equivalence classes
   are transitive. Stateful results that vary between calls do not satisfy this
   premise merely because each call has type `FnMut`.
3. Every call is on valid in-range logical positions of the same sequence, and
   the actual helper realizes the compare-exchange transition above.

Under those premises each call preserves the multiset of logical occurrences
and replaces its pair by the ordered pair `min(x,y), max(x,y)`. Composing such
calls preserves the complete input multiset. If the network's mathematical
sequence sorts every input in its domain, the final sequence is sorted under
the chosen order. This contract makes no stability claim: a two-value exchange
can change the relative order of equivalent occurrences, and `sort9_optimal`
and `sort13_optimal` are not assumed stable.

If network functionality is first proved over Boolean inputs (zero-one
principle), a separate transfer argument is required. For any finite input
whose keys are in a total order, choose a threshold between two adjacent
distinct key classes and map each key to 0 when it is at or below the threshold
and 1 otherwise. Compare-exchange commutes with this monotone map because it
outputs the lesser and greater key. A failure of adjacent sortedness on the
general output gives a threshold that maps those inverted keys to `1,0`,
contradicting the Boolean network theorem. The network still outputs a
permutation because every compare-exchange does. For a strict weak order, apply
this reasoning to its totally ordered equivalence classes; it proves sorted
classes, not stability within a class. The transfer requires the fixed-order,
key-preservation, and compare-exchange premises above.

## Required actual-source correspondence and open implementation proof

The mathematical composition is conditional on an abstract
`CE(i,j)` operation that compares current keys at `j,i` and exchanges their
logical values exactly when the first is less. Source correspondence requires
reviewing the pinned SmallSort source's every actual call, its argument order,
the enclosing slice length, pointer provenance/validity, and the match between
its `is_less` callback and the abstract fixed-order relation. A correct
abstract network theorem alone establishes none of those facts.

The Rust implementation bridge remains **OPEN / NOT PROVEN**. A proof of the
actual helper must establish all of these obligations without imposing
arbitrary `Copy`, `Freeze`, purity, or no-panic bounds on the safety theorem:

* `v_base.add` bounds, allocation/provenance, alignment, initialized reference
  validity, aliasing for equal positions and ZSTs;
* legal `FnMut` borrow and callback normal/unwind resource relation, allowing
  legal interior mutability and effects;
* actual `hint::select_unpredictable` result and no-unwind behavior at both
  selected pointer instantiations;
* `ManuallyDrop::new`, `ptr::read`, overlapping-permitted `ptr::copy`, and
  `ptr::copy_nonoverlapping` validity, initialization, ownership conservation,
  padding, and absence of a panic/early exit during the temporary interval;
* a complete normal resource post and comparator-panic post, including the
  current state of `F`, the two selected values, and framed other slots.

Existing sort4 research does not discharge these items. In particular, its
accepted pointer ownership component is narrowly about a SAFE
`MaybeUninit<*const Element>` constructor and does not prove pointer-selection,
general `MaybeUninit` union ownership, raw T reads/copies, `FnMut`, or this
helper. The select-callee review records the `select_unpredictable` / raw
pointer bridge as open. Do not use an assumed helper contract to call this
network direction a completed public Challenge 8 proof.

## Integration requirements for the network proofs

* `select_unpredictable`: prove the actual call or state a reviewed, exact
  abstraction, including chosen-pointer equality and normal-only behavior at
  **T = *mut Element**. The other direction's actual helper at *const Element
  is a related integration dependency, not an automatically interchangeable
  verified summary or license to extend its experimental profile.
* `ManuallyDrop`: use the repository's pinned interpretation only within its
  existing scope; separately prove the `T` temporary and ownership accounting.
* `FnMut`: retain mutable callback state and legal effects in the state
  relation. The functional proof may add fixed-order/key-preservation
  premises, but they do not constrain the safety theorem.
* Memory: establish the slice length (`>= 9` or `>= 13`), each constant
  index's validity, pointer provenance and references. Equal-address ZST
  positions remain distinct logical elements. No distinct-index requirement
  may be smuggled into the abstract network proof.

These are integration requirements for later composition. This note itself
contains no executable verification result and does not close the public goal.
