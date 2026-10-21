# R12 S4 independent integration review

**Current decision: GO for the S4 registration delta, subject to the normal exact published-closure and profile-pin checks before execution.** The initial review found a matrix-shape mismatch; the current implementation fixes that path and the focused end-to-end classifier tests now exercise the actual paired-owner representation.

## Finding

The original blocker was that `a1-runner.py` emitted `caller_calls.dispatch_pair`, while the matrix classifier expected legacy `caller_calls.ast`. The current `a1-matrix-classifier.py` P-dispatch branch consumes both paired owners, requires each source-bound MIR binding and AST call structure, checks the exact three unique owner/callee rows, and compares every trace AST string and MIR span string against the corresponding independently generated AST/MIR record. The matrix test now constructs that same `dispatch_pair` shape and requires it for the positive result. The blocker is resolved.

The matrix predicates retain `proof_credit: false`, require the trace source digest to match the verified source pair, require both owners and the exact expected call lists, and reject missing, duplicate, wrong-owner, or wrong-source trace rows. The runner's trace classifier independently rejects missing/malformed/wrong AST or MIR span values and does not use count-only fallback.

## Reviewed soundness points

- The trace classifier requires exactly three tagged records and exact owner/callee membership, compares original and translated common items, rejects redirection, and joins each row to both MIR and AST call spans. Missing, duplicate, unknown, malformed, or mismatched entries remain inconclusive. `python -m unittest test_a1_dispatch_trace_join -v` passed 4/4 focused tests.
- The MIR column adjustment is supported by the exact pinned tool source (`f76012fb518703b1d98e243ac4f487f16877cfcb`): the Rust MIR exporter stores `rustc_span::CharPos.0` unchanged (`vf_mir_exporter/src/lib.rs`, `encode_char_pos`), and the translator explicitly adds one to make the position 1-based (`vf_mir_translator.ml`, `translate_char_pos`). Thus `_mir_call_span` adding one before comparison to AST locations is consistent with the pinned AST coordinate convention.
- AST and MIR spans are allowed to differ. Pinned translator code takes `call_loc` separately from `FnCallData.callSpan` (`translate_fn_call`, around lines 3845–3857); `translate_fn_call_rexpr` uses `call_loc` for `Ast.CallExpr` and `fn_loc` for the MIR call location. The trace now binds each logged field to its own exact AST/MIR source span and checks both low lines against the source-derived call line. The synthetic positive uses different AST/MIR ranges; wrong-span mutations fail.
- The runner uses separate normal and readonly MIR views, and the source pair remains checked against the generated-source identity before the pair bindings are collected. The dispatch observation and trace carry `proof_credit: false`; this is structural dispatch evidence only.

Verification: `python -m unittest test_a1_dispatch_trace_join test_a1_matrix_classifier -v` passed 25 tests. The refreshed profile's runner, AST gate, MIR call binder, matrix classifier, and C patch SHA-256 pins match the current files. This review did not run a compiler, verifier, Cloud Build, or full runner; no proof acceptance is claimed.
