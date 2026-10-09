# Actual generic `MaybeUninit::new`: source/MIR capture only

This is a bounded Cloud-only diagnostic for the pinned repository std at
`cd371e035c7e573760c43bf934d53e8118ee3e7d`. The complete
`library/core/src/mem/maybe_uninit.rs` SHA-256 is
`1230d267542337ee2842c29d8227cf8a58fe75c53a2a70efaee3922c4e8e25c0`;
`manually_drop.rs` is `f9cce798828cc852c00feeea9a6218c225b68d92727a5edbddc7c08a731a4f25`;
`hint.rs` is `ce89716d46b8060db2c2da1aef1d4bcccf90e0804fc021d4470c55203501315f`.
The actual generic union has exactly `uninit: ()` and
`value: ManuallyDrop<T>`, and its inherent `pub const fn new(val: T) ->
MaybeUninit<T>` body is exactly `MaybeUninit { value:
ManuallyDrop::new(val) }`. The actual select body still has two external
`MaybeUninit::new` calls. These pins must be checked against the full files,
not inferred from selected excerpts.

The preparer makes a disposable, source-local module with the same union
identifier, two field bytes, `impl<T> MaybeUninit<T>`, generic method signature
and method body. It retains `#[repr(transparent)]` and uses the same `T`
without Copy, Freeze, purity, size-positive or no-panic premises. The local
crate omits the core-only `#[stable]`, `#[lang = "maybe_uninit"]`,
`#[derive(Copy)]`, `#[rustc_pub_transparent]`, method `#[rustc_const_stable]`,
`#[must_use]` and `#[inline(always)]` attributes; each omission is explicit
in the source certificate. The generated crate adds the explicit
`#![feature(transparent_unions)]` attribute, the local
`std::mem::ManuallyDrop` import and two diagnostic wrappers. It adds no
dead-code suppression.
Its separate generic wrapper calls the genuine
external `std::mem::MaybeUninit::<T>::new(val)` unchanged. A second wrapper
calls the local method only to make the local body visible to the exporter.
The local type and function have **different DefIds** from the actual core
items. The wrapper does not redirect the external call or make that call use
the local body.

Run only on the identified Cloud provider with the existing frozen toolchain
and exporter, without changing kernel, translator, parser, schema, prelude,
specifications, runtime std or refinement checker. Preserve the exact
original/verified source pair, complete normal and readonly MIR binaries and
decoded text, compiler/export/decode/refinement logs and exits, full local
body/union declaration inventories, actual external-call DefPath and type
substitutions, active `value` field, `ManuallyDrop::new` move, normal and unwind
successors. Where the exporter omits or encodes a field differently, report
`UNOBSERVED` with the full raw MIR; do not synthesize a pass. A setup,
frontend, unsupported-union or refinement failure is inconclusive, not a
proof negative. No verifier body proof or runtime summary is requested.
The VeriFast dead-code check is therefore not run by this source/MIR lane;
its status remains unobserved, not disabled or passed.

The falsifiable hypothesis is only that this same-source local copy can be
exported as a complete generic body and the independent wrapper retains a
distinct external call. Success establishes a source/MIR observation, not
actual-callee linkage or correctness. A genuine future generic constructor
would need linear `<T>.own` transfer into a reviewed `MaybeUninit<T>` ownership
interpretation and checked union/storage/borrow/move/drop semantics; the stock
generic `MaybeUninit_own` is opaque, and C8 already failed its SAFE prototype
before body verification. Keep unrestricted implicit-Sized `T` (including
symbolic ZST, non-Copy and panicking Drop); the separate concrete aligned ZST
layout boundary remains open. No generic new, as_mut_ptr, assume_init or
whole-select summary is accepted from this capture.

Cloud integration calls `prepare.py --proof-root ROOT --cloud-dir CLOUD
--evidence EVIDENCE` with a fresh `/workspace` evidence path, then
`capture.py --cloud-dir CLOUD --evidence EVIDENCE --tool-home TOOL
--compiler-sysroot SYSROOT --deadline-epoch EPOCH` in the same identified
Cloud Build. The complete proof inputs are this card, `SOURCE-PINS.json`,
both scripts and the three pinned repository std files above. The Cloud
infrastructure dependencies are the reviewed `provider.py`, the pinned
exporter, refinement checker, schema and toolchain/sysroot, and `capnp`.
The collector emits the source certificate, exact source pair, full
normal/readonly MIR binary and text, all stage logs/exits and
`capture-result.json`. The latter is always `accepted=false`; absent
exporter fields are `UNOBSERVED` and any nonzero setup/export/refinement
stage is `INCONCLUSIVE`. No local execution or proof run is part of this card.
