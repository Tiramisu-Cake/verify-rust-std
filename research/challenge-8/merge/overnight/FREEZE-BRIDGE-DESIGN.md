# Freeze and direct-byte snapshot bridge — design before implementation

## Claim boundary and pins

This is a proposed dependency for the unchanged `bidirectional_merge` body, not
an accepted proof. The repository checkout is `6ddfd1999991478bdc511546afe5b21e4997e878`;
the exact relevant blobs are `library/core/src/marker.rs`
(`64a67bbd11c12bc6dd03867cb5c479642dbec3a6`),
`library/core/src/slice/sort/shared/mod.rs`
(`e1977d79f32076488e37048d17be77e37a321b0c`), and the unchanged
`library/core/src/slice/sort/shared/smallsort.rs`
(`40939f922bcb6fdc7ee0d30427fa861827043827`). VeriFast reference is pinned
at `f76012fb518703b1d98e243ac4f487f16877cfcb` (stock Rust prelude and
RustBelt specs; no local verifier run is part of this design).

Falsifiable hypothesis: under the actual `T: FreezeMarker` bound, a callback
cannot change the bytes of an input `T` place through safe shared access, so
the two raw-pointer copies in `bidirectional_merge` observe the original direct
place values. This is a statement about the bytes of those input places. It
does not say that memory reached by following a pointer stored inside `T` is
unchanged, that callback state `F` is unchanged, or that `T::own` can be
duplicated/recovered from a shared slice predicate.

## Source and stock-model facts

`Freeze` is a language-item unsafe auto trait. Its source documentation says
that it detects `UnsafeCell` “internally, but not through an indirection”; the
core source gives `UnsafeCell<T>` a negative implementation and explicitly
implements `Freeze` for raw pointers, references, and `PhantomData` regardless
of the pointee. `FreezeMarker` is an empty local trait with the blanket
`impl<T: Freeze> FreezeMarker for T`. The actual merge body requires this marker
and documents its comparator inputs as outdated temporary copies.

The source facts support the following distinction (the second sentence is an
inference from the auto-trait rule and pointer impls): a frozen struct's direct
fields, including a raw-pointer field's address/metadata representation, are
the snapshot subject; a mutable target reached by dereferencing that pointer
is outside that subject and may change. A type containing `UnsafeCell` directly
does not meet the marker bound. Unsafe user implementations and unsafe code
remain trusted Rust obligations, not facts proved by this merge contract.

Stock VeriFast does not currently model `Freeze`. Its shared-slice translation
is `<[T]>.share(lft, tid, v)`, backed by `array_share` and per-element
`<T>.share`; it is not the initialized `array<T>` plus per-element `<T>.own`
post used for `&mut [T]` full borrow. `simple_share` is a fractional lifetime
borrow. Therefore no `share -> own`, full-borrow, or current-value recovery
step is available here. The stock `to_u8s__at_lft` / `from_u8s__at_lft`
lemmas relate a lifetime-borrowed typed place to its byte sequence and back;
the byte sequence is `option<u8>` data and does not itself encode a new
`T::own` resource. These laws preserve a typed value/byte relation, but do not
establish that callbacks preserve that relation over time.

## Candidate bridge and trust boundary

Prefer a checked lemma that consumes and returns the same shared-lifetime
fraction for the exact direct source place while establishing equality of its
before/after `array_at_lft_` byte sequence. Its body must derive the equality
from the compiler-checked `Freeze` evidence for `T` and the shared borrow; it
must not assume byte equality, `T::own`, or comparator purity. If stock VF
cannot express the auto-trait evidence or this checked lemma, the only proposed
semantic extension is a narrowly trusted, source-linked primitive with this
scope:

* one already-valid, aligned direct `T` place, an active shared lifetime loan,
  and compiler-origin proof of `T: Freeze` for the exact type;
* preserve the same loan, place, provenance, metadata, and all unrelated frame
  resources; establish equality only for the `size_of::<T>()` bytes of that
  place before and after the shared callback interval;
* no allocation-range extension, read/write permission, raw-pointer target
  stability, validity reconstruction from arbitrary bytes, `T::own`, or
  comparator answer/purity conclusion;
* no ZST interpretation by byte separation: for `size_of::<T>() == 0`, direct
  byte equality is vacuous and the existing logical value/ownership contract
  must independently state what is preserved.

