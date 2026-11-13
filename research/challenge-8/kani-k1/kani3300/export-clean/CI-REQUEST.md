# X1 coordinator CI request — NOT DISPATCHED

Prepared source `c9d3b2c17afe02ceabce73692279a797c54ddd69`, tree `b9d991ff795f35924272e448d819fb424fcda254`, from exact
`94c00a8859bc9e4f0f1b7db73a95dbee88f6213a`. Cloud preparation spend $0. This request
is not authorization for this worker to push, dispatch or submit CI.

1. Integrate the separately owned E1 + X1 changes into C0, record exact SHA/tree,
   and review any property-identity delta with the affected suite owner before
   changing its manifest. Keep intended operations and complete expected sets;
   never snapshot arbitrary newly failing properties.
2. First run Python negative/checker tests for both existing suites and both
   JSON-handler exec scenarios (`uninit-contract-oracles` and
   `uninit-contract-mode-boundaries`) with their existing `config.yml`/`test.sh`.
   Python checks are `python3 .../test_checker.py` and `python3 .../test_observe.py`.
   Actual suite runners are coordinator-only; do not run locally on the VPS.
3. Confirm eight exact oracle cases and all six roots were exercised, legal
   companions succeeded with required useful checks/covers, recursive negatives
   retained their exact cycle Unsupported inventories, Replace stayed unclaimed,
   missing/extra/nonterminal properties failed and cleanup did not hide diagnostics.
4. Then include the same two existing suites in unchanged Quick on that same
   integrated C0. Preserve profile defaults, object-bits12, full original exit/
   error information, timeout/RSS caps and exact source/tool/argv identities.

The regression runner now cleans temporary outputs and does not offer persistent
`--output`/receipt replay or `--keep-temps`. If exact exports/models/argv are needed
for CI evidence, capture them in a separate CI-only overlay under coordinator
control; do not reintroduce capture bookkeeping into upstream tests. Console
observations preserve complete mode outcomes/failures and detailed failing logs.
No CI workflow/overlay was added by X1.

No full gate/replay stage is executed by this task. Later M3/C1 binding, final
regression and uninit-on SmallSort replay need their own issued stage and exact
final source identities. Historical Quick claims in the plan are not X1 results.
Marker-diagnostic production work remains DEFERRED.
