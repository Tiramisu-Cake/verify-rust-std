# Native C1 declaration scope and free paths — DRAFT static review

This review is read-only evidence for [BINDING-CARD.md](BINDING-CARD.md),
not approval of a transformed AST or a proof result. Pinned kernel
`/root/verifast-select-sort4-c4-bind-20261010/src/verifast.ml` has SHA-256
`37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`.
The capture-only native pre-AST has SHA-256
`18973de5dd5ff1a9c94652fd808d42ffe2297096adb8a3cc1980f74a554ccea5`.
Independent MIR review reports `_5` StorageLive in bb0, StorageDead in bb1,
no later use; callback `_55.._62` occur only in bb43–45 and the actual call's
normal/unwind continuation. This report still needs the pinned full MIR graph
as a machine-checked admission certificate; the AST capture alone does not
record StorageDead.

## Pinned kernel behavior

`verifast.ml:988–1127` treats ordinary non-address-taken locals as symbolic
values. A `DeclStmt` produces a heap object for an address-taken local, static
array, union, or qualifying struct; address-taken scalar/reference locals get
a points-to chunk. `src/verify_expr.ml:1500–1525` assigns each declaration's
`blockPtr` and marks address-taken locals while traversing its actual block.
`verifast.ml:180–201` consumes listed local objects on block exit. The exact
`locals_to_free` list is populated by the verifier's traversal; the empty
`ref []` printed by a pre-verification AST capture is not a free-path result.

`verifast.ml:2522–2906` wraps a block's fallthrough, `ReturnStmt`, and outgoing
label continuations. Each route runs `free_locals`; a strict lifetime child
also freezes outer types/bounds, rejects lifetime-scoped heap chunks and
escaped local types, and filters inner variables from the outgoing environment.
`GotoStmt` at `verifast.ml:2922–2928` invokes its target continuation, so a
goto to a label outside the `'cmp` block goes through that block's outgoing
wrapper. `ReturnStmt` at `verifast.ml:1985` and `2999–3057` evaluates the
return value before invoking the wrapped return continuation. A direct
callback unwind must therefore be routed to an epilogue **outside** the strict
child after source debt closure; otherwise the strict exit may correctly
reject live `'cmp` debt. The epilogue executes source recovery and full native
tail/MU/F/thread/type rejoin before the original `unwinding()` return.

## Proposed path certificate for this exact AST

The `_5: &'erased [T]` declaration is root index 2; it is assigned and used
at root 77–78 for `v.len()`. It is not a callback local and cannot be tied to
`'cmp`. The implemented bound patch leaves `_5` at its original outer scope.
Fresh callback-free preparation passed strict entry with `_5` unchanged, so
there is no observed reason to shorten its lifetime. MIR reports StorageDead
at bb1 before the size-of call; that remains a recorded source fact, not a
new translated lifetime cut. Any later `_5`-specific failure needs separate
review.

Callback `_55.._62` are root declaration indices 52–59. Move all eight into
the single `'cmp` child; this includes raw `_59/_60` as well as six
reference-bearing locals, preserving their exact types, declaration order and
initializations. The source uses each only after the marker, in child 22–31.
The normal route executes call, debt close at child 32, checked cut at 33,
then exits to root normal cleanup at 114–126. The direct unwind route executes
the marker debt block, exits by a unique goto to an external epilogue, then
executes pair recovery, four-cell join and the fourth full-native rejoin block
before returning `unwinding()`. Both exits must cross the child wrapper once;
no goto may target a location inside the child from outside or bypass its
cleanup. The callback's direct unwind cannot enter later comparisons.

The captured declarations show `ref (false)` address-taken flags, and neither
`AddressOf(Deref Var)` in the callback expression nor tuple-field assignment
directly marks those local variables address-taken under
`verify_expr.ml:1390–1490`. This predicts no local stack points-to chunks for
these moved scalars/references. It does **not** dispose of reference-own,
borrow, or lifetime resources created by `create_ref` and `reborrow_ref`;
those must be consumed by the actual call/debt protocol and verified on both
outcomes. Admission must assert the original flags and check the post-rewrite
flags/list after `stmts_mark_addr_taken`; if any differs, the transformation
refuses before proof. Full normal/direct-unwind posts, return, free and leak
checks remain the decisive dynamic gate.

This is a bounded relocation certificate proposal. It neither proves the
prepared resources nor authorizes dropping a local, synthetic StorageDead,
borrow chunk, strict cut or automatic native post. A missing graph edge or
failed free/escape check is an exact blocker, not a reason to relax the kernel.
