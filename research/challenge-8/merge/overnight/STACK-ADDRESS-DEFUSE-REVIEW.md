# Bounded stack-role def-use admission review

Run 37762243525 historically passed the earlier `stack-roles` and
`stack-proof-ast` gates for the length-two/three diagnostic. Those gates found
the correct four hidden IDs and fourteen invariant addresses, but their
merge-argument and tuple-result checks were existential: a correct copy edge
could remain visible even if a later same-line assignment overwrote its
temporary before the call or cursor use. That historical `AST_LINKED` is not
evidence that the stronger checks in this revision have run. Actions dispatch
for a new run returned HTTP 422 without creating a job, so the stronger gate
remains **OPEN** pending a fresh GitHub-hosted matrix.

`stack-address-admission.py` now checks the four actual MIR `merge_up` and
`merge_down` operands, rather than inferring them from source text. Each must
be a distinct moved temporary with a single live-before-write definition in
the call terminator's own basic block and no earlier RHS use. The first three
definitions must copy the unique nonparameter VDI cursor for that role; the
fourth must take the mutable reborrow of the source `is_less` parameter. The
normal target block must extract fields 0, 1 and 2 in order, copy each through
one intermediate, then write only its corresponding source-named cursor in
order. Extra target-block reads/writes of the tuple result, intermediate
overwrites/reads and cursor overwrites are rejected. This is a bounded local
control-flow check for the compiler shape observed in the actual case; an
unfamiliar lowering fails closed instead of receiving a graph-reachability
pass. New in-memory mutants change a real MIR operand and overwrite an
argument, field temporary and cursor. An exhaustive walk of every decoded
`Place` in the selected function's `basicBlocks` requires the four hidden
roles to occur at precisely twelve previously identified parsed objects:
Range aggregate destination, `into_iter` argument and destination, iterator
move, both merge return destinations, and three field reads per tuple. The
gate compares object identities, not only names or counts. Further mutants
insert an extra hidden read, an extra write in another block, and a hidden
read nested in an aggregate operand.

`stack-proof-ast-admission.py` now locates the linear statement list that
contains each actual merge `SwitchStmt`. It requires the four immediately
preceding assignments to be the exact call argument definitions, followed by
the three immediate field extractions and six ordered bridge/cursor writes.
Additional same-line argument writes before the call, or later same-line
field/cursor writes, fail. The compiler-generated argument and tuple
intermediate locals must also have exactly one assignment anywhere in the
whole MIR body and proof AST; a nested or differently located overwrite of
those locals cannot be hidden by the local statement check. New in-memory
mutants insert the call/field/cursor overwrites. An exhaustive walk of `Var`
nodes in the selected proof-AST `Func` requires precisely twenty-seven
identified objects: thirteen runtime occurrences across the Range
constructor, range call/iterator move, both merge return assignments and six
tuple field reads, plus fourteen ghost `AddressOf` operands in the invariant.
New mutants add a hidden read on another source line and a nested hidden
write. This links the admitted raw call/return roles to the shape that
VeriFast actually verifies, without changing the proof AST or verifier.

The checks do not claim a whole-program dataflow proof. They establish the
bounded call block and its normal successor/linear AST statement path.
An exhaustive audit of every later write to source-named cursors remains
**OPEN**; source cursors legitimately change again in the actual loop and odd
branch, so a blanket uniqueness test would reject valid code. The hidden-role
walk covers all parsed MIR basic blocks and the selected proof-AST function;
it is not whole-program alias analysis, a check of calls' memory effects, or
a general control-flow proof. The exact unchanged runtime-source hash, stock
verifier, refinement checker and complete normal/unwind proof remain separate
mandatory gates. Raw MIR
retains the tuple pointer mutability distinction; the OCaml proof AST erases
that distinction and cannot independently recheck it. The exporter/decode
producer relation and translator semantics remain trusted tool boundaries.
Only static Python syntax parsing and `git diff --check` ran locally; no
exporter, generator, admission script, build or verifier was executed. All
strengthened admission and its new negative controls remain
**OPEN** until a fresh GitHub-hosted run; historical certificates were made
by earlier gate code. The current in-memory control suites expect thirteen
normal-MIR rejection mutants and seventeen proof-AST rejection mutants; the
five new hidden-role mutants require the specific exhaustive-access gate to
reject them, rather than accepting an unrelated earlier rejection.
