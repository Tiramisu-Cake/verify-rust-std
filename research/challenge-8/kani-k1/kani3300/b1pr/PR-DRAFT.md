# Preserve memory initialization checks at unresolved calls

With `-Z uninit-checks`, the local uninitialized-memory visitor returned early when `try_resolve_instance` returned `Err`. It visited the call operands twice, then skipped the common epilogue that publishes the current instrumentation target. This discarded the entire target: the unsupported-call check, operations collected while visiting the operands, and any union argument entry loads attached to a statement-free entry block. Separately, `Virtual`, `Shim`, and `LlvmIntrinsic` instances fell through a catch-all arm without call-specific handling.

For example, this regression uses Rust 2021 (`--edition 2021`) and keeps the union read in the call terminator of an otherwise empty entry block:

```rust
#![feature(core_intrinsics, custom_mir)]
#![allow(internal_features)]
use core::intrinsics::mir::*;

union Word {
    byte: u8,
    word: u32,
}

fn identity(value: u32) -> u32 { value }

#[custom_mir(dialect = "runtime", phase = "optimized")]
#[inline(never)]
unsafe fn indirect(value: Word, f: fn(u32) -> u32) -> u32 {
    mir! {
        { Call(RET = f(value.word), ReturnTo(done), UnwindUnreachable()) }
        done = { Return() }
    }
}

#[kani::proof]
fn check() {
    let _ = unsafe { indirect(Word { byte: 42 }, identity) };
}
```

The call through `f` cannot be resolved statically. Its target must still retain the union's entry `LoadArgument`, the check of `value.word`, and the unsupported-call check. The regression expects the partially initialized read to fail. A companion using `Word { word: 42 }` expects the read check to succeed; both report the unsupported function-pointer call. Custom MIR fixes the call shape so the operand read and entry load exercise the discarded-target path directly.

## Changes

- Visit each call's operands with one `super_terminator` call. On resolution failure, append `Unsupported` and leave the call arm through the common epilogue, preserving all collected operations and entry loads.
- Handle instance kinds explicitly: treat shims with MIR bodies like ordinary MIR callees, including the union argument transfer protocol; emit `Unsupported` for bodyless `Shim`, `Virtual`, and `LlvmIntrinsic` instances. Existing `Item` and `Intrinsic` handling is retained.
- Let the local visitor own unsupported-call instrumentation for function-pointer and virtual calls. The delayed-UB visitor no longer adds a duplicate guard, so reporting also works when there are no delayed-UB targets.
- Turn a function-item resolution error into an unsupported-check diagnostic instead of unwrapping the error.

This relates to [the memory initialization tracking issue #3300](https://github.com/model-checking/kani/issues/3300). Function-pointer and vtable call effects remain unsupported.

## Diagnostics and regressions

Function-pointer and trait-object calls use the existing messages beginning `Kani does not support memory initialization checks across calls through function pointers` and `Kani does not support memory initialization checks across trait object method calls`. The existing `delayed-ub-unsupported-call` expected output is unchanged; the local visitor now emits these checks independently of delayed-UB targets. Bodyless shims report `Kani does not support memory initialization checks across calls to bodyless Shim instances`. A shim with a MIR body follows the ordinary callee path; any unsupported call inside it is checked in that body.

Add 20 fixtures in `tests/expected/uninit/unresolved-calls`: ten cases, each with and without a safe `copy_nonoverlapping` operation to seed delayed-UB analysis. They cover direct-call positive controls, function pointers, erased and wrapped pointers, escaped global pointers, trait-object calls, shim calls, pending operand checks, and initialized/partially initialized union entry arguments. The pending-operand and union-entry tests use custom MIR and require named safety-check outcomes alongside the unsupported-call diagnostic. All new fixtures compile with `-D warnings`. The shim fixtures expect the bodyless-shim diagnostic encountered by the tested call chain. Existing upstream regression sources and expected outputs are unchanged.

## Testing

- [Focused uninitialized-memory CI in the fork](https://github.com/Tiramisu-Cake/kani/actions/runs/43110714635): PASS for all selected suites (`kani`: 22, `expected`: 83, `ui`: 14, script: 1). Formatting, build, and Clippy with `-D warnings` also passed. This run uses the same source and tests with a separate CI-only workflow commit.
- [Full Kani CI in the fork](https://github.com/Tiramisu-Cake/kani/actions/runs/43112332778): regression jobs passed on `ubuntu-22.04`, `ubuntu-24.04`, `ubuntu-24.04-arm`, and `macos-15-intel`; performance, LLBC regression, documentation, and benchcomp jobs also passed. The `macos-14` job was cancelled because the fork had no available runner; the overall run is therefore marked cancelled.

*Disclosure: this change and description were prepared with AI assistance.*
By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.
