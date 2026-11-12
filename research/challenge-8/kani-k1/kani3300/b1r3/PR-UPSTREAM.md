Title: Preserve memory initialization checks at unresolved calls

Refs #3300

With `-Z uninit-checks`, when the uninitialized-memory visitor cannot resolve a call (a function pointer, a trait object, ...), `visit_terminator` returns early. Everything it had already collected for that terminator is dropped: the checks on the call's operands and, in a statement-free entry block, the argument loads. Kani still reports that it does not support checks across such calls, but the actual uninitialized read in the operand is no longer reported.

Example ([`pending-ops-plain.rs`](https://github.com/Tiramisu-Cake/kani/blob/7ef191d8dd589d5fe589d1aff164d33ae35677f0/tests/expected/uninit/unresolved-calls/pending-ops-plain.rs), custom MIR so that the read is an operand of the call):

```rust
#[custom_mir(dialect = "runtime", phase = "optimized")]
unsafe fn indirect(f: fn(u8) -> u8, pointer: *const u8) -> u8 {
    mir! {
        { Call(RET = f(*pointer), ReturnTo(done), UnwindUnreachable()) }
        done = { Return() }
    }
}
```

The harness passes a pointer to an uninitialized heap byte. On `main` the only failed check is the "calls through function pointers" diagnostic, and the `indirect.safety_check` for `*pointer` is missing. With this change both are reported.

### Change

- Visit the operands once, add `Unsupported` after the operations already collected, and push the target through the common path. The resulting order is entry `LoadArgument`, operand checks, `Unsupported`, then the call.
- The local visitor owns the diagnostic, so it no longer depends on delayed-UB analysis having seeds.
- The visitor and the points-to analysis share one fallible call resolution. Unresolved items, virtual calls, LLVM intrinsics and non-foreign callees without a body are rejected. Generated shims are checked with `Instance::body()` instead of the definition-level `has_body()`. Seed collection skips failed resolutions instead of unwrapping, and points-to keeps its existing graph when it cannot follow a callee.
- MIR-backed shims keep the normal path for ordinary by-value storage. A shim call whose argument or return storage contains a union, or whose storage cannot be classified, is rejected before `StoreArgument`/`LoadArgument`. No new shadow transfer is added.

### Testing

`tests/expected/uninit/unresolved-calls` adds 22 harnesses: direct calls, function pointers, trait objects, erased, wrapped and global function pointers, Fn-trait pointers, generated shims, pending operand reads and statement-free entry blocks with initialized companions. Each comes in a plain variant and a "seeded" variant whose ordinary byte copy gives delayed-UB analysis targets.

On `main` six of them fail: in the entry-block and pending-read cases the `indirect.safety_check` properties are missing from the results. With this change all uninit-checks suites pass.

CI on this commit in my fork: [Kani CI](https://github.com/Tiramisu-Cake/kani/actions/runs/43208073261) passes the regression jobs on Ubuntu 22.04, Ubuntu 24.04, Ubuntu 24.04 ARM and macOS 15 Intel, plus perf, documentation, LLBC and benchcomp; Cargo Deny and Format Check also pass. The macOS 15 Intel job needed one rerun after a CBMC timeout in the unrelated `cargo_autoharness_multichareq_searcher` test. The macOS 14 job does not start on the fork (GitHub reports that the `macos-14-arm64-us-default` configuration is not supported).

### Not in this PR

- Reachability still unwraps the resolution of `FnDef` calls before this pass runs.
- The early flush in the `UnionAsField` statement path is a separate issue.
- General ABI support, union return values and memory effects of indirect calls are not added.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