That primitive would still be a trust dependency requiring a separate hosted
admission and falsification gate; it is not accepted by this note. In
particular, a postcondition asserting unchanged logical `T` values without a
checked representation/value lemma would be target-equivalent and is rejected.

Keep the resource invariant split in two layers. Generic merge safety carries
the current valid source values and their single existing owners, current `F`
ownership, pointer associations, destination initialization/options, and
complete normal/unwind posts; answers remain arbitrary. The direct-byte frame
is an observation fact available only at comparator borrows. Functional A/B
then separately needs immutable keys/current logical values, sorted halves,
faithful normal comparator answers, and the stated order law. None of these
functional premises may enter the generic memory-safety contract implicitly.

## Options and dependency choice

1. **Checked generic Freeze lemma (preferred).** Teach no semantics: connect
   existing compiler-origin trait evidence to a verified lifetime-byte frame
   lemma. This is viable only if the VF type/interpreter exposes exact auto
   trait evidence. It must be tested for a type with a pointer field as well
   as a scalar.
2. **Narrow trusted direct-place primitive (fallback).** Use the scope above
   only if the checked route is not expressible. Record it separately from
   proved bodies and require both exact-source admission and negative controls.
3. **No Freeze bridge (valid partial result).** Continue arbitrary-answer
   actual up/down/resource safety proofs while retaining current source values
   in posts. Do not claim stale temporary comparisons are equivalent to the
   original values, and leave the actual bidirectional functional bridge open.
4. **Concrete-type-only lemma.** A proved scalar or closed-record case can
   validate byte-law wiring but does not discharge generic `T: Freeze` and
   cannot be promoted to actual generic merge acceptance.

## Acceptance matrix for the next hosted profile

| Case | Expected obligation/result |
|---|---|
| `u32` direct place, shared loan framed across callback | Prove equal direct bytes; preserve exact loan and frame. No owner created. |
| `struct { p: *mut Cell }` with exact compiler `Freeze` evidence; callback mutates a separately-owned `Cell` through `p` | Direct bytes of the struct remain equal; target bytes may differ and remain governed by their own resources. This distinguishes pointer-field stability from transitive immutability. |
| `UnsafeCell<u32>` | Reject at actual `Freeze`/`FreezeMarker` bound, not at unrelated setup or parser stage. |
| Re-open the same shared bytes as a second `<T>.own`, or turn slice `share` directly into owned-array resources | Reject at the intended linear-resource/ownership obligation. |
| Claim the raw-pointer target's bytes unchanged from `Freeze` alone | Reject at target-byte equality; separately-owned target mutation is a positive control for the permitted mutation. |
| Wrong place/provenance or byte range extending beyond the one direct `T` | Reject at exact place/range predicate, while retaining the unrelated frame. |
| ZST | No byte-range assertion is used to infer logical value equality, slot separation, or ownership. Keep the existing independent ZST contract open. |
| Callback normal and unwind | On both outcomes, preserve the direct-byte frame and return current `F`/target resources; unwind additionally follows actual cleanup and leaves cursor/destination state at the pre-call point. No callback state rollback is assumed. |

Each negative must reach its named predicate or compiler-bound obligation;
frontend/setup failures are not evidence. Full-source equality after ghost
stripping, exporter/decode/refinement, return, leak, dead-code and unwind gates
remain active. This matrix does not substitute for the complete actual body or
the repository-source caller proof.

## Feasible implementation sequence and open links

First inspect hosted exports for the actual bound and the exact runtime
callback/reference loan. Establish that `T: Freeze` in the blanket impl is
preserved as compiler-origin evidence and associated with the identical `T`
at the merge body. Next exercise the stock lifetime-byte laws on a scalar and
a raw-pointer-containing frozen record, with the separately owned pointee
mutation control. Only then choose the checked lemma or the bounded trusted
primitive. Integrate the frame around each actual comparator call, retaining
the callback's current `F` and any independently-owned indirect target on both
normal and unwind paths. Finally compose actual up/down resource posts with
bidirectional's odd-copy/guard and caller cleanup; establish A/B functional
facts only in their separate assumption layer.

Still open: whether the pinned translator preserves generic auto-trait
evidence at a call/body in an admissible form; whether stock VF lifetime loans
can be framed around the exact callback's shared `&T` arguments and closed on
unwind; and how actual callers realize source `T::own` without deriving it
from `&[T]` sharing. The source-linked direct-byte fact alone resolves none
of those ownership/caller obligations and is not full actual M3 acceptance.
