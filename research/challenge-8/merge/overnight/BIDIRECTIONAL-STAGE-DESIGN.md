# Checked panic option-stage facts

Run37752503002 /77f50f75 frames all14 hidden chunks and reaches the actual
first callback's unwind post. Its first failure is the pure relation
`bidirectional_unwind_options(dst0,dst1,dst0,dst1)==true`, with both initial
options arbitrary. No callback resource is missing at that reported obligation.

Keep the exact existing fixpoint unchanged. Prove its unchanged-state theorem
by case analysis on the first option, and prove first-write/full-write facts
by explicit assertions in checked lemma bodies. No trusted summary, axiom,
physical chunk or owner is added. The framed two-slot positive case must return
both exact old options; the negative writes only the suffix in the asserted
logical stage and must reach its marked assertion. Its oracle stays uncalibrated
until hosted evidence. All helper execution/return/leak/dead/source/export/
decode/refinement gates and old matrix remain mandatory.

The actual len2 invariant keeps all original resources. Invoke the unchanged
fact before the first actual merge_up call, on the same existing size_align
annotation line to avoid changing the number of in-body preprocessing tags.
Fresh normal-MIR roles still must match; final proof-AST linkage remains OPEN.
This pure dependency proves no whole bidirectional, caller bridge or Freeze fact.
