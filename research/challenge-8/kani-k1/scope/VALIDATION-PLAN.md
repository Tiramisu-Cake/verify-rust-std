# INTEG validation plan — inventories checked; proofs NOT RUN

Target library tree: `4dd5393bbb4524104c8b05cb70910c6836c3b8de`, after INTEG and without OPT/UNSTABLE8. The
current source inventory predicts 176 ordinary P1 names and 449 total with controls. The P2 candidate patch
predicts 339 ordinary names. All are source forecasts until inventory/build/CI results on the exact combined
SHA are available.

## Local static checks

Run from the repository root:

```sh
python3 research/challenge-8/kani-k1/scope/prepare_scope.py
python3 research/challenge-8/kani-k1/scope/prepare_pr2.py
python3 research/challenge-8/kani-k1/scope/check_scope.py
python3 research/challenge-8/kani-k1/scope/check_helpers.py
```

These scripts check source names, class manifests, the exact 31 Part 2-to-ordinary harmonics, paired Cell
argument cfgs, helper-use candidates, and a temporary-copy application of `pr2-ungate.patch`. They do not run
Rust expansion, a compiler, Kani, CBMC, or CI. Their JSON outputs are explicitly marked forecast-only.

## Future same-SHA inventory and CI

Before any formal run, pin the combined library tree and all toolchain/Kani/CBMC flags. Obtain actual ordinary
and controls inventories, then compare exact names and classes rather than tuning the Python forecast.
Check `unused_macros`, `unused_imports`, and `dead_code` in both configurations, including the per-argument
Cell cfg expansion. Verify every expected-fail control fails its intended property; a timeout, setup failure,
or missing result is not an expected failure.

P1 manifests: 176 ordinary; 231 positive extended names; 11 retired duplicates; 2 TIMEOUT diagnostics;
28 expected-fail controls; 1 unsupported deferred case. Keep diagnostics and controls separate from the
ordinary acceptance gate. The 10 positive DIRECT cases remain opt-in; each is marked `p2_candidate=yes` and
`p2_macos_ci=UNKNOWN`. The 12 new ordinary DIRECT cases likewise need verification on the combined SHA.

For DIRECT controls, verify that the value-corruption case fails in the shared `assert_sorted_and_probe_preserved`
oracle at the intended property. The ordinary DIRECT assertion counts and contract/scratch composition also
need same-SHA expansion. The `direct/results.tsv` FAILED control measurement used the previous control body;
the revised shared-oracle control has no current result and awaits measurement. Preserve the distinction between
the B/general caller matching exact T/N contracts and any conditional scratch48 allocation transfer.

The 11 old sorted-permutation C callers remain controls-only as retired duplicates; their checks record that
they have matching helper and T/F/N, both branches, the shared oracle, and no callers. C u64 N6..8 remains
conditional on supporting A u64 cases. Mutating-Cell insertion N6..19 stays opt-in in P1; only plain u64
insertion safety is among the 27 returned harmonics.

For any organizer or full-suite CI, use the coordinator's approved build workflow and current budget/slot
limits. Historical P-6 success is 8/8 for Actions run `40748125754` on its historical source; it does not
establish acceptance for this tree. Do not combine P-6 macOS VT with GCB timings from `direct/results.tsv`.

## Cost and evidence accounting

[`integ-cost.md`](integ-cost.md) reports the incremental known P-6 macOS ΣVT: +1159.9 s for the 31 returned
harmonics and −245.6 s for the 11 retired callers. New DIRECT ordinary Mac VT is UNKNOWN. DIRECT GCB seconds
and RSS remain separate per-harness data in [`scope.tsv`](scope.tsv). P-7 autoharness, division by job count,
and GCB-to-Mac conversion are excluded. Historical C3a records remain in `c3a-evidence.json` and are not
rewritten as new results.

## Completed INTEG inventory checks

On the same library tree, K-1 listed exactly 176 ordinary names on `91a8566276` and 449 names with controls
on `7da2486dc3`. Exact sets match the manifests; no `unused_`/`dead_code`/`smallsort/verify` grep matches
were found in either successful inventory log. The initial 10-minute list timed out, consuming one slot.
The three-build task limit is exhausted; no controls/smoke measurement was dispatched. The candidate request
and required file:line binding are recorded in `../integ/measurement-candidate.request.json` and
`../integ/source-audit.json`. Inventory success is not successful verification of any property.
