# R11 checked-helper verifier stage

## Decision

The bounded tool-side design is a separate experimental `checked-helper`
stage in `checked-threshold-contract.patch`. It exists only to prove the
source-bound `a1_cleanup_option_ref` lemma before the caller-focused stage may
consume that lemma's contract. The stage does not create or publish a caller
summary, and its successful process exit alone is not a caller receipt.

The stage retains the existing checked-contract opt-in, exact Cloud phase,
native unwind settings, complete specless inventory, reference-creation
settings, actual two-impl/method inventory, and verifier focus mechanism. It
accepts only the helper name `a1_cleanup_option_ref`; checks the independently
computed SHA256 of `verified/lib.rs`; requires the requested focus to be the
certified helper body start; and validates the supplied source/body line
bounds, ghost delimiters, exact lemma declaration, closing brace, and unique
declaration. It rejects any forced-legacy-redirect control. The full helper
block hash is checked by the paired backend against its source certificate and
profile pin. The caller stage still selects only the actual compiler MIR
observer body and keeps its existing publication checks.

## Trust and applicability boundary

This adds no axiom, assumption, external function, permission leak, `forget`,
or runtime helper. It changes only a verifier command mode and exact focus
admission; the proof body remains checked by VeriFast. The helper-only mode
must run before caller verification on the same exact build/source/tool/profile
pair. Its result must be a checked helper-stage PASS consumed by the paired
backend gate, with no summary emitted or consumed during this stage. A failed,
missing, malformed, stale, or mismatched helper result must fail closed.

An exact source-only replay applied the O26 20-patch chain and its two pinned
refresh patches to raw tool HEAD `f76012fb518703b1d98e243ac4f487f16877cfcb`,
then replayed the A1 strict, C4, native C1/C4, slice, threshold, selected
branch, required-item, and native-signature patches. It reached the pinned
pre-C translator SHA256
`f9d1097efa321b7c6496810990aae1f09584eb13da3a494d1c56641776c19f4d`.
The revised C patch applied there to translator SHA256
`9f065ebe4937cc08383ccd8791e956558202a5ab7a045f0bef74d229234a4a71`, and
reverse-check/reverse/reapply returned the same pair. This establishes exact
patch applicability and byte reproducibility, not OCaml compilation or
VeriFast acceptance. No local compiler, verifier, source extractor, preparer,
or Cloud Build was run. The separate helper stage is experimental and requires
independent review before Cloud dispatch.

## Controls

`test_a1_checked_helper_tool_patch.py` checks unified-patch parseability, the
closed helper identity/name and source/focus bindings, no publication from the
helper stage, unchanged caller-body focus restrictions, and retention of
existing unwind, inventory, and profile controls. The sibling backend
synthetic controls cover the exact block certificate, AST lemma kind/span,
same-build handoff, and rejected/missing paths. These static tests do not
establish the OCaml patch compiles or that verifier focus accepts the lemma.
