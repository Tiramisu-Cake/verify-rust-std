# INTEG scope forecast

Scope documents describe the library after INTEG, without OPT or UNSTABLE8. The source library tree is
`4dd5393bbb4524104c8b05cb70910c6836c3b8de`. This is a static source forecast, not compiler expansion,
`kani list`, proof success, or organizer CI evidence.

## Part 1 manifests

The inventory has **449 names**: 176 ordinary and 273 opt-in. The class column in [manifest.tsv](manifest.tsv)
assigns every name once; [scope.tsv](scope.tsv) retains the source item and evidence source for each name.

| Class | Count | Treatment |
|---|---:|---|
| ordinary | 176 | Default inventory |
| budget-deferred | 153 | Positive historical names still behind budget gates |
| retired-duplicate | 11 | Old `general_stable_sorted_permutation` C callers, retained under controls |
| positive-direct | 10 | DIRECT opt-in candidates |
| timeout-diagnostic | 2 | DIRECT 600-second timeouts; diagnostic only |
| expected-fail | 28 | 26 prior controls plus 2 DIRECT controls |
| deferred-unsupported | 1 | Unsupported ZST contract instrumentation |
| preexisting-opt-in | 68 | Remaining positive opt-ins |

Ordinary includes 12 DIRECT names: B `general_stable_direct_u64_n2..n5`, B `general_stable_direct_u8_n2..n8`,
and A `merge_scratch48_contract_u8_n9`. The 10 positive opt-ins are B u64 N6/7 and A u64/u8 N5..8. B u64 N8
and u8 N9 remain TIMEOUT diagnostics; the two controls remain expected failures. DIRECT results are evidence
from `direct/results.tsv`, measured on pilot library tree `e16a8ee5`; their macOS candidate status remains
UNKNOWN. The current INTEG source tree remains `4dd5393bbb4524104c8b05cb70910c6836c3b8de`.

The 11 retired callers were checked against their C harnesses: they use the same helper and T/F/N, cover both
branches, use the shared oracle, and have no name consumers. They remain present under controls. The matching B
callers stay ordinary. Ordinary C u64 N6..8 remains conditional on supporting A u64 proofs; A status is recorded
per row in the manifests.

The 31 Part 2 names returned to Part 1 ordinary are exactly three swap contracts, one mutating-route Cell case,
and 27 plain u64 insertion safety harmonics N6..19: four lower-length cases plus 23 grouped cases. Mutating-Cell
insertion proofs N6..19 remain opt-in in Part 1. Of these, 23 grouped invocations carry a cfg on the paired Cell
argument; the static parser records each generated name separately.

## Part 2 candidate patch

[pr2-ungate.patch](pr2-ungate.patch) is a single candidate patch. It removes 173 budget/positive-DIRECT cfg
gates: 158 rows classed budget-deferred, five shared helper rows, and 10 positive DIRECT gates. The 158 rows
refer to 153 distinct proof harmonics because helper and grouped-invocation gates can cover or repeat names;
the 23 paired Cell argument gates are individually represented. It preserves all 11
retired duplicates, both TIMEOUT diagnostics, all 28 expected-fail controls, the unsupported item, and other
pre-existing opt-ins. Static forecast: **339 ordinary P2 names** (`328 + 12 ordinary DIRECT + 10 positive
DIRECT − 11 retired duplicates`). Positive DIRECT in P2 is a candidate; macOS CI has not confirmed it.

Every `positive-direct` row in [manifest.tsv](manifest.tsv) and [scope.tsv](scope.tsv) is marked `p2_candidate=yes`
and `p2_macos_ci=UNKNOWN`. The changed value-corruption control has a historical FAILED row in
`direct/results.tsv` from a different body; the current shared-oracle control still awaits measurement.

[budget-gates.tsv](budget-gates.tsv) lists every removed gate, its class, exact helper or proof item, and the
harmonics associated by local source references. [pr2-static-check.json](pr2-static-check.json) records the
temporary-copy apply check, inventory, patch digest, and limitations.

## Cost evidence

[integ-cost.md](integ-cost.md) separates historical P-6 macOS VT arithmetic from DIRECT GCB measurements.
The 31 returned names contribute **+1159.9 s known P-6 ΣVT**; removing 11 retired callers subtracts **245.6 s**.
The 12 new DIRECT ordinary names have no P-6 macOS VT, so their contribution is UNKNOWN. P-6 history is from
8/8 partitions in Actions run `40748125754`. DIRECT GCB results come from `direct/results.tsv`; GCB time and
RSS are listed per harness in [scope.tsv](scope.tsv), not converted to Mac VT. No P-7 autoharness projection,
job-count division, or cross-platform coefficient is applied.

## Validation

Run from the repository root:

```sh
python3 research/challenge-8/kani-k1/scope/prepare_scope.py
python3 research/challenge-8/kani-k1/scope/prepare_pr2.py
python3 research/challenge-8/kani-k1/scope/check_scope.py
python3 research/challenge-8/kani-k1/scope/check_helpers.py
```

These checks use a narrow Python source scan and token-reference helper forecast. They do not run a compiler,
Kani, CBMC, or CI. The positive DIRECT P2 candidate and combined branch still require organizer CI.
