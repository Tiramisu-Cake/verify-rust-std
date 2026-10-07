# Networks experiment journal

Historical common logs remain untouched. Own phase starts 2026-10-07 at
bea62488b44f8c557e45e04cb4eb259b0173422f. Budget 1800 summed hosted job seconds.

## N9 — prepared before implementation/dispatch

Actual obligation: sort9_optimal lines426–467, 25 actual swap_if_less calls.
Hypothesis: exact call sequence composes abstract compare-exchange into a sorted
9-element prefix and permutation of occurrences. A dropped final comparator
should break sortedness; a duplicated CE output should break permutation.

Domain: arbitrary nine logical occurrences and fixed total preorder on
preserved keys; all abstract CE calls normal. Rank variables are unbounded
mathematical integers, including ties. Separate permutation component admits
arbitrary Boolean decisions and retains complete occurrence identities.
Rust T unrestricted including ZST; the abstract proof has no physical memory.
Full normal target: sorted prefix, same occurrence multiset, fixed suffix modulo
callback effects. Full Rust safety/unwind target is in SWAP-CONTRACT and SOURCE-MAP;
this deliberately pure fixture does not discharge it or claim a panic model.

Profile: unchanged official VeriFast26.09/source809de459, release archive
da1b619f...98aa; no tool patches. Binary sorting plus checked per-CE threshold
commutation/general rank theorem, separate identity-count conservation.
Pure C ghosts require no Rust MIR/refinement; Rust bridge remains OPEN.

Controls: named positive binary/rank-transfer/permutation lemma bodies return
with full declared posts and leak checks; missing-final-CE negative rejects its
marked sortedness assertion on a concrete binary counterexample; duplicated
output negative rejects marked occurrence conservation. Unknown operation,
parse/setup/unrelated helper/timeouts are INCONCLUSIVE, never intended failures.
Full generated source/logs, before/after hashes, source map, verifier command and
exit, exact negative line and summary retained in Actions artifact.

Decision: positives and intended negatives all accepted -> prepare N13 under
same frozen profile. Routine ghost syntax/generation/classification failure ->
fix within phase and NEW SHA run, preserving failure. Missing semantics -> stop
without patch. Budget bound -> checkpoint. No automatic merge.

Dispatch: smallsort-research.yml on challenge-8/networks;
proof=verifast_sort4_components, sort4_component=networks9, budget_minutes=30.
Actual network job cap10min, per proof180s; only one job/experiment.
Source SHA/run/cost pending.

### N9 first result

Proof SHA `d433216f635c58d84ed9b9cde7bcab95c2c38549`,
[run37636248489](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37636248489),
[full artifact11490266217](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37636248489/artifacts/11490266217).
Artifact ZIP SHA2565ef244a960dc58e8fb7eac5c30a925e8db194b0b62b7d7a2008fa64d914ecab0,
41,706,974bytes; original raw results/classifications preserved.
Stock console dc672335da76fe1bb06cf7ebca916185c34edb65466df0a937645a437c7f0ecc.
Complete source gate matches25 calls with lines441–465; all source hashes unchanged.

Binary PASS,0.203703s/83 statements,496 return/leak paths. Threshold exit124 at
180s: only order_at_0 visited,12142 complete path return/leak checks; no full
8-adjacency theorem. Identity exit124 at180s,207556 path return/leak checks;
no full universal-choice permutation theorem. Millions of repeated statement
paths demonstrate branch explosion from inline conditionals, not a false proof.
Both timeouts INCONCLUSIVE; successful paths do not replace whole-unit acceptance.

Sorting negative: omission of step25(5,6), input mask11 (bit i = occurrence i),
mutant output000001011; correct error88,16–18, VC`!(true) || false`.
Permutation negative: duplicate0 instead of preserving3, correct error12,55–57,
VC`((0 = 3 ? 1 : 0) + (0 = 3 ? 1 : 0)) = (0 + 1)`.
Manual intended failures established; raw automatic classifiers INCONCLUSIVE:
they demanded literal false and counted untimed diagnostic-note headers twice.
Preserve this failure; do not overwrite original results.

Full Actions log and ZIP read, all generated sources/source map and log heads,
tails, errors, named bodies and complete path counts audited. No Rust proof.
One executed job14:23:19Z–14:29:40Z = **381s**; skipped jobs consume0.
Budget381/1800,1419 remain.

## N9b — within-profile decomposition, prepared before next dispatch

Same actual source/domain/normal target/unwind boundary as N9. Hypothesis:
pure min/max/selection fixpoints with **checked-body** local threshold and
two-occurrence conservation lemmas avoid repeating branch splits across the
25-step symbolic sequence. Keep every original final ordering and occurrence
count assertion, arbitrary ghost ranks/tokens/decisions and all tool gates.
New proof abstraction, not a new trusted tool rule; no assumed or bodyless lemma.
Exact local normal lemma posts: min/max commutes with arbitrary integer threshold;
selection pair preserves count of arbitrary occurrence q for arbitrary decision.
These proofs have no runtime/unwind/memory claims.

Classifier repair uses timestamped body headers and the two observed exact
normalized negative predicates. Require exact assertion line/columns, execution,
sole error and VF1. Hosted rejection controls: unrelated line, predicate, body,
target execution, column, timeout and source change. Preserve original N9 raw
INCONCLUSIVEs; a new source requires a new run. If all original positives and
intended negatives pass, advance N13; unsupported/profile change still STOP.
Cap10min/180s proofs, within remaining1419jobseconds. Run/SHA/cost pending.
