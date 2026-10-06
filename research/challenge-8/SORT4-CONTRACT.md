# `sort4_stable`: source contract and caller audit

Static audit at `68fcc98b79fc69b717d3e2ed42605cae8b4ffc05` (branch
`challenge-8/research`). The target is
`library/core/src/slice/sort/shared/smallsort.rs`, blob
`e555fce440872898e47fd5114f32eb15401d07df`. This note separates what the
body does from the stronger resources a sound generic proof must account for.

## Body and memory effects

`sort4_stable<T, F: FnMut(&T, &T) -> bool>(v_base: *const T, dst: *mut T,
is_less: &mut F)` reads four source elements. It calls the comparator in this
order: `(v[1], v[0])` (`c1`), `(v[3], v[2])` (`c2`), `(c, a)` (`c3`),
`(d, b)` (`c4`), and `(unknown_right, unknown_left)` (`c5`). Only after all
five calls return does it issue four one-element
`ptr::copy_nonoverlapping` operations to `dst[0]` through `dst[3]`, in the
order `min`, `lo`, `hi`, `max`. There are no loops, local destructors,
`ManuallyDrop`, or cleanup guards in this body.

The pointer choices preserve a permutation of the four logical source
*indices* for every possible sequence of five boolean answers, including
answers from a stateful or inconsistent comparator. `c1` and `c2` choose one
index from each disjoint source pair; the four `(c3,c4)` combinations
partition those four indices into `min`, `max`, `unknown_left`, and
`unknown_right`; `c5` only exchanges the last pair. For ZSTs distinct logical
indices need not have distinct numeric addresses. No comparator-ordering
premise is needed for the logical index permutation. Ordering and stability
do need a pure, consistent strict ordering premise: safety permits any valid
callback results, and interior mutation can invalidate earlier observations.

For a general non-ZST `T`, the source must provide four initialized, valid,
readable `T` locations with alignment, bounds, and provenance sufficient for
the `add` operations and shared-reference dereferences. The destination must
provide four aligned, writable `T` slots with valid bounds and provenance.
Each executed `copy_nonoverlapping` requires that its one-element source and
destination regions do not overlap. To establish the whole operation for all
five-bit outcomes without tracking a comparator-dependent overlap case, a
clear sufficient contract is separation of the full source and destination
ranges: an earlier output write into an overlapping source range could
change bytes read by a later copy. This is a sufficient all-outcomes
precondition, not a claim that every specially constrained mapping with
partial overlap must fail. The source SAFETY comment says only “valid for 4
reads” and “valid for 4 writes”; it does not state the per-copy
non-overlap requirement. That is a contract gap. The callers below provide
separate source and scratch storage, but their facts must not be silently
promoted to a universal precondition of this unsafe function.

ZST is a separate proof obligation. Numeric address inequality is not a
meaningful separation argument for zero-sized locations; the proof must use
valid allocation/provenance and in-bounds logical element positions, and
check the precise Rust requirements of `add`, reference creation, and
`copy_nonoverlapping` at size zero. No ZST result is inferred from the i32
functional domain.

## Ownership, normal return, and panic

Initialized bytes and ownership of a live `T` are different resources. The
four copies initialize `dst`, but they do not invalidate the four source
locations and do not by themselves create a second independently droppable
`T.own` sequence. For non-`Copy` values, a full proof needs an explicit
ownership protocol: which range owns the four logical values on return, what
the caller may later drop, and how the copied representation in the other
range is treated. The function's short SAFETY comment specifies none of this.
The proof must include arbitrary generic `T`, including non-`Copy`,
non-`Freeze`, destructor-bearing values, and ZST; functional harnesses over
`i32` and a `Copy` tag do not establish those cases.

On normal return, a generic safety postcondition accounts for the current
source bytes after callback effects, four initialized destination
representations, the single current logical ownership sequence and any frame
resources, plus the updated state of `F`. It must state who may later treat
the destination bytes as owning `T`, and what happens to any prior destination
resources. Byte copying alone cannot transfer or duplicate a `T.own`
sequence. Sortedness and stability belong to a separate functional
postcondition under purity and ordering premises; safety has no such premises.
There is no general promise that `F` is pure or that values reachable through
it/global state remain unchanged. Rust's shared-reference rules constrain
ordinary writes through `&T`, but interior mutability and other valid
callback effects remain possible.

