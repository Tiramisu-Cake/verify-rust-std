# KANI3300 A3 fixture review

## Reviewed identities

- Semantic candidate reviewed in [REVIEW.md](REVIEW.md): `e3c529a0d5a501987a36c1481bb7e8a48c80dc73`, tree `520f75b9df2be108f598b3c62f956666752bdfc5`, diff SHA256 `c39b6522f08dc951e130bd36f805ef83be9fe2e3fc692cee8eec7515b0e28028`, spec SHA256 `5ca8a699ce50a1f0fda972d79fd717c6aa8d9a25b15dec542cbdae8faa716b4b`.
- Fixture candidate before union-pointer correction: `55d704a56dbd5864ffb75e3d861a544c281f8ebd`, tree `f8c059aed34acbc2305651e361236854e51521a7`, diff SHA256 `f1e86aa80986620e486dd81a7de918fc9c69250eae4ac2376b93a951873e302e`, review packet SHA `7a468e809ec0a94ab5b1e58944237536b4fab09836e575e14a946edcfa06724a`, spec SHA `ef711d74c41e95b419bd0520c7f8a3293fbf12a296e6741a27efde1c7014ca99`.
- Final fixture candidate: `14c0a3c95b6ece62b01f96f663b455f8c5e155dc`, tree `8af499c3fb6c1108614e57c6ba446f66435c7d34`, diff SHA256 `8c7241c5a51d0dbf07da391f4bba6b89b53984a7ef556632e15412139dc1c93b`, delta packet SHA `0d2ef8a19a999505d6b45eba03bed9c58d80f959842eda2e9c35d572ea3fb125`, spec SHA `437c9dbeb6584fe3653acc613bd4f3d5bf8a0bccda9f3edf7d3935077ecea296`.

The final correction changes only the union probe's source observation pointer from `*const Byte` plus cast to `*const u8` obtained with `addr_of!(source.byte)`. This statically avoids seeding the unrelated delayed-UB union check while retaining a raw read of the source field after the custom MIR call.

## Static assessment

The fixture set has matching harness names and expected-output entries: pairing has 6/6, unsupported paths 2/2, and Move/Copy has 9/9. The pairing controls include three selected MaybeUninit argument positions interleaved with ordinary arguments, nested and repeated calls of the same payload size, and an initialized argument/return control. The unsupported controls cover a foreign bodyless function and a generic `FnOnce` invocation. Pinned `rustc_public` exposes `InstanceKind::Shim`; the candidate's protocol predicate excludes this kind, so the FnOnce fixture is aimed at the intended rejection path. Actual MIR resolution remains unobserved.

The custom MIR controls compare in-place `Operand::Move` with `Copy`, check that an initialized callee parameter remains readable there, check that moving an uninitialized payload into the callee still fails, check a callee write does not restore the caller source, include an ordinary by-value temporary control, and exercise a one-byte union source. The expected harness names and counts match the source annotations by static text inspection.

## Finding: padding deinitialization lacks a fixture control

No in-place Move fixture uses shadow storage with padding: the MaybeUninit payload is `u8`, and the union has one `u8` field. The semantic code's all-byte deinit mask was reviewed statically in `REVIEW.md`, but these tests do not distinguish full-extent deinitialization from a payload-only mask for a padded source. Add a custom MIR Move control with a padded shadow-storage type and a raw pointer observation of a padding byte if this invariant needs direct regression coverage. This is a coverage gap, not a finding that the implementation is incorrect.

There is no dedicated ordinary-union normal-return fixture; MaybeUninit normal-return controls cover the shared index-0 protocol, while the union fixtures cover argument Move/Copy only.

## Validation limits

Static review only. The committed expected files are reviewed as test expectations, not as observed results. No compile, MIR lowering, test, Kani, CBMC, Miri, or proof run was performed; all such outcomes remain `NOT_RUN`. No proof or runtime credit is claimed.
