# CMP2 repair contract — static diagnosis, native NOT_RUN

The CMP1 full candidate is 6ef9fd72066443f7f113440ba32f77f310520a93. Pin/toolchain/KT2 and the R/S/P descriptor, ghost state, argument buffer and compound-copy rules stay fixed.

## Defect and applicability

`delayed_ub/instrumentation_visitor.rs::find_all` visits statements/terminators, but MIR parameters have no assignment statement. It can therefore issue delayed checks on an ordinary by-value parameter with fresh, false shadow bytes, even though the caller supplied a typed value. The exact std path is `PolymorphicIter::drop` -> `alive.clone()` -> `partial_drop(alive: IndexRange)` -> `SliceIndex::get_unchecked_mut(self: IndexRange)` -> `IndexRange::len`. Struct reference unsizing preserves the prefix address and does not initialize or destroy R/S. The failing-instance points-to binding is not retained evidence: causal confirmation awaits native.

## Fix and invariant

At BB0 seed only supported sized ordinary formal parameters whose exact place can receive a delayed get. Preserve the existing caller operand checks. A typed-mask setter initializes only the parameter allocation's data bytes and leaves its padding false. Exclude unions and every by-value storage-containing type, including nested products/ManuallyDrop; those retain their existing Store/Load protocol and empty S witnesses. A pointer/ref parameter setter covers the pointer value, never its pointee. Never seed R again after a body write: later poison must remain observable. Select the actual entry instruction and terminator source even for an empty-statement block.

This is an ordinary typed-write representation repair; no new memory model/trusted premise. Unsupported ordinary layouts remain unseeded. Aggregate/move/ManuallyDrop/DST projection and IntoIter tests remain independent discriminators.

## Controls and limits

Retain all 18 CMP1 selectors and all 35 negative harness requirements, plus one selector of minimal positive repros and one of ordinary-parameter source/body poison negatives (20 total). Keep every per-root golden failure and u8 padding-byte diagnostic: incidental *const u8 failures cannot substitute for the intended byte read. Use direct u8 padding dereferences to name that obligation at the fixture source. No native/compile/proof acceptance is claimed before the single authorized, reviewed Cloud attempt; dispatch requires a coordinator GO on the exact published packet. Budget cap $0.60, proposed reservation $0.540, spend/reserve $0 at pre-build.
