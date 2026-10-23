# R24 positive-only AST diagnostic

Defect: the R23 positive proof call reaches the outer return and leak-check,
then reports the same three dead-code sites. Translator 103a34 did not change
that outcome, and the emitted AST has not yet been bound to those diagnostics.

Applicability: one additive diagnostic call immediately before the unchanged
positive proof call, only when the runner explicitly enables
--positive-ast-inventory and both the existing R21 callee route/provider
checks and exact R24 session phase are present. Negative variants and default
R20/R21/R23 behavior do not run this call.

Invariants: verifier source, translator, proof/model/checker/gates, preflight
pins, and all seven controls remain unchanged. The diagnostic uses the same
actual stage setup and both enabled gates, with only
-dump_ast_with_locs r24-positive.ast.ml added to the verifier argv. It is
separately named r24-positive-ast, has no proof credit, and cannot change the
ordinary proof stage result or exit behavior. Capture and restore all
diagnostic environment values exactly. Validate the physical source pair and
the ten already-produced unit/body snapshots against current positive pins
before and after the diagnostic.

Controls: isolated helper tests cover exact route/provider/variant admission,
argv and gates, default-off and negative skip behavior, successful and
nonzero verifier exits, stage errors and malformed/partial/missing outputs,
source and snapshot drift, symlink/path refusal, environment restoration, and
source-stage-target binding. Diagnostic exceptions are recorded with observed
source/snapshot state and re-raised unchanged. Missing or invalid evidence is
marked incomplete with proof credit zero. No Cloud or local proof tool runs.
