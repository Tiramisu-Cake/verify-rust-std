# `ManuallyDrop::new` CFG regression

`forget.rs` checks the minimal generic identity lowering of
`std::mem::ManuallyDrop::new`. `shared_cleanup.rs` checks an ordinary caller and
a generic shared-cleanup caller with a real unwind-capable call. Its local
function named `new` is an ordinary Rust function and serves as a name-boundary
control for the standard-library special case. Each should-fail control has a
separate command so its expected failure cannot mask another function.

Historical baseline evidence shows `shared_cleanup` passes on the pre-candidate
translator, while the minimal `forget` case fails with orphan dead code. The
candidate is expected to accept `forget`, the ordinary caller, and the
shared-cleanup caller; the two negative controls should fail at their marked
postconditions. These are documented expectations, not new verification
results; all cases remain NOT_RUN in this worktree.

The Cloud gate must inspect decoded MIR and the translated caller AST: both
calls in `shared_cleanup` must have the same cleanup ID, and the caller AST must
retain the actual unwind `goto` for the ordinary call. A whole-unit string
match is insufficient. Compilation, VeriFast, and proof execution are NOT_RUN.

`dead_code_pre.rs` is intentionally unregistered because the contradictory
precondition makes the whole function dead code. Run from this directory:

```text
verifast dead_code_pre.rs
```

Expected result: exit status 1 with a dead-code diagnostic spanning the whole
function. This is not a `req false` proof error. `mysh` does not express this
expected exit status, so the fixture remains unregistered. Do not add
`-allow_dead_code` or an assumption to make this case pass.
