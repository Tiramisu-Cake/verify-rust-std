# O22 actual nested ghost scope repair, before frontend patch

O22 (`37754201983`, proof SHA `02945280…`) admitted the exact O21
five-body source and complete decoded MIR. Independent source controls
rejected at the verified-source SHA gate; both direct typed-MIR controls
rejected at the complete-unit SHA gate. The positive then raised OCaml
`Not_found` in `TrBody.translate_fn_call` while translating a
`VeriFast_ghost_command`. Its `List.find` matches a typed MIR ghost call's
source line against this body's `State.ghost_stmts` list.

The captured qualified nested Drop body has ghost-call terminators at
source lines 95 and 96, then the real pointer Drop call at line 97. Its own
exported `Body.ghostStmts` list is empty. Both source-written annotations
are instead the **first two** entries of the outer helper's 12-element
`Body.ghostStmts` list, with exact raw text and spans already pinned by
the O21 admission. The nested translator therefore receives no matching
statements and `List.find` throws. The outer translator also receives two
annotations whose MIR calls belong to the nested method. This is a
frontend ownership-of-metadata defect, not an absent proof resource.

The proposed separate overlay activates only after the exact source/full
decoded-unit admission. It moves those two existing annotation records
from the outer body's translator-local ghost list to the qualified nested
Drop body's translator-local ghost list. It requires the expected two raw
commands and exact outer/nested DefPaths; any different inventory rejects.
The original MIR, source spans, two ghost calls, runtime body, normal and
unwind successors, shared cleanup and all proof obligations remain intact.
No new ghost statement is fabricated and no call or postcondition is
deleted. A future six-body source variant requires its own renewed
admission before this reparenting may apply.

The trust boundary is the compiler exporter’s allocation of nested-source
ghost annotations to the enclosing body's metadata. The exact O21 source,
span and complete MIR pins justify only this two-record reparenting. The
positive must proceed past nested ghost-call translation and then run full
memory/validity/unwind/leak/dead-code/refinement checks; it is not accepted
merely by avoiding the exception. Negative controls must alter the two
ghost texts/spans, their order, a typed ghost call, or the qualified nested
DefPath and reject at the exact source/MIR gate or scope gate. Existing
three source/two direct-MIR O22 controls remain mandatory in the changed
profile. The next failure location determines whether a separate resource
or call-linkage component is needed.
