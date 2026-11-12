# Preserve memory initialization checks at unresolved calls

Refs #3300

A failed call resolution in the local uninitialized-memory visitor returns before publishing the Call terminator target. This loses checks collected from the operands and can also lose union argument loads attached to a statement-free entry block. Visit the operands once, append Unsupported after the pending operations, and reach the common target flush exactly once. The resulting operation order is entry LoadArgument, operand checks, Unsupported, then the original call.

The local visitor owns function-pointer and virtual-call diagnostics, including when delayed-UB analysis has no seeds. A shared fallible resolver rejects unresolved function items, virtual calls, LLVM intrinsics and nonforeign callees without an actual instance body. Generated shims use `Instance::body().is_some()` rather than definition-level `has_body()`. Intrinsic and foreign allocation models retain their existing dispatch. Seed collection ignores failed resolutions and collects only recognized intrinsic targets; points-to analysis preserves previous edges when it cannot follow a callee.

MIR-backed shims with ordinary by-value storage retain the usual analysis and instrumentation path. Before StoreArgument, a shim call with union-containing or unknown argument/destination storage is rejected. The same conservative check guards callee entry before LoadArgument; tuples, arrays, ADT fields and closure captures cannot hide union storage. References and raw pointers do not transfer their pointee's by-value shadow. This guard establishes no new shadow model or ABI protocol: existing top-level union argument transfer for ordinary Item calls remains unchanged, with no new return-value handshake.

The exact [statement-free partial-entry regression fixture](https://github.com/Tiramisu-Cake/kani/blob/7ef191d8dd589d5fe589d1aff164d33ae35677f0/tests/expected/uninit/unresolved-calls/entry-partial-plain.rs) uses custom MIR with Rust 2021 and panic=abort. It is a regression fixture, not a measured minimal reproducer: a matched base run has not established false SUCCESS for this input. Its initialized companion distinguishes successful operand reads from the unsupported-call failure. Other controls cover direct Item calls, function pointers, trait objects, erased/wrapped/global pointers, pending operand reads, Fn-trait pointer calls and non-shadow function-item/drop/closure behavior, with plain and ordinary-byte-copy seeded variants. Fn-trait syntax alone does not establish a particular generated instance kind.

The claim is limited to Call target retention and the modified uninitialized-memory/points-to paths. Reachability has an earlier FnDef resolver unwrap; a local runtime Unsupported cannot protect a compile-time failure there. The separate UnionAsField statement flush/index defect is outside this change. General ABI support, union returns and indirect-call memory effects are not added.

Testing: candidate `7ef191d8dd589d5fe589d1aff164d33ae35677f0` (tree `e8315096d962a0851430850aa225d8f32cdb6568`) is **NOT_RUN** pending coordinator targeted and full fork CI. Static rustfmt and `git diff --check` passed; compilation, Clippy, generated-body/ABI bindings and reached properties remain NOT_RUN. Goldens specify expected outcomes, not observations. Existing controls are unchanged. Historical results on other source/test trees do not validate this diff.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with AI assistance.*
