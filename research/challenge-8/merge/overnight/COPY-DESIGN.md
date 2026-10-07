# Copying into MaybeUninit scratch: source and trust review

This note reviews the frozen VeriFast 26.10 model for the actual SmallSort
scratch writes. It proposes the smallest useful next dependency; it does not
change a verifier spec, implementation, patch, or runner. The pinned VeriFast
tree is `f76012fb518703b1d98e243ac4f487f16877cfcb`.

Relevant frozen files:

| File | Git blob | SHA-256 |
| --- | --- | --- |
| `bin/rust/prelude_core.rsspec` | `34d3057d0325ef065b4e1933078e56894d2c70ce` | `435146cd4632541241563ae45b146704c14f6f7cdd3b5d404837617f08bc91b8` |
| `bin/rust/std/lib.rsspec` | `a1e9a160716ba97d1ee86587f0620f0eb21b7668` | `2da7acfb6596f8abec90c103ef7f294152c18f974b88124669882fc051272999` |
| `bin/rust/rust_belt/points_to_at_lifetime.rsspec` | `40939f922bcb6fdc7ee0d30427fa861827043827` | `dd27384b6c17b733c8e36487ed82574fdf290ac5bc4e4becd24076dbebfffe4b` |
| actual `smallsort.rs` | `e555fce440872898e47fd5114f32eb15401d07df` | `85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1` |

## What the frozen model says

In `prelude_core.rsspec`, `points_to_<T>(p; v)` and `array_<T>(p,n;vs)`
model a typed cell or array whose values are `option<T>`; `none` represents
uninitialized storage and `some(v)` is exposed by the initialized `points_to`
and `array` predicates. Thus the model already distinguishes typed
initializedness from ownership: a `points_to` chunk says what value is in a
cell, while `<T>.own(t,v)` is a separate permission/invariant resource.
Neither `points_to` nor `points_to_` gives a `T` value its logical
`<T>.own` resource.

The current `std::ptr::copy_nonoverlapping<T>` contract in `std/lib.rsspec`
requires `src[..count] |-> ?vs` and `dst[..count] |-> _`, then returns the
source unchanged and `dst[..count] |-> vs`. This is suitable for an initialized
destination (including `CopyOnDrop::drop`), but rejects a slot modeled as
uninitialized `MaybeUninit<T>`. It also leaves the Rust safety conditions
implicit in those typed array chunks: nonnull/aligned pointers for zero-byte
copies, byte-size limits, allocation validity, and explicit non-overlap are
not written in that intrinsic contract.

The same spec file models `MaybeUninit<T>` with
`MaybeUninit::inner : MaybeUninit<T> -> option<T>`, `uninit()` as the empty
state, and `new(v)` as `some(v)`. `open_MaybeUninit_` and the array conversion
lemmas bridge wrapper storage with optional typed storage. In particular,
`array__to_array_MaybeUninit` and `array__MaybeUninit_to_array_MaybeUninit`
provide the direction-specific array views; `MaybeUninit<T>` has the same
`size_of` and `align_of` as `T`. `Layout::new<T>()` uses those size/alignment
functions; allocator specs expose `alloc_block_in`/`alloc_block` and aligned,
bounded storage. The actual general SmallSort scratch is a stack
`MaybeUninit<[T; 48]>` viewed as `&mut [MaybeUninit<T>]`; no allocator is needed
for that path.

The actual `small_sort_general_with_scratch` first casts the MaybeUninit slice
pointer to `*mut T`. It copies initialized source runs into that raw pointer,
then extends them with further one-element copies. `sort4_stable` and
`sort8_stable` also write to scratch; `bidirectional_merge` writes to its
destination before that destination is initialized as `T`. `CopyOnDrop` later
copies a fully initialized scratch array back into initialized `v`; that
existing call fits the frozen initialized-destination contract and must remain
a distinct control.

## Recommended dependency

Do not synthesize an initialized ghost shadow over the real scratch. That would
make the existing intrinsic precondition pass by claiming initialized `T`
cells where the runtime storage is `MaybeUninit<T>`. It also cannot model a
partially initialized output on an unwind edge. Do not add `<T>.own(t,v)` to a
copied scratch slot: SmallSort copies bytes while retaining the source-side
owner, and the scratch copy has no independent `own<T>` entitlement.

The smallest practical change is a separate, explicitly reviewed trusted
specification for an into-uninitialized form of the intrinsic (or a narrowly
gated additional contract for the existing intrinsic). It should consume the
destination's writable MaybeUninit storage and produce typed initializedness
for exactly the copied slots, while retaining source bytes and source
ownership. A candidate abstract contract is:

```text
source: initialized [T] memory with values vs
destination: writable raw MaybeUninit storage, with any prior byte state
copy: dst receives the same abstract T values vs
post: source memory and source-side own(T) are unchanged;
      dst is initialized as [T] with values vs;
      no destination own(T) is created
```

This must not silently assume the old destination contained either `none` or a
valid `T`. Safe `MaybeUninit::<&T>::zeroed()` can hold a null pointer
representation that is invalid for a Rust reference; the current
`option<T>`-only view cannot encode such an initialized but invalid T
representation. A fully general contract should therefore consume
the destination as raw bytes/MaybeUninit and replace those bytes, then expose
the post-copy bytes as typed `T` only because they were copied from initialized
source `T` cells. Existing `from_u8s_`, `to_u8s_`, and byte-array lemmas are
useful for this bridge, but the frozen ones do not by themselves provide a
verified byte-copy intrinsic into an uninitialized range. Any proposed
contract must be checked against the kernel's pointer/provenance model,
including pointer-valued fields; ordinary byte values alone must not erase
provenance.

