# Restricted one-element MaybeUninit copy profile

This profile proposes a staged intrinsic contract dependency for the M2a
scratch-copy investigation. It does not establish a proof of SmallSort or
authorize extending the model beyond the domain below. The actual Rust source,
kernel, exporter, and refiner remain unchanged; the translator has the narrowly
scoped C1 lowering recorded below.

## Exact inputs

- VeriFast source: `f76012fb518703b1d98e243ac4f487f16877cfcb`.
- Source patch: `copy.patch` (includes the C1 count-literal lowering and
  scalar-fraction syntax correction), SHA-256
  `da167ee095e9fb5f425e2d604dd46a973a8c1e3a5121b2c87cc3546b0ec8e9a5`.
- Modified source paths: `bin/rust/std/lib.rsspec` and
  `src/rust_frontend/vf_mir_translator/vf_mir_translator.ml` only.
- Frozen input `bin/rust/std/lib.rsspec` SHA-256:
  `2da7acfb6596f8abec90c103ef7f294152c18f974b88124669882fc051272999`.
- Patched `bin/rust/std/lib.rsspec` SHA-256:
  `5c55f95a6a098ef47ac9376e3bc6409fc744637da62d5b9b10b724c85dd9b5f8`.
- Frozen `src/rust_frontend/vf_mir_translator/vf_mir_translator.ml` SHA-256:
  `c1eb897673f88b0b8dc50798deca603bdad2c60818b6d5380ccf1dda055fe445`.
- Patched translator SHA-256:
  `720b7525a70032d7f67d3f306eedde2134397e70eec6f933e18a56a0e691c7e7`.
- `bin/rust/prelude_core.rsspec` is byte-identical to pinned input SHA-256
  `435146cd4632541241563ae45b146704c14f6f7cdd3b5d404837617f08bc91b8`.
- `bin/rust/rust_belt/points_to_at_lifetime.rsspec` is byte-identical to
  pinned input SHA-256
  `dd27384b6c17b733c8e36487ed82574fdf290ac5bc4e4becd24076dbebfffe4b`.
- Fixture: `copy-cases.rs`, SHA-256
  `b67234fb3bcb7d1d4e6ee601f45ab4eeb2527296d49693bf71a04f5f76498872`.

## Contract boundary

The patch preserves the existing initialized-array contract for calls not
selected by the translator's narrow count-literal mapping. Only an actual
`std::ptr::copy_nonoverlapping` call with an AST third argument that is the
integer literal `1` is lowered to the synthetic
`std::ptr::merge_copy_nonoverlapping_one<T>(src, dst, count)` spec target; the
three actual arguments are preserved. Nonliteral counts and other callees keep
the original intrinsic target and contract. The synthetic contract has
unconditional assertions, including `count == 1 && size_of::<T>() > 0`, so its
pattern variables are bound directly. In that one-element synthetic contract,
the source is one initialized `T` chunk with a read fraction and the
destination is one full writable `points_to_<T>` chunk, whose abstract old
state may be `none` or `some(old_T)`. The post retains the source chunk and
creates one initialized destination chunk containing the exact source value.
This is a typed-value transfer in the frozen `T` memory model: it does not
serialize values as bytes, so pointer-valued T fields retain the abstract
provenance represented by that value. The intrinsic contract mentions no
`<T>.own` predicate; ownership remains at the source and is neither removed
nor manufactured at the destination.

The synthetic spec requires positive source and destination
addresses (`0 < src as usize` and `0 < dst as usize`); both addresses
aligned to `align_of::<T>()`; positive `size_of::<T>() <= isize::MAX`; no
integer overflow in either byte endpoint; both object ranges within their
pointer-provenance limits; and numerically disjoint half-open byte ranges.
These are literal preconditions, not facts inferred from a local ghost shadow.
The destination resource carries writable permission for exactly one typed
slot. The contract is non-unwinding and terminating, as for the stock
intrinsic.

