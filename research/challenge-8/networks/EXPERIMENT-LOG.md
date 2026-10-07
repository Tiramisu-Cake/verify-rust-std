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
