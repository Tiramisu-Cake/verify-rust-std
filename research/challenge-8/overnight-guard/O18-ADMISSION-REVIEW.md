# O18 H2b source and typed-MIR admission audit

O18 proof `bb9c46bc423a43cccf0e93a0ad7651c3faee6f1b`, hosted run
`37745138207`, applied H2a, H2b and the separate H2c source-gate
tightening. Evidence reviewed under
`/tmp/overnight-o18-evidence/overnight-s6/{h2b-source-admission,h2b-mir-admission,nominal-guard-template,generic-pointer-drop}`.
O18 workflow exit was nonzero because a separate actual-owner-linked
fixture preparation failed. All H2b admission stages completed and their
individual artifact files are present. This review does not relabel the
workflow as a whole or claim the actual nested Drop DefPath.

The H2b source-admission positive completed paired NORMAL/readonly
export/decode and refinement, passed the exact local source/MIR gate, and
verified with exit 0. Its checked generic method and local guard Drop each
have two normal/unwind return/leak pairs; owner constructor, concrete
`u32` witness and same-unit `OrdinaryDrop` return/leak. Seven source/ADT
mutants all completed paired export/decode/refinement and received verifier
exit 2, no proof entry and one exact H2 certificate fatal. `repr(packed)`,
`repr(C)`, `repr(align(16))` and the type alias before the ADT reject at the
new H2c `local guard unreviewed pre-ADT source` boundary. Extra field,
extra ghost command and casted guard call reject at `local guard exact
source/ghost owner`. No source mutant was counted as a typed-MIR control.

The MIR matrix independently reverified the unwrapped positive with full
exit 0, both method and guard normal/unwind return/leak pairs and ordinary
Drop return/leak. All twelve direct mutation cases use the same source
bytes. Their independent real-exporter NORMAL/readonly capture, decode and
refinement passed; each recorded one exact reproducible changed field in
the unique guard typed-MIR body, distinct canonical/mutated binaries,
matching source/exporter/console/wrapper hashes, and `mutant_exact=true`.
Each shadow-verifier run exited 2 with one exact certificate fatal, no
proof entry or ordinary verifier error. Reasons matched the intended
boundary for receiver, callee, type substitution, move/copy, argument
local/projection, destination, normal edge, unwind edge, cleanup flag,
extra statement and ghost inventory. These mutants are a *test-tool*
profile, not positive proof runs.

The ordinary O18 H2b eight-case resource matrix retained its positive
full proof. Its four source controls reject before proof, missing cell and
wrong target fail at the owner close (`verified/lib.rs:28`), and duplicate
returned cell fails at its extra constructor post (`verified/lib.rs:37`).
The six-case generic callee matrix retained a full positive and exact
missing-owner, false-normal, false-unwind, initialized-retention and
owner-retention negatives. The future-run `retains_initialized` classifier
now records the verified caller post's optional-versus-initialized
auto-close failure at `prelude_core.rsspec:213`; the historical O17 label
is unchanged.

The admission evidence is strong for the **local source-shaped H2b unit**
and the H2c attribute-source boundary. It is not an actual nested std
Drop proof. A direct adversarial generated-post test (initialized cell,
generic owner, second cell, false normal/unwind) remains a separate
test-only profile under design; O18 caller probes do not substitute for
that AST-post test. No `Element` right appears in generic H2b, so the
actual helper's no-extra-Element obligation remains separate. No harness
repair was needed for the H2b O18 matrices.
