# Generic checked-forget call lane: exact no-unwind CFG candidate

O14b run `37713536492` proves the standalone public unsafe
`checked_forget_generic<T>(t:T)` body under current-thread pre, same-thread
normal post and false unwind. All NORMAL/readonly export/decode and
refinement stages pass; false post, lost/duplicated thread and contradictory
pre fail at their intended proof/dead-code obligations. This qualifies only
the local callee body. It does not qualify a caller or the actual SAFE std
`forget` call.

The next isolated fixture puts the same exact callee before a public generic
caller that invokes it with a separate initialized boolean frame. The full
callee, caller, normal/unwind posts and independent frame must verify in one
unit. Before any CFG rule, capture both complete NORMAL/readonly typed MIR
graphs and the first stock call-lane error. The expected historical symptom
is a synthetic `unwinding` switch arm reported as dead code because the
callee contract proves false unwind, even though Rust MIR retains a cleanup
successor. A different error reopens the hypothesis.

The proposed opt-in frontend rule is only for the exact caller DefPath and
the exact local generic FnDef/substitution and plain Move operand, after
pinning the whole checked callee source/contract and both full MIR graphs.
It emits `fn_outcome_result(checked_forget_generic::<T>(move t))` as a
normal-result call. The callee's false-unwind post excludes the fixpoint's
`unwinding` case. The emitted successor inventory has only the normal edge,
which matches the emitted AST, while the original MIR cleanup edge remains
in the source certificate and all cleanup blocks with another predecessor
remain reachable. The rule is off for other calls and never disables
unwind/dead-code checks. Full-unit proof must discharge the callee and caller
return/leak paths, with normal and false-unwind contracts, before this
component can be accepted.

This isolated call lane is a prerequisite to a separate actual-helper
redirect. It has no nominal guard, no permission to an `Element` pointee,
and makes no claim about SAFE std `forget` correspondence. The latter needs
the exact actual source/typed-call/drop-flag/shared-cleanup certificate and
the truthful caller-side guard ownership split in
`ACTUAL-FORGET-LINK-BEFORE.md`.
