# R23 fractional ghost cleanup successor candidate

Status: **design only / unverified**. The S3 positive trace reaches the normal
return and leak check, then the terminal log reports dead code at the outer
function span and twice at source position `235:5-6`. Exact cause is still
unknown; this candidate addresses one localized translator inconsistency.

## Defect hypothesis and applicability

In `translate_fn_call`, an admitted `VeriFast_ghost_command` call is replaced
with its checked source ghost statement (or `Noop` for the callback marker).
The generated statement has no runtime call or unwind arm, but the ordinary
`FnCallOutcome` path can leave the call's MIR cleanup successor in the
translated CFG predecessor inventory. In the exact R23 nine-body profile,
seven of the ten `select_unpredictable` cleanup predecessors are such synthetic
ghost commands. Keeping an unwind successor for an erased ghost call can make
the translated CFG disagree with the emitted AST. This is a hypothesis, not a
claim that it caused S3's dead-code report.

The proposed change applies only while the already-admitted fractional R23
profile is active and only in the existing branch that replaces the builtin
ghost command with its source annotation or callback-marker `Noop`. It returns
the normal successor list only. It does not alter the builtin ghost command,
the source annotation, any assertion, or any real call.

## Invariants

- The raw, decoded MIR body and all source, unit, body, and block hashes remain
  unchanged. The ten raw cleanup edges to `bb28` remain part of admission.
- The seven ghost commands still emit their exact ordered source ghost
  statements; callback markers remain `Noop` and continue to inject the
  existing checked callback recovery path.
- Every ghost call keeps its normal successor.
- Real pointer-drop, `forget`, and `assume_init` calls keep their original
  unwind successors and existing normal/unwind checks.
- Other profiles and generic/default translation remain byte-identical.
- No checker dead-code behavior, ownership gate, summary, runtime behavior, or
  verification option changes.

## Static controls

A focused synthetic source test must distinguish: the seven R23 ghost calls
lose only their translated cleanup successors; their normal successors and
ghost statements remain; the three real cleanup calls retain their unwind
successors; raw inventory stays 10-to-`bb28`; a ghost call without a cleanup
edge is unchanged; and non-R23/default paths preserve the original successor
list. These are translation-shape controls only, not typed MIR, compiler,
exporter, decoder, verifier, or dead-code acceptance evidence.

Cloud confirmation in a later authorized window is required before claiming
the dead-code blocker is resolved.
