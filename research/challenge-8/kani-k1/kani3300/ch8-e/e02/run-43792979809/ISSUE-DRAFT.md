Title: Loop contracts: explicit `loop_modifies` rejects initialization shadow writes with `-Z uninit-checks`

A raw write to an initialized `u8` fails a loop assigns check when initialization checking is enabled:

```rust
#![feature(stmt_expr_attributes)]
#![feature(proc_macro_hygiene)]

#[kani::proof]
fn shadow_write_u8_candidate() {
    let mut value = 17u8;
    let pointer = &mut value as *mut u8;
    let mut remaining = 1usize;

    #[kani::loop_invariant(remaining <= 1)]
    #[kani::loop_modifies(&remaining, pointer)]
    #[kani::loop_decreases(remaining)]
    while remaining != 0 {
        unsafe { pointer.write(41) };
        assert_eq!(unsafe { pointer.read() }, 41);
        remaining -= 1;
    }
    kani::cover(remaining == 0, "primitive write loop returns");
}
```

Save as `shadow_write_u8_candidate.rs` and run:

```sh
kani shadow_write_u8_candidate.rs --harness shadow_write_u8_candidate --exact \
  -Z unstable-options -Z loop-contracts -Z quantifiers -Z uninit-checks \
  --harness-timeout 600s --jobs 1 --cbmc-args --object-bits 12
```

Kani 0.68.0, unmodified upstream `0aac16ef62da9e9d5645782d458593e5d78143ba`;
Rust 1.101.0-nightly (7189d39d9, nightly-2026-10-23), CBMC 6.11.0,
CaDiCaL, x86_64 Linux, default checks enabled.

Expected: verification succeeds. The loop frames both the counter and the destination byte, and writes the byte before reading it.

Actual: FAILURE, with exactly one failed check:

```text
Check that self->value is assignable
library/kani_core/src/mem_init.rs:93
kani::mem_init::MemoryInitializationState::set::<1>.assigns.1
```

The export reports 93 successful checks, one failed check, and the return cover satisfied; no unsupported constructs or warnings. Removing only `-Z uninit-checks` succeeds. Two separately tested controls also succeed with and without initialization checking: the same framed loop with the raw write and value assertion omitted (retaining the raw read and counter update), and the raw write/read/assertion without a loop.

This appears to be an omission in the loop frame's treatment of instrumentation state. At this revision, [statement.rs:260–274](https://github.com/model-checking/kani/blob/0aac16ef62da9e9d5645782d458593e5d78143ba/kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs#L260-L274) records the explicit targets; [hooks.rs:884–904](https://github.com/model-checking/kani/blob/0aac16ef62da9e9d5645782d458593e5d78143ba/kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs#L884-L904) adds generated locals but no initialization-shadow allowance. The helper writes shadow `self.value` at [mem_init.rs:93](https://github.com/model-checking/kani/blob/0aac16ef62da9e9d5645782d458593e5d78143ba/library/kani_core/src/mem_init.rs#L93). Function contracts already handle that static separately in [contract.rs:142–170,230](https://github.com/model-checking/kani/blob/0aac16ef62da9e9d5645782d458593e5d78143ba/kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs#L142-L230).

Related assigns reports: #4906 and #4790; this example fails on initialization shadow state with a primitive destination.

*Disclosure: this issue was prepared with the help of AI assistants.*