An initial *diagnostic* contract could use `array_<T>` option chunks when the
target scratch is known to begin uninitialized or to contain only valid
previous T copies. That restricted model can unblock a first actual-body
diagnostic, but it is not a general `MaybeUninit<T>` contract and cannot be
called unrestricted-safe. The caller-local stack allocation and actual
write-before-read order need to prove this narrower precondition on every
normal and unwind path. For any such staged use, retain a clear phase gate
before claiming the generalized intrinsic.

## Conditions the primitive and fixtures must expose

Before it returns initialized destination cells, the contract needs evidence
for all of these Rust conditions, whether expressed directly or derived from
separating allocation/range resources:

- Source is readable and initialized for `count * size_of::<T>()` bytes; its
  typed values are valid `T` and the existing source ownership is preserved.
- Destination is writable for that byte range, including when initially
  uninitialized or holding arbitrary MaybeUninit bytes. Its allocation
  identity/provenance and extent must support the entire write.
- Both pointers are nonnull and aligned to `align_of::<T>()` even when
  `count == 0` or `size_of::<T>() == 0`.
- The mathematical byte count does not overflow and is at most `isize::MAX`.
- The source and destination byte ranges do not overlap. Empty ranges are
  handled explicitly; zero-sized elements still retain pointer nonnullness and
  alignment requirements. Do not infer separation merely from a typed-array
  predicate until its ZST semantics are checked against the pinned model.
- The post-state preserves the exact abstract copied values (including any
  pointer provenance represented in `T`) and source permissions. It introduces
  destination initializedness only. It never invents `<T>.own`, consumes
  source ownership, assumes `Copy`/`Freeze`, or makes a purity assumption.
- If the write is composed with a possibly panicking callback, a postcondition
  on callback unwind must preserve the prior destination byte/initialization
  state. The primitive itself is non-panicking, but must not be used to erase a
  pre-call snapshot needed for a later unwind claim.

The current `array_<T>` recursion is address-based through `p + 1`; for a ZST
this pointer does not advance. Its ability to represent multiple ZST elements,
and the ability of separated chunks to distinguish their logical slots, must
be answered by a hosted ZST fixture before using array chunks as the generic
contract. Existing alignment controls are not evidence that the Rust Belt
typed heap model handles ZST range ownership.

## Falsifiable regression gates

Keep these as isolated CASE fixtures, each with a single intended target and
with expected stages/predicates recorded only after hosted output establishes
the exact diagnostic:

1. **Positive initialization bridge:** copy one initialized `T` into one
   uninitialized `MaybeUninit<T>` slot; prove copied value/initializedness,
   unchanged source and source `<T>.own`, and absence of destination `<T>.own`.
2. **Linear ownership control:** require both source `own(T)` and initialized
   source memory. The positive returns exactly the original source owner. A
   negative target tries to return or consume a second `own(T)` for the scratch
   copy; it must fail at that resource, not at setup or an unsupported cast.
3. **No uninitialized source:** use `MaybeUninit<T>::uninit()` as source; fail
   at the source read/initializedness gate.
4. **Writable destination:** remove the destination write chunk or make its
   range too short; fail at the destination resource/bounds gate.
5. **Alignment:** separate source-misaligned and destination-misaligned
   controls, including zero count and ZST count, to ensure zero bytes do not
   bypass alignment/non-null requirements.
6. **Non-overlap:** for nonzero `T`, use exact, partial, and disjoint ranges;
   exact/partial overlap fail at the non-overlap/resource gate, while the
   disjoint positive retains exact values. Add zero-sized pointer cases
   separately once the frozen model's empty-range semantics are understood.
7. **Size bound:** target the multiplication/`isize::MAX` byte bound without
   causing frontend or integer-overflow setup failure.
8. **Old destination bytes:** exercise `none`, prior valid Some(T), and an
   arbitrary initialized byte pattern that is invalid as `T`. The generalized
   primitive should overwrite all three without decoding or dropping the old
   contents; if the model cannot represent the final case, state that as a
   limitation rather than proving the other two as a general MaybeUninit
   result.
9. **No source mutation / no provenance loss:** include a pointer-bearing `T`
   control if supported by the frozen frontend, compare the abstract source
   and copied pointer values, and retain allocation provenance on both sides.
10. **Actual body controls:** retain the existing initialized-destination
    `CopyOnDrop` copy control; separately target the first scratch write,
    a later write into already initialized scratch, and normal/unwind return.
    These only diagnose `merge_up`/callers after the primitive gate; they are
    not proof of whole SmallSort safety or ordering.

## Decision boundary

The stock `copy_nonoverlapping` contract cannot establish the actual
MaybeUninit scratch write because it requires `dst[..count] |-> _`. A ghost
initialized shadow would hide that mismatch. A separate proposed staged
contract is now captured in [COPY-PROFILE.md](COPY-PROFILE.md) and
`copy.patch`: it covers exactly one positive-size element with an option<T>
destination state and explicit address/alignment/range conditions. It creates
a new trusted semantic edge from source T values to destination
initializedness, so it still requires review and hosted controls before
integration or proof claims. The most important open issue is representation
of arbitrary initialized-invalid MaybeUninit bytes together with typed pointer
provenance; the staged option<T> contract does not cover unrestricted scratch
storage.

No source/spec patch, runner, verifier, build, or executable test was changed
or run while preparing this design note.
