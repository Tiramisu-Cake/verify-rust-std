# Strict lifetime cut: immutable entry metadata and same-file admission

This is a review of the **unaccepted** 26.10 lifetime-cut draft, before
changing the implementation. The base is stock VeriFast `f76012fb` with the
current 12 production patches in `overnight/run-s6.sh` order. The draft has
not been built or verified on that base. It remains a separate opt-in trusted
translator/kernel component; actual `sort4_stable` requires its own complete
source and typed-MIR certificate and checked resource recovery.

## Defect and falsifiable repair

The draft saves `!tparam_bounds_table` and `outer_tenv` as OCaml lists. This is
only a shallow snapshot: a bound or outer-variable type can contain an
`InferredType` with a mutable state reference. `type_fold_open` ignores that
constructor. A reference unresolved at entry could later resolve to a type
containing the ending lifetime, escaping the current strict check. Resolved
`EqConstraint` chains can also alias later mutable references. The claim that
entry bounds are immutable is therefore false.

At strict block entry, recursively resolve and rebuild all types in the
saved outer bounds and outer type environment into values containing no
`InferredType` references. Reject unresolved/cyclic inference or an unknown
constructor with an exact strict-snapshot error; do not guess a type. At
every strict exit, inspect live heap type arguments, outer variable types,
and current bounds with the same fail-closed traversal: unresolved inference
is rejected before metadata rebasing. A live scoped type in a heap argument
or surviving outer variable is rejected. A bound learned *inside* the scope
for an already outer type parameter such as `F` may be forgotten at the cut
and its heap/variable metadata rebased to the frozen entry bound; this
forgets a local proof fact, never adds one or changes a permission, predicate,
coefficient or heap term. A scoped type on a non-outer live heap argument is
rejected. Saved entry bounds must be free of the ending type. Ordinary blocks
do not use this operation.

The draft also compares marker and ghost-block source positions without an
explicit file identity test. Require the marker, declaration-block open and
close positions to name the same source file before constructing a cut.
Cross-file positional coincidence is rejected before proof. The generic
opt-in operation need not hardcode one body path, but its use for actual
sort4 is conditional on separate exact body/source/MIR/CFG admission.

## Trust and control obligations

This changes trusted AST scope correspondence and strict exit checking in
`vf_mir_translator.ml` and `verifast.ml`; no prelude, resource rule, SMT,
memory model, or check disabling is authorized. The candidate patch must be
rebased onto all 12 current patches and limited to those two files.

Hosted controls required before acceptance: a concrete `F` bound whose
entry snapshot and exit rebase preserve a lawful proof; an inference that
resolves late to the ending lifetime; a live bounded heap type argument;
an outer variable carrying the scoped lifetime; and a goto into the cut
prefix. Each negative needs a matching lawful setup and must fail at its
intended admission/exit predicate, not at parse, missing callee or an earlier
resource. Check normal, return, direct unwind, and outgoing-goto exits;
duplicate/foreign-file marker, missing/extra marker and no-opt-in rejection;
ordinary block/Drop and full S6/H2/callback regression. Record exact source
file equality, full body path and complete NORMAL/readonly typed MIR plus
original/mutated hashes. Full actual sort4 normal/unwind posts stay unchanged.

No result from these controls is claimed yet. Local work is static editing
and patch review only; root alone runs hosted tests.
