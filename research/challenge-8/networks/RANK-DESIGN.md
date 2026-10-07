# Checked finite SWO construction and exact network composition

The abstract keys are immutable. Each original occurrence has a distinct ID;
`rel(i,j)` is the pullback of the chosen strict weak key order to those IDs.
Multiple IDs may have equivalent or identical keys. The same pure relation is
used for every comparison; this models preserved keys, faithful comparator
answers and normal completion, not an actual Rust callback implementation.

`finite_swo(rel,d)` explicitly requires irreflexivity and both transitivity
laws over every member/pair/triple of d through finite `forall` predicates.
No rank or embedding appears in this premise. `swo_rank(rel,d,id)` is stock
list `count` of strict predecessors in the ORIGINAL domain d; equal classes
may have different sizes, hence ranks may have gaps, but identical key classes
must have equal ranks. Integer occurrence IDs themselves are not ranks.

The generic bridge and CE/application bodies below were accepted in R9d,
[run37653851684](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37653851684),
source955fd2a3334e8fe14c55bdb00f98c4f9813da775, stock26.09. Network composition
is a separate acceptance gate; see STATUS for its current result.

Own checked bodies in swo-rank.c:

- `swo_forall_at` and `swo_laws_at` extract finite pointwise laws.
- `swo_pred_equiv` proves equal incoming comparisons for equivalent keys.
- `swo_equal_count_rec` proves count equality by structural list induction.
- `swo_strict_count_rec` proves subset count monotonicity and strict growth
  when the witness x is present; irreflexivity excludes x from pred(x), and
  x<y includes x in pred(y).
- `swo_rank_bound_rec` proves nonnegative ranks below domain length for members.
- `swo_rank_bridge` checks both less/rank< and equivalence/rank== directions.
- `swo_ce` proves each source-order comparison rel(right,left) realizes min/max
  ranks, stays inside the occurrence domain and preserves any token multiplicity.

prove-ranks.py uses unchanged prove.py for actual full-source SHA/literal-call
admission and the EXACT accepted integer rank theorem/helper generation. That
rank theorem's bodies are verified in each same-unit composition, before using
its summary. Generated SWO ID wires select original identities, not key ranks.
Each literal CE checks ID-wire equality, rank-wire equality, membership,
constructed rank/ID correspondence and arbitrary-q total occurrence count.
R9e checks the composed schedule against a symbolic original domain with
finite_swo and membership of the fixed original IDs. A separate body specializes
that theorem to the exact literal domain0..N-1 and discharges each initial
membership precondition. Both bodies retain full original posts and are checked
in the same unit; this prevents repeated concrete triple-law expansion rather
than adding an assumed theorem.

The final application checks the accepted whole-rank sorted post and converts
each adjacent pair back through the constructed bridge. Explicit exported posts
include all output IDs in the original domain, all adjacent !rel(right,left)
and equality of arbitrary-q occurrence multiplicity. No stability post.

One isolated negative keeps irreflexivity and strict transitivity but breaks
incomparability transitivity: only0<2;0~1,1~2,0!~2. Its constructed ranks satisfy
rank1=0<rank2=1 while less(1,2)=false. The expected failure is the marked
comparison-correspondence assertion, not a failed SWO-callee precondition or
unrelated helper. Negative sources include definitions only plus one own body.
The unchanged fail-closed classifier requires exact stage/location/predicate
and7 independently altered log/exit/source rejection controls.

The original admitted std bytes and networks remain unchanged. This phase adds
mathematical proof bodies; it does not rewrite the verifier's semantics or Rust
AST/MIR. Stock list/count/forall semantics stay fixed. No bodyless own lemma,
rank-correspondence assumption, comparator-panic post, pointer resource, Rust
memory safety, verifier soundness or public Challenge completion is supplied.
Current acceptance/open obligations are in STATUS and RANK-EXPERIMENT-LOG.

R9f adds swo_ordered_pair with a full body using swo_rank_bridge and exporting
only the needed adjacent order. Its new body and revised whole composition
await hosted verification; accepted generic R9d/R9e claims do not cover it.