At each of the five comparator calls, a panic occurs before this function has
written any destination slot. Therefore the body's own destination writes are
absent on every comparator-unwind path. That fact does not undo effects the
callback made through `F`, `UnsafeCell`, globals, or other valid access paths;
nor does it make source bytes unchanged in the presence of interior
mutability. The unwind postcondition must return the source/frame resources,
end the temporary shared borrows, account for the current `F` state, and
preserve callback effects. It must return one current logical ownership
sequence; it cannot assert that a callback's permitted effects were rolled
back. It must not claim a sorted result or restore pre-call callback state.

| Panic site | Actual comparator arguments | Destination writes by this body before panic |
| --- | --- | --- |
| `c1` | `(&*v_base.add(1), &*v_base)` | None |
| `c2` | `(&*v_base.add(3), &*v_base.add(2))` | None |
| `c3` | `(&*c, &*a)`, where `a = v_base + c1`, `c = v_base + 2 + c2` | None |
| `c4` | `(&*d, &*b)`, where `b = v_base + !c1`, `d = v_base + 2 + !c2` | None |
| `c5` | `(&*unknown_right, &*unknown_left)`, with both pointers selected from `a,b,c,d` by `c3,c4` | None |

## Callers and scratch storage

`small_sort_general` (same file, around lines 205–217) creates
`MaybeUninit<[T; SMALL_SORT_GENERAL_SCRATCH_LEN]>`, views it as
`[MaybeUninit<T>]`, then calls `small_sort_general_with_scratch`. That
function accepts `v: &mut [T]`, `scratch: &mut [MaybeUninit<T>]`, and
`is_less: &mut F`; it checks `scratch.len() >= len + 16` before casting the
scratch base to `*mut T`. The separate mutable borrows establish separate
storage for valid safe callers. In the `len >= 8` branch, the `sort4_stable`
calls write four cells at `scratch_base` and four at
`scratch_base.add(len_div_2)`, reading from `v_base` and
`v_base.add(len_div_2)`. The corresponding four-cell source and destination
ranges are separate. In the smaller branch, the function copies one source
cell from each half into scratch instead.

`sort8_stable` (around lines 663–675) has `T: FreezeMarker`, takes source,
destination, and scratch pointers, calls `sort4_stable` on source ranges
`[0,4)` and `[4,8)` into scratch ranges `[0,4)` and `[4,8)`, then merges
scratch into `dst`. Its documented caller precondition requires valid source
reads and valid destination/scratch writes, but does not itself state every
pairwise separation needed by `sort4_stable`; the concrete
`small_sort_general_with_scratch` call has separate `v` and scratch borrows.

After presorting, `small_sort_general_with_scratch` extends each scratch run,
constructs `CopyOnDrop`, merges back to `v`, and forgets the guard on success.
These later operations are caller-level ownership/recovery machinery and are
not proved by a `sort4_stable` functional harness. On a comparator panic in
`sort4_stable`, no slot from that invocation has yet been written, though a
prior `sort4_stable` call in `sort8_stable` may already have initialized part
of scratch. Scratch is `MaybeUninit`, so it is not automatically dropped;
whether copied resource-bearing values are accounted for on unwind belongs
to the full caller proof.

The caller's `FreezeMarker` bound is implemented for `T: Freeze` in
`small_sort/shared/mod.rs`; it is absent from `sort4_stable` itself. It does
not imply `Copy`. Thus caller facts can narrow the call-site domain, but do
not discharge the public unsafe function's generic obligations.

## Functional claims authorized for this phase

The actual-body Kani values harness has four independently symbolic `i32`
inputs over the full `i32` range; pure, nonpanicking `<`; four initialized
source cells; and four initialized destination cells in separate fixed
buffers. Its postconditions are nondecreasing destination values and exact
multiset equality with the inputs. The actual-body stability harness uses
four `{ key: i32, original_id: u8 }`-style fixed tagged records (the checked-in
harness must state its exact representation), symbolic keys, input IDs
`0..3`, and a comparator that reads only `key`. It asserts exact complete-item
permutation, nondecreasing keys, and increasing IDs among equal keys. These
are finite-domain functional theorems for those layouts and comparator
assumptions. Neither establishes arbitrary generic memory safety, aliasing,
ownership, effects, panic recovery, ZST behavior, or the four required UB
categories.
