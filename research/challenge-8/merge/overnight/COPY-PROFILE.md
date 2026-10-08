# Restricted one-element MaybeUninit copy profile

This profile proposes a staged intrinsic contract dependency for the M2a
scratch-copy investigation. It does not establish a proof of SmallSort or
authorize extending the model beyond the domain below. The actual Rust source,
kernel, exporter, and refiner remain unchanged; the translator has the narrowly
scoped C1 lowering recorded below.

## Exact inputs

- VeriFast source: `f76012fb518703b1d98e243ac4f487f16877cfcb`.
- Source patch: `copy.patch` (includes the C1 count-literal lowering), SHA-256
  `0f1b65503d12affc3b45338304b64ebc85298034a23d83a814a4a8408966d518`.
- Modified source paths: `bin/rust/std/lib.rsspec` and
  `src/rust_frontend/vf_mir_translator/vf_mir_translator.ml` only.
- Frozen input `bin/rust/std/lib.rsspec` SHA-256:
  `2da7acfb6596f8abec90c103ef7f294152c18f974b88124669882fc051272999`.
- Patched `bin/rust/std/lib.rsspec` SHA-256:
  `8901c1b30675ee48cdc2272787e53816573afe33e3a9765b434be79ca379f472`.
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
  `42343dc6fb5c602a6feba753afb62d8327f2b17858feed138e2cd71dec41b971`. The
  fixture has no expected-error oracle; every `TARGET` remains inconclusive
  until exact hosted diagnostics are reviewed.

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

The negative markers deliberately have no predicted diagnostic metadata.
Hosted output must first show failures at their intended source line and
primitive precondition, rather than setup, parser, or frontend errors. Add
explicit expected stage/predicate/location only after observing the exact
diagnostic. The fixture does not run local builds or verifier commands.

## Hosted parser-format correction and C1 lowering

The first hosted source run rejected a block-comment `req`/`ens` wrapper. A
follow-up conditional-expression form exposed a separate binding issue: the
Rust verifier checks both conditional assertion branches but does not export
branch pattern variables to the following postcondition. The current patch
leaves the original intrinsic contract unchanged and places the staged,
unconditional precondition/postcondition on a synthetic spec target. C1
translates only a call whose resolved name is exactly
`std::ptr::copy_nonoverlapping`, whose three arguments are present, and whose
translated third argument is an AST literal integer `1`; it preserves all
three arguments and redirects that call to
`std::ptr::merge_copy_nonoverlapping_one`. Dynamic count expressions and other
names remain on the stock target. This translator change is an additional
trusted semantic dependency and needs separate code review and hosted
calibration. Static patch application and whitespace checks pass; hosted
parsing/verifier evidence is still required.

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
