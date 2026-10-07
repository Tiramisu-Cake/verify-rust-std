# Restricted one-element MaybeUninit copy profile

This profile proposes a staged intrinsic contract dependency for the M2a
scratch-copy investigation. It does not establish a proof of SmallSort or
authorize extending the model beyond the domain below. The actual Rust source,
kernel, exporter, translator, and refiner remain unchanged.

## Exact inputs

- VeriFast source: `f76012fb518703b1d98e243ac4f487f16877cfcb`.
- Source patch: `copy.patch`, SHA-256
  `cbce890459182725932101dc3c8ca6f9f87a8ca1dd0e7b6cf5b5faca620a5f57`.
- Only modified source path: `bin/rust/std/lib.rsspec`.
- Frozen input `bin/rust/std/lib.rsspec` SHA-256:
  `2da7acfb6596f8abec90c103ef7f294152c18f974b88124669882fc051272999`.
- Patched output `bin/rust/std/lib.rsspec` SHA-256:
  `113b37163b6cb5527a4ba37d2a33d469387d484fc30519aa774a77521c469340`.
- `bin/rust/prelude_core.rsspec` is byte-identical to pinned input SHA-256
  `435146cd4632541241563ae45b146704c14f6f7cdd3b5d404837617f08bc91b8`.
- `bin/rust/rust_belt/points_to_at_lifetime.rsspec` is byte-identical to
  pinned input SHA-256
  `dd27384b6c17b733c8e36487ed82574fdf290ac5bc4e4becd24076dbebfffe4b`.
- Fixture: `copy-cases.rs`, SHA-256
  `e93c87b0fd20c4b93baf33533c954876190c4733e8250c4f3a5e05dba08565e2`. The
  fixture has no expected-error oracle; every `TARGET` remains inconclusive
  until exact hosted diagnostics are reviewed.

## Contract boundary

The patch preserves the existing initialized-array contract for every call
except exactly `count == 1 && size_of::<T>() > 0`. In that one-element branch,
the source is one initialized `T` chunk with a read fraction and the
destination is one full writable `points_to_<T>` chunk, whose abstract old
state may be `none` or `some(old_T)`. The post retains the source chunk and
creates one initialized destination chunk containing the exact source value.
This is a typed-value transfer in the frozen `T` memory model: it does not
serialize values as bytes, so pointer-valued T fields retain the abstract
provenance represented by that value. The intrinsic contract mentions no
`<T>.own` predicate; ownership remains at the source and is neither removed
nor manufactured at the destination.

The staged branch requires positive source and destination addresses (`0 <
src as usize` and `0 < dst as usize`); both addresses
aligned to `align_of::<T>()`; positive `size_of::<T>() <= isize::MAX`; no
integer overflow in either byte endpoint; both object ranges within their
pointer-provenance limits; and numerically disjoint half-open byte ranges.
These are literal preconditions, not facts inferred from a local ghost shadow.
The destination resource carries writable permission for exactly one typed
slot. The contract is non-unwinding and terminating, as for the stock
intrinsic.

This is a trusted specification change, not a verified implementation of the
copy. Its proposed justification is deliberately small: for one positive-size
element, the actual intrinsic copies the valid abstract source value into
writable, non-overlapping storage, leaving source memory unchanged. The
separating source/destination resources and explicit numeric range condition
prevent aliasing in this branch, including partial byte overlap. Pointer
provenance is copied as part of the abstract T value, not reduced to an integer
or ordinary byte list.

The profile covers only a destination represented by the stock
`points_to_<T>` option model: uninitialized `none` or a previous valid `T`
value `some(old)`. It does not model arbitrary initialized-invalid byte
patterns (for example, `MaybeUninit::<&T>::zeroed()` contains a null pointer
that is invalid as a Rust reference), ZSTs, count zero, counts other than one,
or typed arrays. The old
initialized-only contract remains active for those branches. No unrestricted
`MaybeUninit<T>` or generic `copy_nonoverlapping` claim follows. This boundary
must remain explicit in every hosted report.

## Fixture intent

`copy-cases.rs` contains a single direct intrinsic helper that is verified in
the shared file prefix, plus isolated cases for:

- initialized source copied into a `none` destination, preserving one source
  `<T>.own` resource;
- initialized source copied over a valid `some(old)` destination, with the
  old value not treated as owned by the scratch slot;
- an unrelated frame cell preserved;
- the physical copy without requiring or creating any `<T>.own` resource, and
  a marked negative that attempts to assert a second identical `<T>.own` after
  retaining the single source owner;
- missing destination write permission, uninitialized source, exact overlap,
  misaligned source, and misaligned destination at marked call sites.
- count-zero, count-two initialized-byte arrays, and a concrete ZST copy under
  the unchanged old initialized-array contract. These are boundary controls,
  not evidence that the staged positive-size option<T> branch handles ZSTs or
  arbitrary counts.

The negative markers deliberately have no predicted diagnostic metadata.
Hosted output must first show failures at their intended source line and
primitive precondition, rather than setup, parser, or frontend errors. Add
explicit expected stage/predicate/location only after observing the exact
diagnostic. The fixture does not run local builds or verifier commands.

## Required next review gates

Before integration, review the spec change as a trusted semantic dependency
and verify the patch applies to the exact pinned tree. Then on a hosted runner,
run the fixture and inspect complete logs, original/ghost-stripped bytes,
artifact hashes, marker outcomes, and resource reports. A positive case must
prove destination initializedness and unchanged source ownership; the
missing-resource and range controls must reject at their marked obligation.
The existing initialized-destination stock contract needs its own positive
control. None of these results establish callback lifetime recovery,
`merge_up`, a whole SmallSort helper, ZST support, arbitrary destination byte
states, or the full generic Rust safety contract.

No local compilation, verifier, fixture runner, or executable test was run.
