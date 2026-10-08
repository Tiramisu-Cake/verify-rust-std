# Repository callers of `bidirectional_merge`: C1 realization audit

## Scope and source identity

This is a source audit, not a proof that the repository call sites satisfy the
current VeriFast C1 contract. The inspected checkout is repository commit
`3557494937f7ed93f87d6b8b2deec912617b0a1a`. The authoritative function source
is `library/core/src/slice/sort/shared/smallsort.rs`, Git blob
`40939f922bcb6fdc7ee0d30427fa861827043827`. The marker sources are
`library/core/src/slice/sort/shared/mod.rs`, blob
`e1977d79f32076488e37048d17be77e37a321b0c`, and `library/core/src/marker.rs`,
blob `64a67bbd11c12bc6dd03867cb5c479642dbec3a6`. The existing resource note
records that the SmallSort blob matches upstream source commit
`cd371e035c7e573760c43bf934d53e8118ee3e7d`.

The hosted verifier profile separately pins VeriFast source
`f76012fb518703b1d98e243ac4f487f16877cfcb` and `nightly-2026-09-25` with
`rustc-dev` and `rust-src`. That compiler/sysroot is a build and translation
dependency, not the repository source identity above. This audit has not
compared its installed `rust-src` SmallSort bytes to the repository blob; a
sysroot copy must not silently replace the extracted repository body as the
proof subject.

The three exact repository call sites are `small_sort_general_with_scratch`
at `smallsort.rs:286`, `small_sort_network` at `:368`, and `sort8_stable` at
`:672`. `bidirectional_merge` itself (`:754`) has no ZST branch. Both public
stable and unstable sort entry points return when `T::IS_ZST` at
`library/core/src/slice/sort/stable/mod.rs:31` and
`library/core/src/slice/sort/unstable/mod.rs:27`, before their normal internal
dispatch. That source path can exclude ZST for those public callers if its
dispatch and compiler fact are carried into a proof; it does not prove a
generic standalone `bidirectional_merge` contract for ZST.

## Per-call source facts and remaining C1 obligations

| Call site | Source and target storage | Source facts established by the body | Caller facts still needed for C1 |
|---|---|---|---|
| `small_sort_general_with_scratch:286` | Source is `scratch_base[0..len]`, reborrowed as `&[T]` from the fully filled scratch array. Target is `v_base[0..len]`, the original initialized `&mut [T]`. | The function returns for `len < 2` and aborts if `scratch.len() < len + 16`. It first fills both sorted halves of scratch: for lengths below 8 it copies one seed per half and fills the rest; the 4- and 8-element network paths seed longer prefixes; the two tail loops extend them to cover every index. `CopyOnDrop` is constructed only after this full initialization. Its `Drop` copies all `len` source values back to `v` if merge unwinds; it is forgotten after normal merge. The output target therefore contains valid old `T` values at entry, and the source has initialized current `T` values. |
| `small_sort_network:368` | Source is the full input `v_base[0..len]`, reborrowed as `&mut [T]`. Target is local `MaybeUninit<[T; 32]>` storage cast to `*mut T`. | It returns for `len < 2`, aborts above 32, and reaches this merge only after `no_merge` is false, so this branch has `18 <= len <= 32`. The input slice is initialized. The destination is separate stack storage; the following copy back runs only after normal merge. If a callback or final guard unwinds from merge, merge has not written to `v`; its destination may be only partly initialized and remains `MaybeUninit`. |
| `sort8_stable:672` | Source is the just-initialized eight-element work window at `scratch_base[0..8]`. Target is the eight-element output window `dst[0..8]` in the caller's `MaybeUninit<T>` scratch array. | This helper is called only from the `size_of::<T>() <= 16 && len >= 16` presort branch of `small_sort_general_with_scratch`. Two `sort4_stable` calls produce the source window before the merge. For the first invocation, target is `[0,8)` and source is `[len,len+8)`; for the second, target is `[len/2,len/2+8)` and source is `[len+8,len+16)`. With `len >= 16`, the output windows, the two source windows, and each source/target pair are disjoint. The outer function checked `scratch.len() >= len + 16`. A panic can leave this `MaybeUninit` target partially initialized; the source window remains the initialized merge input. |

The storage layout, initializedness, and disjoint ranges in this table are
facts visible in the source control flow and Rust types. They are not yet
VeriFast derivations. In particular, casts from `MaybeUninit<T>` storage to
`*mut T`, safe mutable-reference disjointness, and raw-pointer endpoints must
be linked to the frozen allocation/provenance model at each call.

