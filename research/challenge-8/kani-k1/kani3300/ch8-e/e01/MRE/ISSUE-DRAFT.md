# Draft only — not published

Suggested title: Explicit loop modifies rejects writes to initialization shadow state under `-Z uninit-checks`

This is a correctness/feature interaction report. The concrete reproducer below
was observed on a downstream revision; current upstream reproduces a separate
MaybeUninit limitation first. Please do not interpret it as a verified upstream
minimal reproducer. A union-free reduction is proposed below and has not run.

## Reproducer and environment

```rust
#![feature(stmt_expr_attributes)]
#![feature(proc_macro_hygiene)]
use std::mem::MaybeUninit;

#[kani::proof]
fn e_h_write_then_read() {
    let mut destination = MaybeUninit::<u8>::uninit();
    let destination_ptr = destination.as_mut_ptr();
    let frame = std::ptr::slice_from_raw_parts_mut(destination_ptr, 1);
    let mut remaining = 1usize;

    #[kani::loop_invariant(remaining <= 1)]
    #[kani::loop_modifies(&remaining, frame)]
    #[kani::loop_decreases(remaining)]
    while remaining != 0 {
        kani::cover(remaining == 1, "E-H write loop body reached");
        unsafe { destination_ptr.write(41) };
        let written = unsafe { destination_ptr.read() };
        assert_eq!(written, 41);
        remaining -= 1;
    }
}
```

```sh
kani e_h_write_then_read.rs --harness e_h_write_then_read --exact \
  -Z unstable-options -Z loop-contracts -Z quantifiers -Z uninit-checks \
  --harness-timeout 600s --jobs 1 --cbmc-args --object-bits 12
```

Kani 0.68.0, Rust 1.101.0-nightly (7189d39d9, nightly-2026-10-23),
CBMC 6.11.0, CaDiCaL, x86_64-unknown-linux-gnu, default checks enabled.
Observed downstream tool: `Tiramisu-Cake/kani` at
`14bc57fdb99960240c4944845a3d985c8af4dcf7` (SEL1).

## Expected / observed

The destination byte and loop counter are explicitly framed. A real write
initializes the destination before the immediate read. Expected: successful
frame/init checks and reachable body cover.

Observed SEL1: OFF SUCCESS 69 properties / 0 failed; ON FAILURE 224 / 2 failed.
Both ON failures have class `assigns`, description
`Check that self->value is assignable`, at
`library/kani_core/src/mem_init.rs:120`. The body cover is satisfied; there is no
uninitialized-read failure for this positive root.

A companion copying one initialized byte into a distinct destination fails ON
270/5, on shadow `value` at :120 and `copy_by_id` fields at :170/:171/:173/:183.
Both alias negatives do report their intended uninitialized read, but also fail
shadow assigns; they cannot establish a clean control matrix.

Evidence: [run 43783430196](https://github.com/Tiramisu-Cake/kani/actions/runs/43783430196),
artifact 14190061402, member `rows/e_h_write_makes_readable/on/export.json`.
Run success is runner completion. Exact export SHA and failed IDs are retained
in the intake EVIDENCE.json, not inferred from the job conclusion.

Upstream `model-checking/kani` at
`0aac16ef62da9e9d5645782d458593e5d78143ba`: same OFF passes, ON fails an
`unsupported_construct` for raw pointers/unions at fixture:8, before testing
the intended shadow-frame interaction. This is **not** a measured reproduction
of the assigns failure upstream. The attached `shadow_write_u8_candidate.rs`
replaces MaybeUninit storage with initialized u8 and a raw-pointer write;
its compilation and outcomes on either revision remain NOT_RUN.

## Source investigation / hypothesis

At SEL1, raw stores become `MemoryInitOp::SetRef` in
`kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs:450-469`.
The model `library/kani_core/src/mem_init.rs:267-278` calls
`MEM_INIT_STATE.set`; `:120` writes `self.value`.

On **both pins**, explicit loop modifies targets are recorded by
`codegen_cprover_gotoc/codegen/statement.rs:260-274`; the loop hook in
`codegen_cprover_gotoc/overrides/hooks.rs:884-904` adds generated locals and emits
the clause, without adding initialization shadow state. This omission matches
the observed helper-field assigns failures. We have not inspected the transformed
GOTO/CBMC program to prove every attribution step.

Function modifies contracts have a separate shadow-static allowance at
`codegen_cprover_gotoc/codegen/contract.rs:142-170,230`. That path does not build
the loop clause, so its allowance does not resolve this observation.

A fix should preserve user-data framing and the initialization relation across
loop abstraction. Simply allowing/havocking all private state is not sufficient
evidence that inside/outside false bits and aliases remain correct. Suggested
regressions: primitive write, copy, no-write and OFF companions; initialized
witness plus unwritten inside/outside aliases and outside sentinel; scalar
invariant helper-call argument integrity.

Read-only search did not find an exact shadow-field/loop-frame issue. Related:
[#3300](https://github.com/model-checking/kani/issues/3300),
[#5151](https://github.com/model-checking/kani/issues/5151) (upstream union limitation),
[#4906](https://github.com/model-checking/kani/issues/4906) and
[#4790](https://github.com/model-checking/kani/issues/4790) (other generated/callee
assigns failures). A duplicate check and primitive upstream calibration remain
appropriate before publication. No issue/comment has been posted.
