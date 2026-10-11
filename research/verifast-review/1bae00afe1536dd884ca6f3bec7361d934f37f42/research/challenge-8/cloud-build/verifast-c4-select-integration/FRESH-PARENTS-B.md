# Fresh parent proof B

Cloud Build `2669cf81-f8e4-4607-add3-09ce6743ac6a`, exact infra/proof
`95b215b951b459a0ac2406aaf8d290bfc0878517`, effective tool `423d5e3cb1781ed58f8933146a555470f7b42115`, profile r3.
Create 20:00:52.464967156Z; finish 20:06:28.638930Z; charged 337 seconds.
Archive SHA256 `bd8258e45ae57dccc9fafbc01935e245ffd7b4d09646fc48dc580c76630100de`; coordinator download integrity verified.

Actual pointer selector PASS: all seven helper bodies, nested DropOnPanic body,
then outer selector, normal/unwind returns and leak checks; no proof errors or
dead code. Source, both decoded MIR units and ten pre-AST fingerprints match.
No GUARD/GUARD_TEMPLATE/A1_LINK opt-ins were inherited. Final producer AST
SHA256 `a567807354602a49f2445f083b4c62a849cb385b915f9a6e6fd99932473e878e`.
Selector raw proof log SHA256 `c3f41dd7de973d4c57fa09ed63339c4d56dc615eb6f3c803fbe76709d4cba9a6`.

Bounded C1→C4 PASS with original normal/unwind posts, five required helper
bodies, strict lifetime cut enabled and exact original pre-AST. Raw proof log
SHA256 `864c0f2b0d27f30a3b66252bad8138a51414afc1065963092f3e644c166a24da`.

Composition REFUSED before proof: `SORT4-C4-BOUND: local declaration $_171`.
Fresh source-derived AST declares first operand temporary as Bool, unlike the
candidate's pointer expectation. This is an admission mismatch, not a semantic
negative. Composition log SHA256 `473cf2929f9210cce64b69f5c9d760ab22e49a614346049ac9ca1583ce348965`.
New resource/admission/cleanup/outer-bound gates were deliberately deferred.
Two parent PASS results do not establish composition readiness.