## Obligations common to the three calls

The checked pointer-domain adapter currently proves its pure one-cell C1
premises only from explicit positive-size, positive-alignment, valid-index,
bounded-span and endpoint-limit premises. Each actual caller still needs to
derive those facts for the complete source and destination extents and then
for every cell used by the forward, reverse, and odd-copy paths:

* `size_of::<T>() > 0`, `align_of::<T>() > 0`, size multiple of alignment,
  base alignment, and `len * size_of::<T>() <= isize::MAX`;
* nonnull base addresses, nonoverflowing numeric byte endpoints, valid object
  limits and `pointer_within_limits` for both bases and one-past endpoints;
* preservation of source/destination provenance and metadata through slice
  casts and pointer offsets; numeric separation of every source cell from
  every possible destination cell, not merely different base addresses;
* a valid initialized source `T` at each read, and an exact writable
  destination chunk at each copy, including old destination initialization
  state where the C1 option model requires it.

For the external `scratch` call, the two exclusive slice arguments express
nonaliasing under Rust's reference rules. For the network stack array, storage
is a distinct local allocation. For `sort8_stable`, the source and output are
disjoint subranges of one scratch allocation; the offset inequalities above,
not allocation identity, establish separation. Existing source and pointer
domain notes do not yet derive these three call-site facts in the frozen VF
model.

The accepted C1 memory contract asks for an initialized source points-to chunk
and its current `<T>.own`, plus an option-valued writable destination chunk.
The source text establishes initialized values in the source ranges and the
normal Rust borrow/allocation roles described above. It does not by itself
produce the corresponding VF resources. In particular, the stock model of
`&[T]` uses slice sharing; this audit makes no `share -> own` conversion.
Likewise, a `FreezeMarker` bound does not provide `T::own`, comparator purity,
or a general current-value recovery theorem. The marker module defines the
blanket `impl<T: Freeze> FreezeMarker for T`; the `Freeze` source fact blocks
interior `UnsafeCell` within a type but does not freeze memory reached through
an indirection. No observation about a pointee or mutable `FnMut` state is
included in the C1 safety domain.

Destination states differ at the call sites. The final general merge writes
over already initialized `v` elements; under the C1 option abstraction those
are old `Some(valid T)` values, and no destination `<T>.own` may be invented.
The network merge and the two `sort8_stable` merges target `MaybeUninit`
storage that is fresh for these output windows, so their logical old option
state is uninitialized. A formal model of a reused `MaybeUninit<T>` slice must
still account for arbitrary initialized-invalid bytes; the current C1 option
model covers only `None` or `Some(valid T)`. No one destination assumption
applies uniformly to all three call sites.

Callback answers and `FnMut` state effects are unrestricted for memory
safety. If a callback panics, the current copy has not yet occurred, while
earlier copies may remain. The final general caller's `CopyOnDrop` then restores
the whole initialized scratch sequence into `v`; the network caller leaves its
source `v` untouched by the merge and its partial output in `MaybeUninit`; the
`sort8_stable` caller likewise leaves a partial output in the enclosing
`MaybeUninit` array. These are source-level panic-cleanup paths, not yet a
composed VF unwind proof. The guard panic at the end of `bidirectional_merge`
uses those same caller-specific outcomes. The `FnMut` value may have changed
on either normal or unwind return and must be framed as its current value,
without assuming rollback.

## ZST boundary and proof status

The public stable and unstable sort functions explicitly return for `T::IS_ZST`
before their normal dispatch. This supports a source-level path condition for
these public entries; a proof must still link `T::IS_ZST` to
`size_of::<T>() == 0` and show the selected internal dispatch cannot bypass
the guard. Internal functions and `bidirectional_merge` have no such explicit
guard, and the current C1 model requires strictly positive size. Keep generic
standalone ZST behavior separate. Do not turn zero-stride pointers, zero-byte
separation, or a ZST marker fact into element separation or ownership.

Nothing in this audit establishes a call-site proof. Still-open links include
the three allocation/provenance derivations; `MaybeUninit` source conversion to
current owned elements after filling; source ownership at shared-slice
reborrows; destination old-option modeling; exact normal/unwind composition
with `CopyOnDrop`; and current `FnMut` ownership across both outcomes. Hosted
proof evidence must retain the exact repository body and separately identify
the pinned nightly sysroot/toolchain used by the build.
