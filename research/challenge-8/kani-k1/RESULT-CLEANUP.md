# RESULT CLEANUP — G1/G2 DISPATCHED / WAITING FOR WATCH
Task TASK-CLEANUP.md; branch experiment/kani-k1-cleanup-20261101.
Library commit `dd0f293f00c032d9fc69b74419a304dbb92d1108`; library tree `cbe69760c8166d49acf1171c46185dfa3d58b270`.
Base library tree `3c23a45984f0f7cc5e43150a566b09fb1937e7c0`; runtime unchanged.
Removed all 149 cfg(any()) items and empty correct module; comments made self-contained.
Deleted lines: verify.rs 5; verify/correct.rs 207; verify/merge.rs 321;
verify/merge/specdiag.rs 239; verify/merge/specfix.rs 4; verify/network.rs 125.
Total: 901 deleted lines, 7 added comment lines.
Static normalization: PASS; active code and ordering unchanged in both cfg settings.
Deletion provenance: PASS; forbidden cfg(any())/DEACTIVATED/P1-CLEAN/poneclean/Known limitations: 0.
Source sets: ordinary exact 200; cfg-on exact 382; missing/extra/duplicates 0.
Expected cfg-on file uses the exact required correct -> network full-name replacement.
pfc_order.py: 16 ordinary sites, 0 violations; cfg-on metadata not checked by that script.
Rustfmt wrapper --check: PASS, five surviving changed files; diff whitespace check PASS.
Packet and reproducible checks: cleanup/PREBUILD.md, cleanup/*.py and JSON/TXT reports.
G1 `131ff241-7501-4942-b438-9a586f475b9c`: dispatched, controls false, expected exact 200.
G2 `a1fa83b7-22c5-4be5-b0b4-6b8805e536fe`: dispatched, controls true, expected exact 382.
Own builds 2/2; combined submission reserve $1.3500 <= $1.4; actual cost pending terminal accounting.
Global cap $88.96 unchanged; prebuild snapshot used $73.2480, reserved $0.
No compilation or proof acceptance is claimed before native inventories.
Coordinator GO for b996cc62ec received; both dispatched consecutively; identities in cleanup/runs.json.
P1 V5 CANDIDATE library tree cbe69760c8166d49acf1171c46185dfa3d58b270
