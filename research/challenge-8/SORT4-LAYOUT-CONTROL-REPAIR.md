# Wrong-source-span control repair card

## Hypothesis and scope

The prior wrong-span mutant changed `bindingDefSpan.hi.line` from 7 to 8 while
leaving `hi.col=13`. In `verified/lib.rs`, line 8 is blank, so the mutation does
not describe a source coordinate even though it remains ordered. A metadata
rejection from that payload does not establish that a distinct valid source span
is bound to the right ADT.

For `metadata_control_body`, change only the endpoint column from the actual
declaration end `(line=7, col=13)` to `(line=7, col=12)`. This yields the valid
ordered prefix span `(line=7,col=0)..(line=7,col=12)` within `pub struct Z;`.
Keep the source path, file identity, line numbers, all other span fields, layout
values, target, pointer width, and separate `defSpan` unchanged. The falsifiable
hypothesis is that the payload still decodes and encodes, then the verifier
rejects it specifically at the existing `RustLayoutMetadata: binding mismatch`
for the definition-span comparison.

## Exact domain and acceptance

Use only the existing `metadata_control_body` source and unchanged experimental
fieldless-layout profile: VeriFast source `809de4596839b739dd999f9e462242c835e3af46`,
nightly `2026-02-05`, `x86_64-unknown-linux-gnu`, immutable patch SHA-256
`d4a12525bcdbdaa4deb82058d6cc0037c8c09fa508ad2eeb14386b2753693a14`.
No source/runtime, generic-signature, schema, tool, specification, or semantic
change is in scope.

The mutant passes only if both complete endpoint coordinates resolve to valid
positions in the exact selected `verified/lib.rs`, the range is ordered and
nonempty, its file/source identity matches the original binding, its complete
nested payload differs from `defSpan` only in the intended end column, mutation
binary decode/encode succeeds, sources/refinement remain unchanged, and VeriFast
fails with exactly the named binding-mismatch diagnostic. Missing, truncated,
duplicate, or ambiguous coordinate fields fail closed; they cannot select the
first matching nested field or count as the intended negative.

The unchanged full acceptance matrix must retain every previous result, including
all 18 layout cases, seven metadata controls, ten native controls, and all
classifier/span checks. A positive response to the valid-span mutant or any
wrong-stage failure is INCONCLUSIVE and stops this repair branch. The next action
after implementation is one exact-SHA GitHub-hosted full-matrix run; no local
execution, commit, push, or dispatch is part of this repair task.

## Budget

This repair uses the fresh composition/constructor phase budget, not a historical
night budget. Maximum total hosted time is 5,400 seconds, each job at most 1,800
seconds, one relevant job at a time. Root owns the hosted full-matrix dispatch and
evidence closeout.
