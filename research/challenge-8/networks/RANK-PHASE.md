# Phase 2: finite strict weak order to integer ranks

Owner authorization2026-10-07, entry
`a9fe187d48a492939970998ca862736a410c1adc`, branch challenge-8/networks.
IN PROGRESS. Separate **1800 summed hosted job seconds**, preparation/evidence
included, no transfer of phase1 unused301s or of the other direction's budget.
At most one run on this branch, two across the independently authorized directions.
All executable checks on GitHub-hosted Actions; no local proof/generator/tests.

1. Prove arbitrary finite SWO-to-rank embedding without assuming correspondence.
2. Compose with accepted rank-network theorem for N9, exact25 calls.
3. Only after full N9 acceptance, compose N13, exact45 calls.
4. Preserve exact open obligations if incomplete; update own documents/commit/push.

Model: distinct logical occurrence IDs0..N-1, fixed pure relation less(i,j)
representing the comparator on their immutable keys. Relation may identify many
IDs as equivalent, including all keys equal. A finite SWO requires irreflexivity,
strict transitivity and transitivity of incomparability on the entire domain.
Rank(i) is the number of ORIGINAL occurrences z with less(z,i); weights of equal
classes may create gaps, which do not change order or equality. Neither rank
existence nor comparison correspondence is a precondition. Prove equal predecessor
sets for equivalent keys and strict subset/count growth for strict comparison;
then prove less(i,j) iff rank(i)<rank(j), equivalence iff equal ranks, and bounds.

Composition: each literal CE uses less(current_id_b,current_id_a), exact operand
order. A checked local CE bridge relates resulting IDs and their constructed
ranks to min/max. Keep per-step occurrence membership, identities/counts and
rank-model correspondence; apply the actual checked rank theorem and prove
all final adjacent relation posts. Preserve every key via fixed relation and
occurrence map; callback normal return and faithful less result are explicit
functional applicability premises. No stability or Rust memory/panic claim.

Frozen tool: unchanged official VeriFast26.09, source
809de4596839b739dd999f9e462242c835e3af46, archive SHA256
da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa,
console SHA256dc672335da76fe1bb06cf7ebca916185c34edb65466df0a937645a437c7f0ecc.
Existing phase1 prove.py remains byte-identical (SHA256
994afa65a24c1deb73fd120ac88c96fa5d86eb971f58adba678c850a1153d0c4).
Accepted components regenerated verbatim and their bodies checked in the same
composition unit before summary use. No bodyless user lemmas/assumptions,
verifier/frontend/kernel/prelude patches, RAPx or Rust integration. Standard
stock list/forall facilities may express finite laws and induction; their
semantics remain unchanged. Tool-library proof code is not a new solution import.

Controls: missing incomparability-transitivity relation0<2 with1 incomparable
with both violates rank correspondence for1,2. Require rejection of that marked
correspondence assertion, after concrete rank evaluations; unsupported/setup/
precondition/timeout failure is inconclusive. Classifier must reject unrelated
location/predicate/body/target/column, timeout and changed source. Ties are in
positive universal domain and in full equality post, separate IDs/counts retained.

Per-case180s, inner420s, job8min including preparation/evidence; lower job cap if
remaining budget requires it. No blind retry; record card before each experiment,
resolve exact SHA/run, poll/read full artifacts. New trust or exhausted budget:
checkpoint exact unfinished obligation, no tool patch or local fallback.
