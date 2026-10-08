# Exact actual `forget(guard)` to checked generic callee: proposed overlay

This is an unimplemented semantic component. Its prerequisite is a fresh
hosted full proof of public `checked_forget_generic<T>(t: T)` with the exact
new-std body `let _ = ManuallyDrop::new(t);`, precondition current thread,
normal post same thread, and false unwind. The separately executed framed
direct-body G1 cases do not qualify a callable callee. O13 G1c mostly failed
in its fixture marker generator before proof; a repaired O14 run is pending.

The actual source call stays `crate::mem::forget(guard)` and the private
function-local guard stays in place. The candidate redirect is limited to
that one `std::mem::forget` typed FnDef with substitution
`select_unpredictable::DropOnPanic<*const Element>` in the source-certified
specialized actual helper. The argument must be the plain `Move` of the exact
guard temporary, with no projection/Copy, and the preceding MIR statements
must clear the guard drop flag before that move. The local callee receives
the inferred nominal type parameter; it need not name the function-local
Rust type in source. Pin full 26.10 `hint.rs`, `mem/mod.rs`,
`manually_drop.rs`, the local callee body/contract, both complete typed MIR
graphs, exact source spans, the ordered outer ghost inventory, all locals,
normal target, unwind target, drop-flag switch and shared cleanup
predecessors. A same-unit full verifier pass must enter and discharge the
callee's return/leak paths before its summary counts. The trusted step is
the correspondence between SAFE std forget's pinned ManuallyDrop move and
the checked source-equivalent unsafe callee under a weaker, thread-only
interface. It does not change the stock generic SAFE specification.

The O12 projected actual MIR supplies a concrete starting inventory, not
an admission for this new ghost layout: its forget block assigns the guard
drop flag `_35 = false`, then `_30 = Move(_22)`, then calls typed
`std::mem::forget` with normal target bb13 and unwind cleanup bb18. The
same bb18 has predecessors from other calls. The new ghost blocks will
renumber locals/blocks, so the new gate must derive and check their fresh
canonical identities rather than reuse these numbers by assertion.

The stock translator emits a `FnCallOutcome` switch for a call result and
adds the MIR cleanup successor to its target inventory. For a callee with
proved `on_unwind_ens false`, the switch's `unwinding` arm is unreachable
and VeriFast's mandatory dead-code check reports it (observed in the older
G1 call lane). The exact-call candidate may instead emit
`fn_outcome_result(checked_forget_generic::<Guard>(move guard))` as a
`FnCallResult`, with only the normal successor in the **emitted AST** target
inventory. This is justified only after certifying that callee's false
unwind and the actual call's source/MIR identity; the fixer is off for all
other calls. `fn_outcome_result` is a total stock fixpoint, and the callee
post excludes its `unwinding` case, so the normal extraction cannot hide a
reachable panic. The original MIR unwind edge remains in the source
certificate and the shared cleanup block remains reachable through its
other predecessors. No global pruning or disabled dead-code/unwind check.

In the caller, opening truthful nominal guard ownership immediately before
the call yields exactly one selected initialized slot cell, which remains a
frame across the thread-only callee. The empty raw-pointer value predicate
may be opened to `true`; it grants no `Element` pointee right. The selected
wrapper closes after the call, while the unselected wrapper was already
closed after its checked non-unwinding pointer drop. The actual nested
generic Drop body is proved separately for normal and unwind; the outer
helper cannot count a vacuous/default owner or an unproved destructor.

Admission controls must reject wrong/std callee body, weakened local post,
different nominal type/Element, Copy or projected operand, wrong drop flag,
extra operation between owner open and move, altered normal/unwind target,
removed shared cleanup predecessor, missing or duplicated selected cell,
wrong pointer value, lost thread, false post, source drift, and missing
callee proof. Source/admission failures are not proof negatives. Positive
status requires NORMAL/readonly export/decode, refinement, complete full
verifier return/leak/dead-code checks, and explicit normal/unwind contract
classification under the exact combined patch profile.
