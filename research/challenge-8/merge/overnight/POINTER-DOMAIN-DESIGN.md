# Checked pointer-domain bridge for C1

## Target and hypothesis

The target is the actual `core::ptr::copy_nonoverlapping(src, dst, 1)` call in
`merge_up` and `merge_down` from the pinned repository
`library/core/src/slice/sort/shared/smallsort.rs`. The separate trusted C1
primitive requires a positive-sized `T`, nonnull aligned pointers, a
`size_of::<T>() <= isize::MAX` bound, non-overflowing one-element endpoints,
object limits for each pointer, and numerically disjoint one-element byte
spans. Its data contract also requires initialized source and writable
destination resources; this probe intentionally proves only the pure pointer
domain and does not call the C1 primitive.

Falsifiable hypothesis: from source and destination bases with positive size,
positive alignment, `n >= 2`, valid indices `i,j < n`, total spans bounded by
`isize::MAX`, non-overflowing numeric endpoints, both endpoint pointers within
their original provenance limits, base alignment, and disjoint full numeric
spans, ordinary checked `add` derives every pure C1 premise for `src+i` and
`dst+j`. It preserves each pointer's original provenance and metadata. The
proof is conditional on those explicit base/endpoint limit facts; it does not
infer allocation identity or range facts from integer addresses.

The alignment proof is checked structural induction over the stock list
`repeat(nat_of_int(index), true)`, rather than relying on an unavailable
successor law for stock `int_of_nat`. Stock `length_repeat` and
`int_of_nat_of_int` connect the list length back to the caller's nonnegative
index. The recursive step uses stock `length_nonnegative`, `mul_mono_l`, and
the checked one-stride lemma; the base and one-stride lemma use pinned
`div_rem_nonneg` and `div_rem_nonneg_unique`. Index/count arithmetic and
alignment lemmas run before the ordinary pointer `add` operations, so an
arithmetic failure cannot be hidden by a pointer-operation diagnostic.

## Exact domain and posts

For `s = size_of::<T>()`, `a = align_of::<T>()`, and machine maximum `U`, the
adapter requires `2 <= n`, `0 <= i,j < n`, `0 < s`, `0 < a`, `s % a == 0`,
`n*s <= isize::MAX`, positive base addresses, both base addresses divisible
by `a`, `base_address + n*s <= U` independently for source and destination,
`pointer_within_limits(base)` and `pointer_within_limits(base+n)` for both
bases, and full-range separation:
`src_base+n*s <= dst_base || dst_base+n*s <= src_base`.

The returned pointers are exactly `src_base.add(i)` and `dst_base.add(j)`.
The post records their constructor identity, address `base_address + index*s`,
unchanged provenance and metadata, nonnullness, alignment, one-element numeric
endpoint bounds, `object_pointer_within_limits(pointer,s)`, and disjoint
one-element numeric spans. These are precisely the pure C1 premises for the
actual one-element copy; the C1 memory resources remain separate obligations.

## Allocation and trust boundary

The caller must establish each base and terminal pointer's
`pointer_within_limits` fact from the source/destination allocation model at
the same source version. In the frozen prelude, the `array` and
`array_` postconditions expose these two endpoint facts; for the actual
MaybeUninit scratch, the existing raw/MaybeUninit allocation representation
must expose equivalent endpoint facts before this adapter applies. This probe
does not prove that actual caller resource conversion. It uses ordinary `add`
only inside the bounded extents, then derives interior endpoint limits from
the endpoint facts and arithmetic order. It does not turn numeric separation
into provenance equality, permission, initializedness, ownership, or alias
evidence. C1 still requires its own source read fraction and exact destination
write resource. No additional axiom, assumption, ghost shadow, runtime-source
edit, verifier semantic edit, or resource-producing primitive is introduced.

The domain is deliberately positive-stride and excludes ZSTs. It does not
cover the case where the merge's left/right source pointers alias by provenance
or where destination and source ranges overlap; actual merge's partition/cursor
invariants must establish the full-range disjointness premise at its caller.
This probe proves neither that invariant nor the actual `merge_up`/`merge_down`
normal or unwind posts.

## Hosted matrix and decision mapping

| Case | Intended obligation | Required evidence | Next decision |
| --- | --- | --- | --- |
| `pointer_domain_pair` | All pure C1 premises for arbitrary valid `i,j` | Exact source identity; helper body entered; constructor/provenance/metadata posts; normal, unwind, return, leak and dead-code gates | If green, add this checked adapter to the hosted merge matrix. |
| `pointer_domain_out_of_index` | Caller cannot establish adapter precondition when `i == n` | Exact verifier diagnostic at `verified/lib.rs(92,29-30)`: `Cannot prove condition. (Cannot prove n < n.)`; stages exporter/decode/VeriFast/refinement = 0/0/1/0; the marked caller body executes. | Accept only this exact rejection and source integrity; any different failure remains inconclusive. |
| `pointer_domain_overlap` | Caller cannot establish whole-range separation when bases overlap | Exact verifier diagnostic at `verified/lib.rs(106,76-78)` for the failed full-range separation disjunction; stages 0/0/1/0; the marked caller body executes. | Accept only this exact rejection and source integrity; any different failure remains inconclusive. |

## Saved calibration and classification boundary

The saved hosted artifact `37717433930` (source SHA
`b04b1b6063e53d3bb543c117f5ea84d493ed01da`) recorded the two diagnostics above
with the marked negative bodies entered. At that time both rows were
`INCONCLUSIVE`, because the fixture did not yet carry exact rejection metadata.
The current `EXPECT_REJECTION` declarations pin those observed diagnostics;
they do not retroactively change the saved result. A fresh hosted run is required
before either negative can be called `EXPECTED_REJECTION`.

The matrix has one positive case and two negative controls. The positive
`pointer_domain_pair` case checked five bodies (the adapter, wrapper, and three
alignment helpers) with the full positive gate. Its contract remains a
pointer-domain lemma only: it does not accept C1 memory safety, either merge
callee, cleanup, or SmallSort.
