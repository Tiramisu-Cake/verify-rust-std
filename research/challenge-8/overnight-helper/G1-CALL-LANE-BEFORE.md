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

O15 (`37714432761`, profile `63e2cf46`) supplied that capture. Both exports,
decodes and refinement pass with unchanged source. The callee graph SHA-256 is
`c493d14bf8a7bcbd3d3ab98655218798470a46042c5001572b50a3d4a3fff154`;
the caller graph SHA-256 is
`1f1f8e96cc210ea50d53744e6aa41cf73e5eff81ae5f10be777eb05d8a706504`
in both modes. The sole caller call is typed `FnDef checked_forget_generic<T>`
with `Move(_4)` and no projection, normal bb1 and Cleanup bb2. Bb2 contains
only `UnwindResume` and has no other predecessor. Full verification enters
and discharges the callee body, then the caller's normal return and leak
check; it exits 1 solely with `verified/lib.rs(17,1-29,2): dead code` at the
synthetic call unwind arm. This confirms the stated CFG mismatch without
assuming that an ordinary Rust call is generally non-unwinding.

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

The revised `verifast-g1-checked-forget-call-cfg-26.10.patch` is a new,
experimental trusted frontend component and is not part of O15/O16. Its
first name-only draft was rejected during review: an arbitrary same-name
callee with a real unwind could otherwise have been projected. The revised
rule is default-off and requires an explicit opt-in repository root. It pins
the std `ManuallyDrop` and `forget` source, the exact whole local source
including both bodies and contracts, the same-unit two-body order, both
generic/public/unsafe signatures, full local inventories, ordered statements,
all three basic blocks, a `Cleanup` edge and empty `UnwindResume` cleanup,
and the typed `FnDef checked_forget_generic<T>`/plain `Move(_4)` call. It
requires exactly one translated call. Its `fn_outcome_result` projects the
ordinary result only for this reviewed unit; the callee's false-unwind post
still must be proved in the same full-unit run before the caller can pass.
The source MIR cleanup block remains present, and all normal verifier unwind,
leak and dead-code checks stay enabled. This source/MIR gate is a trusted
correspondence component, not a theorem about all Rust calls.

The patch statically applies to the cumulative H2b/callback candidate but
has not been built or verified. A fresh positive must verify callee and
caller return/leak with no dead code; separate false normal post,
frame/thread loss and duplication controls must fail at their intended
obligations. Wrong callee and weakened callee unwind must be admission
failures. The hosted matrix currently records diagnostic negatives until
their exact proof locations are reviewed. A fixture with shared reachable
Cleanup must retain and verify that path before any generalization beyond
this exact three-block unit.

O18 (`37745138207`, `bb9c46bc`) ran the nine-variant matrix with both MIR
modes and refinement succeeding. Every proof stopped at the same admission
error, `callee/caller signature source span`, before either body began.
The exporter reports raw column zero for both signatures, while the
translator converts to one-based column one; the gate expected zero.
O18's two recorded admission-control labels therefore have the **wrong
cause** and all nine variants remain inconclusive. The corrected gate
expects one-based column one. The classifier now requires each control's
specific source refusal (`exact caller post or runtime body/source suffix`
for wrong callee, `exact checked callee and caller source prefix` for
weakened unwind), full frontend/refinement and source integrity, and zero
proof headers. A fresh hosted run is required for every proof claim.

O19 (`37746579002`, `a6f9d5e0`) crossed that gate. The positive verifies
the exact generic callee and framed caller in the same unit with full
verifier exit zero, both MIR modes, refinement, normal/unwind posts,
return/leak checks and no dead-code refusal. False post, frame and thread
loss/duplication controls fail at their intended obligations. Wrong callee
and weakened callee unwind now fail at their distinct exact source reasons.
The `wrong_value` proof also failed at its intended caller post, line 22,
with `Cannot prove flag == !(flag)`; its O19 classifier label remained
INCONCLUSIVE because it expected a heap-chunk error. The next hosted
classifier run will use that exact equality predicate and replay rejects
the O18 common setup failure. These results qualify the isolated G1 call
lane only after parent review; SAFE std `forget` remains unlinked.
