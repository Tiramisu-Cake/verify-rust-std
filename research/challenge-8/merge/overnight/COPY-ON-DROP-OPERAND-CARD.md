# CopyOnDrop AST operand admission card

## Problem and exact rule

The fresh positive and first-body-false artifacts both pass structured readonly
MIR admission. The false case reaches its exact `assert false` inside the
actual `CopyOnDrop::drop` body, but the old AST gate assumed that VeriFast's
synthetic argument locals retain the positive case's names. Inserting the
assertion changes those names while preserving the same three reads from
`self.src`, `self.dst`, and `self.len`. The old log matcher also treated a
diagnostic-context `note: Verifying function ...` line as a second function
header.

The classifier now recognizes only timestamped verifier function-header
records and requires exactly one actual `Drop::drop` body segment. Within the
runtime `Ast.Func` (the pinned 13-field node's runtime body, field 10), the
single `std::ptr::copy_nonoverlapping` call must take three variable
expressions. Each variable must be defined by its unique ordered reaching
assignment from the corresponding physical `self.src`, `self.dst`, and
`self.len` field. Those definitions must be the three immediately preceding
AST statements before the call, at the call's source line; there may be no
intervening write, duplicate/ambiguous definition, unsupported projection, or
coercion in the admitted path. The ordered field origins must be `[0, 1, 2]`
and match same-source readonly structured MIR's field-origin proof, including that the
third operand is dynamically read from `self.len`. Local variable names are
not compared across MIR and proof AST.

The AST gate still requires one declaration and one runtime body, matching
source bounds, one copy call to the exact callee, the `returning` and
`unwinding` switch branches, and the normal return node. It does not accept a
read-only prototype proof as the runtime body.

## Trusted inputs and scope

Inputs remain the pinned original SmallSort source, extracted `CopyOnDrop`
source, same-source readonly MIR decode, actual normal proof AST and refinement, pinned AST
printer output, and the existing profile-pinned VeriFast command. The checker
only parses those recorded artifacts; it adds no verifier, parser, kernel,
prelude, or source semantics. It introduces no ownership conversion or
caller-frame claim.

The positive gate is unchanged: exact exporter/decode/VeriFast/refinement
success, source integrity, admitted MIR and runtime AST, one actual target
body, copy execution, normal return, leak check, and no error or dead code.
The matched false control still requires valid exporter/decode/refinement,
VeriFast exit 1, unchanged source and admitted MIR/AST, entry into the actual
target body, exactly one global/body assertion error at the predeclared
`verified/lib.rs:85` columns 20–25 with predicate `Cannot prove false`, and no
dead code. Since the deliberate first statement fails before the copy, the
negative does not require copy execution, return, or leak check. A setup,
source, MIR, AST, stage, body-entry, or location mismatch is inconclusive.

This is a localized classifier repair for the direct generic `CopyOnDrop`
component. It does not prove caller cleanup, callback framing, a slice
ownership bridge, or the complete sorting routine. Fresh hosted evidence is
required before either positive or negative status is credited.

The standalone MIR capture uses the official exporter preprocess-readonly
mode. Its local numbering is never claimed to be the actual normal frontend
MIR numbering. Source identity and the independently decoded runtime proof
AST's physical field reads/call operands establish the connection; no new
normal-message certificate is asserted by this Drop gate.

Both gates additionally refuse dead-code records anywhere in the saved VF
log, including outside the target-body segment. The matched first false
requires zero target copy executions/returns/leak records after its failure;
these zeros identify this diagnostic and do not remove target positive posts.
