# R10 bounded native P1 target rationale

## Defect and applicability

R9 S5 used nearly all of its 900 second runner window before package upload completed, so no delivered P1 or tuple-alpha result was available. The R10 full-matrix runner performs the expensive P0a/P0b/P0c proof lifecycle and then runs every synthetic mutation, dispatch/default/Freeze/false31/redirect route, legacy R1–R7 controls, OFF route, and 26-row admission before it returns. For the immediate R10 target, this unrelated work can consume the remaining shared deadline after the native P1 and tuple-alpha observations have become available.

The bounded path applies only to the exact R10 profile execution mode `native-p1-target`. It retains the existing tool reconstruction and focus/dead-code registration regression unchanged, and reuses the complete existing P0a/P0b/P0c lifecycle, including both body/conformance attestations, same-pair receipt, and caller observation. The existing legacy/OFF fixture constructors remain because the complete positive receipt requires their source/unit identities in its full 26-row expected-input manifest; only their verifier routes are omitted. It then runs P1 immediately, followed by the existing paired-MIR wrong-binding and region-role controls and only the `alpha_valid` synthetic translator invocation. P1 retains the R-only reference, same-Build source pair, paired normal/readonly support, compiler inventory, structural equality gate, and full-source interface checks. The alpha route retains the actual compiler-derived paired decoded input, isolated encoding/translator invocation, AST requirement, unchanged-tool/source/input hashes, and transport classifier.

## Preserved guarantees and controls

No source, proof, equality, native-interface, generic/lifetime, normal/unwind, focus, dead-code, or classifier predicate is weakened. The positive body lifecycle remains complete. Existing `N-binding` and `N-region-swap` observations are only reported after the same compiler-bound P1 normal/readonly baseline and their immutable prepared inputs validate. Alpha acceptance is a representation-only translator observation and never compiler, refinement, or proof credit. All 26 `CASE_ORDER` rows remain present; rows outside the explicitly executed target set retain `NOT_RUN` plus the bounded-scope reason. Any missing prerequisite, timeout, or exception remains `NOT_RUN` or `INCONCLUSIVE` with its original event/error context.

This path never records the matrix admission gate and always reports `matrix_complete`, `dispatch_ready`, `diagnostic_complete`, `verification_accepted`, `profile_accepted`, `accepted`, and proof credit as false. The normal full-matrix path remains the R10 default for profiles that select it.

## Report serialization applicability

R9's lossless observation-pointer serialization remains byte/behavior compatible for R9 and disabled for older phases. The same bounded transformation is enabled separately for exact R10 authorization only when the call-site phase and report root's `authorization_phase_id` match. It only replaces byte-for-byte JSON-equal non-null mapping observations, leaves missing/null/wrong-type/conflicting data inline, and keeps all top-level and non-matrix details unchanged.

## Differentiating synthetic controls

Isolated tests will exercise stage order, deadline/timeout outcomes, partial P0/P1 progress, missing/null/wrong-type prerequisites, original adapter exceptions, all-26 NOT_RUN preservation, and the invariant that the bounded path cannot create a matrix admission record. Report tests will check R10 pointer round trips and that R9 and older authorization phases preserve their established behavior. No local preparation, extraction, compiler, verifier, or Cloud execution is part of this change.
