# Final normal-MIR to proof-AST linkage gate

`stack-proof-ast-admission.py` is a separate hosted-only read-only gate. It
accepts the final `stack-roles.json`, the exact verified source, and VeriFast's
fresh `proof-ast.ml` from the same GitHub run. It checks the owned branch/run,
source SHA and role certificate before parsing the entire OCaml constructor
dump with a restricted, full-consumption grammar. It does not evaluate OCaml.
Unknown tokens, duplicate/ambiguous roles and unsupported target shapes fail.
The output is exclusively created and records both input hashes.

Within the unique actual `bidirectional_merge` function, the gate requires:

- One hidden declaration per certified raw local, with the expected Range or
  three-pointer tuple structure and the normal-MIR declaration source span.
- Unique `Range::into_iter`, `merge_up` and `merge_down` call switches at the
  certified source spans, each retaining a normal result assignment and an
  explicit unwind return. The range input and result bind to the certified
  hidden locals; the range input is built from start `0` and `len_div_2`, and
  the range result moves into `iter`. The two merge calls retain their exact
  four argument paths from the three named cursors and `is_less`.
- Exactly three tuple result field extractions per merge call, with local-copy
  paths to the intended named cursors. In VeriFast's actual AST the upward
  destination cursor is `dst_1`, corresponding to Rust source `dst`.
- One loop-body invariant on the line after the range header containing all
  fourteen hidden `AddressOf(Var("$_N"))` nodes and no hidden address elsewhere.
  Any extra address of an unknown hidden numeric local is rejected, even if
  the four certified roles still have their expected occurrences.
  Each Range has padding/start/end; each tuple has padding/0/1/2. The fields
  retain the observed regular versus maybe-uninitialized points-to mode, and
  padding predicates target the matching struct. No unresolved marker call
  may remain anywhere in the proof AST.

The normal-MIR role certificate remains the source of truth for IDs, raw types,
VDI exclusion and raw call/field dataflow. In particular, the raw MIR checks
the tuple pointer mutability as `*const T, *const T, *mut T`; VeriFast's
`PtrTypeExpr` dump does not distinguish const from mut, so this AST gate cannot
independently recheck that distinction. It checks that the translated AST
exhibits those same role destinations and locations. It does not establish permission ownership,
soundness of the translator, loop correctness, actual-callee contracts, leak
freedom, dead-code freedom or refinement. Those existing gates remain required.
In-memory negative controls mutate a hidden address, hidden declaration type,
call source span, normal result destination, unwind clause, tuple field, merge
input, range endpoint, padding type argument/predicate, points-to mode and an
extra unknown hidden address.
Each must be rejected; they only test this gate's own fail-closed behavior.

Run 37752503002 supplied the first fresh rewritten AST and a final normal-MIR
role certificate, but its AST gate was still `OPEN`/125. This new checker is a
candidate for the next separately pinned hosted experiment. Its source was not
run locally. A hosted parse/admission failure is diagnostic and cannot be
reclassified as an accepted proof or repaired by weakening the checked shape.
