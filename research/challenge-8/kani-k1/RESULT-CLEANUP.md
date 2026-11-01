# RESULT CLEANUP — PASS
Task TASK-CLEANUP.md; branch experiment/kani-k1-cleanup-20261101.
Library commit `dd0f293f00c032d9fc69b74419a304dbb92d1108`.
Library tree `cbe69760c8166d49acf1171c46185dfa3d58b270`; base tree `3c23a45984f0f7cc5e43150a566b09fb1937e7c0`.
Removed all 149 cfg(any()) items, empty correct.rs and its registration; comments made self-contained.
Deleted lines: verify.rs 5; verify/correct.rs 207; verify/merge.rs 321;
verify/merge/specdiag.rs 239; verify/merge/specfix.rs 4; verify/network.rs 125.
Total: 901 deleted lines, 7 added comment lines; runtime smallsort.rs unchanged.
Static normalization/deletion provenance PASS; active bodies/signatures/attributes/order unchanged.
Candidate forbidden cfg(any())/DEACTIVATED/P1-CLEAN/poneclean/Known limitations: 0.
Source exact sets 200/382; cfg-on expected uses the required correct -> network full-name replacement.
Historical expected files, tools/workflows/flags/pin/cap unchanged.
pfc_order.py: 16 ordinary sites, 0 violations (ordinary only, not cfg-on metadata).
Rustfmt wrapper --check PASS for five surviving changed files; diff whitespace check PASS.
G1 `131ff241-7501-4942-b438-9a586f475b9c`: SUCCESS, controls false, native exact 200, $0.5940.
G1 request cleanup-g1-inventory-200-20261101; head `b996cc62ece60859ba7f20d2c37dc9962bf8f6db`.
G2 `a1fa83b7-22c5-4be5-b0b4-6b8805e536fe`: SUCCESS, controls true, native exact 382, $0.5400.
G2 request cleanup-g2-inventory-382-20261101; head `a476a6578864d802e61916021ee525ec60b552a1`.
Both exact native sets: missing/extra/duplicates 0; both build heads bind the library tree above.
Both request SHA-256, Kani pin 9461e07af7, inventory/page hashes and tooling identities match.
check-tooling vs 30f77e859903df14b442ff9294d4fbbd44827f20 PASS for both; pool k1-standard4.
Own builds 2/2; spent $1.1340 <= $1.4; reserved $0; combined submission reserve was $1.3500.
Global cap $88.96 untouched; costs selected only by the two own UUIDs.
Inventory confirms compilation/list membership; formal proofs were NOT_RUN in this task.
Artifacts: cleanup/PREBUILD.md, runs.json, final-check.json, g1/g2.inventory-check.json,
cleanup/g1/g2.summary.md, bounded inventory pages, tooling checks, budget-final-own.txt.
Coordinator GO for b996cc62ec; builds submitted consecutively, waited via k1g.sh watch.
P1 V5 CANDIDATE library tree cbe69760c8166d49acf1171c46185dfa3d58b270
CLEANUP ЗАВЕРШЁН
