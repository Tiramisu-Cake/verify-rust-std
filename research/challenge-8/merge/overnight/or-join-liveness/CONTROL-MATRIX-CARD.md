# Complete OR shape-control matrix: prepared diagnostic extension

Problem: the first driver covers only edge kind34 and target34. Passing those
cannot establish the full exact source/MIR/AST matcher. This extension changes
only deliberate inputs in the separate diagnostic tool copy. Production source,
exporter, six/seven translator/kernel and all target posts remain unchanged.
No result here is a theorem or full profile acceptance.

Rule: start from a fresh exact admitted prepared source and its official normal
MIR, require the unchanged lossless roundtrip/AST positive, then apply one named
mutation to its parsed semantic tree. Re-encode and decode with the pinned schema
and require full-tree equality with the expected single mutation. Reject wrong
source, missing/duplicate original block/field, wrong original value, unexpected
extra mutation or failed export/encode/decode. The b34 tree supplies a field-map
hypothesis only; its old source/MIR is never a new positive input.

Required controls (each independent, not accumulated):

* storage-live-34 and storage-live-36: replace first StorageDead kind with
  StorageLive, retaining local/count.
* goto-38-34 and goto-38-36: change pure-entry target37 to existing38.
* statement-count-34 and statement-count-36: remove exactly second StorageDead.
* real-statement-34: append a copy of the already-typed Boolean comparison
  assignment from33, preserving its record/operands; this inserts a translated
  operation rather than a StorageLive/Dead-only control.
* predecessor-32: change the existing block32 Goto33 to37, adding one edge to
  the panic block. Block32 is the end of the odd-tail arm immediately before
  the admitted guard.
* comparison-eq-33 and comparison-eq-35: change final ne operator to eq,
  keeping operands/result type.
* branch-order-33 and branch-order-35: swap exactly the original false/true
  target pair [35,34] or [38,36].
* span-column-34 and span-column-36: decrease pure-entry Goto source-span
  low-column position50 to49; keep file/line/high endpoint.
* panic-callee: change only FnDef's diagnostic name to std::process::abort.
  Callee/type translation compatibility is UNTESTED; an unrelated unsupported
  operation is INCONCLUSIVE, never the desired matcher refusal.
* panic-unwind: change block37 unwind kind continue to unreachable; other
  call fields/target/source stay unchanged. Translation support is untested.

Expected stage: verifier exit1, unique exact MIR-OR-JOIN-LIVENESS matcher error
at admitted actual function signature, no target body execution, no unrelated
error. Source-hash control is separate: mutate one harmless comment byte in a
copied source and require admit-source.py's exact admitted-source-hash refusal
before export. It is source admission, not MIR/refinement or proof-negative.

Trust assumptions remain the pinned official exporter, Capnp schema/encoder and
full-consumption parsed-tree certificate. No mutated message may feed the actual
production proof or refiner; the unchanged source pair still uses the official
refiner in every diagnostic mode. Production home/source inventories must match
before/after. A partial budget/unsupported/missing-AST run yields unaccepted
partial evidence. A complete matrix needs every corresponding unique refusal,
roundtrip positive, source gate and the same-source six/ seven coverage and
full-positive evidence. Existing kernel/cleanup closure remains a separate open
trust obligation even if all these frontend controls pass.

## Next Cloud gate after fde74800

The fde run certified both initial mutant messages and obtained both exact
frontend refusals. The roundtrip was lossless and its actual target AST existed,
but the driver misclassified it because the next-function search matched its
own indented header. The next source starts that search after the matched
header, expands to all17 independent modes, and fixes the text-slice helper
return arity for new mutation guards. These are diagnostic bookkeeping changes;
no production semantic rule or source changes. The driver work cap is240s
for all17 official refinement/manual-export/frontend-export checks, with exact
per-mode results and INCONCLUSIVE on exhaustion. Source hash refusal remains a
separate gate before export. No new input is called checked until fresh Cloud
evidence.

Fresh target AST positive uses a10s verifier cap; it credits only frontend
admission and cannot credit target proof completion. The corresponding full
positive is separately run with the original full posts.

## RESOURCE10 predecessor-anchor correction

The 9ad825fa control attempt refused in its own normal-MIR setup guard before
any Capnp mutation or frontend call: in that current target body, block28 is a
`VeriFast_ghost_command` call, not a Goto. Block24 is another Goto33 on a
different control arm. The selected mutation anchor is block32, whose frozen
normal MIR terminator is Goto33 at the end of the odd-tail arm immediately
before block33's guard. The exporter and driver must bind that exact block id,
field shape, and original target33; the expected-tree certificate still allows
only the one block32 target change to37. This corrects diagnostic bookkeeping
only. It changes no production source, MIR exporter, verifier, or theorem.

## RESOURCE10 panic-callee field-path correction

The ad653ca9 control capture passed the normal-exporter hash and decoded the
exact admitted normal MIR, but every manual mutation refused before applying a
change. The decoded declaration records contain `ty` for the Boolean
comparison locals. The refusal was in the separate panic-callee check: the
decoded field nesting is `func.constant.const.val.ty.kind.fnDef`, so looking
for `ty` directly below `const` stopped at a nonexistent field. Bind that
observed `val` layer both when checking the original panic callee and when
building the expected one-field callee-name mutation. This retains the exact
field/key/type/callee checks and full-tree mutation certificate. The ad653
attempt contributes no mutation/refusal classifications; fresh Cloud evidence
is required.