This is a trusted specification and translator-lowering change, not a
verified implementation of the copy. The lowering is admitted only for the
exact `std::ptr::copy_nonoverlapping` name and an AST integer literal `1`; it
preserves the three source arguments and redirects to a synthetic declaration
whose unconditional precondition enforces positive-size `T`, count one, and the
stated memory domain. It does not rewrite dynamic counts, count zero, count two,
or other call names. The proposed justification is deliberately small: for one positive-size
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
that is invalid as a Rust reference), ZSTs, or dynamic counts other than the
stock path. Literal count zero and count two stay on the old intrinsic
contract. Literal count one with ZST `T` is redirected to the synthetic spec,
which rejects at its positive-size precondition; its fixture is a mapping
boundary calibration, not a stock-contract control. No unrestricted
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
- count-zero and count-two initialized-byte arrays that stay on the original
  intrinsic contract; a literal count-one concrete ZST case is a support-only
  mapping calibration expected to reach the synthetic positive-size gate. It
  is not accepted as proof evidence, nor evidence for general ZST support.

The hosted run `37706472350` reached all fixture stages. The direct missing-destination case failed at the synthetic intrinsic destination `points_to_<T>` requirement, the duplicate-owner assertion failed for the second `<T>.own`, and the uninitialized source was rejected while eliminating the `none` option from the initialized source chunk. These three observed diagnostics are now pinned with exact rejection metadata. The other target negatives previously failed at the wrapper predicate `copy_one_domain`, so overlap and alignment cases now call the intrinsic directly and omit spatial chunks; they isolate only the corresponding pure range/alignment premise. Their exact diagnostics remain unknown until the next hosted run.

The run also recorded successful copy helper and case return/leak checks for positive fixtures, but classified them `INCONCLUSIVE`: the common `CopyControlZst` declaration caused seven unrelated generated type helper headers in every case, violating exact header admission. The declaration now lives solely inside the ZST calibration case so ordinary positive cases contain no unrelated helpers. The ZST calibration remains support-only and inconclusive. No local builds or verifier commands were run.

## Hosted parser corrections and C1 lowering

The first hosted source run rejected a block-comment `req`/`ens` wrapper. A
conditional-expression alternative exposed that branch pattern variables do
not reach the postcondition, so the patch places the unconditional staged
contract on a synthetic target and leaves the original intrinsic contract
unchanged. A later hosted parse rejected scalar fractional points-to written
as `[?f]*src |-> ?v`; the current patch uses the stock parser form
`[?f](*src |-> ?v)` and `[f](*src |-> v)`. C1 translates only calls whose
resolved name is exactly `std::ptr::copy_nonoverlapping`, with three arguments
and translated third argument an AST integer literal `1`; it preserves all
three arguments and redirects to `std::ptr::merge_copy_nonoverlapping_one`.
Dynamic counts and other names remain on the stock target. The translator
change is an additional trusted dependency requiring separate review and
hosted calibration. Static patch application and whitespace checks pass;
hosted parsing/verifier evidence is still required.

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
states, or the full generic Rust safety contract. The C1 translator lowering
is itself an additional trusted semantic dependency and requires explicit
review of its exact name/count guard in addition to the spec contract.

No local compilation, verifier, fixture runner, or executable test was run.

## C1e fresh body evidence

Run37707274811/proofe9c10d6b: four full initializedness/value/ownership/frame
positives and the explicit no-owner positive PASS; count0/count2 stock controls
PASS; missing-destination, second-owner and uninitialized-source exact negatives
accepted with fail-closed mutations. Direct overlap and both alignment controls
reach their intended primitive requirements; exact new oracles are pinned for
another fresh combined matrix. Their original INCONCLUSIVE classifications remain
historical evidence. C1 is a bounded TRUSTED primitive specification, not a proof
of std intrinsic body, ZST, arbitrary invalid byte state or actual merge.

## C1f accepted bounded component

Run [37707794942](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37707794942),
proof `b8f25c1831152660fa6b2eba667dc8d8e068d2ad`, accepts five positive cases,
stock count-zero/count-two controls and all six intended resource/range/alignment
negatives with fail-closed classifier mutations. Full source identity, stages,
body execution, normal/unwind, return/leak and dead-code gates pass. Earlier
INCONCLUSIVE classifications above remain historical. This accepts only the
bounded trusted C1 contract described above; actual merge, concrete ZST and
arbitrary invalid destination byte states remain open. Compatibility after the
new cleanup kernel dependency still requires its separate full hosted matrix.
