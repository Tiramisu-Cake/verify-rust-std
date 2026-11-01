# CLEANUP PRE-BUILD REVIEW

Status: WAITING FOR COORDINATOR GO; no dispatch authorized before that GO.
Review SHA is the published commit containing this packet, reported with PRE-BUILD REVIEW.
Base `e2c5ac879b8f18bcc5684f79f24d5e5195c30e54`; source/library equals task base `7f558e061a`
(tree `3c23a45984f0f7cc5e43150a566b09fb1937e7c0`).
Library commit `dd0f293f00c032d9fc69b74419a304dbb92d1108`; library tree `cbe69760c8166d49acf1171c46185dfa3d58b270`.
Branch `experiment/kani-k1-cleanup-20261101`; task `TASK-CLEANUP.md`.

## Patch

Removed 149 `cfg(any())` items: correct 33, merge 75, network 26, specdiag 15.
Deleted empty `correct.rs`, its module registration and doc entry; simplified historical comments.
Changed library lines (+/-): verify.rs 3/5, correct.rs 0/207, merge.rs 2/321,
merge/specdiag.rs 0/239, merge/specfix.rs 2/4, network.rs 0/125 (7/901 total).
Runtime smallsort.rs is byte-identical; active helpers/macros, signatures, attributes, bodies,
gates, names and module/item order remain identical after prescribed normalization.
`define_merge_contract_harness` remains active for ordinary lengths N5..8.

## Static evidence and reproduction

- `python3 -B research/challenge-8/kani-k1/cleanup/check_cleanup.py`: PASS;
  report `static-check-prebuild.json` covers every verify source file, including deleted correct.rs.
  Strings/chars/raw strings are preserved; retired items are delimiter-balanced with comments hidden.
  After deleting retired items, comments, empty lines and `mod correct;`, base/candidate bytes match.
  Surviving code-line bijection establishes deletion provenance despite ambiguous repeated braces
  in a textual diff. All five forbidden markers have zero candidate occurrences.
- `source_inventory.py`: exact ordinary 200 and cfg-on 382, no missing/extra/duplicate names;
  `source-inventory.json` binds each source file by SHA-256 and records item/macro/module gates.
  Ordinary expected is the historical `integwrapfix/ordinary-expected.txt` unchanged;
  cfg-on expected is `cleanup/cfg-on-expected.txt`, the exact required full-name substitution.
- `integwrapfix/pfc_order.py library/core/src/slice/sort/shared/smallsort`: 16 sites, bad 0.
  This checks ordinary order only. Both cfg trees are covered by normalization; native compilation
  and metadata remain NOT_RUN until inventories. See `pfc-order.txt`.
- TASK-SPECFIX rustfmt wrapper: exit 0 for all five surviving changed Rust files;
  `git diff --check` clean, Rust/comments <=100 columns. See `rustfmt-check.txt`.
- `checker-validation.json`: lexical cases and active-body/string mutation detection PASS.
- No local cargo/rustc/Kani/proof, Actions, CircleCI or macOS builds were run.

## Exact requests and budget

Both use kind inventory, runner gcb-e2-standard-4, inventory:true, harnesses:[], timeout 20 min;
kani_jobs, uninit_checks and worker fields are absent. Validator accepts both, see request-validation.json.

| Build | Request / controls | Expected exact set | SHA-256 | Envelope / reserve |
|---|---|---|---|---|
| G1 | cleanup-g1-inventory-200-20261101 / false | 200 | 835d8aa13613fadc96f4531b633f2980745ba828357570bab5889dc3e806e4ea | 50 min / $0.6750 |
| G2 | cleanup-g2-inventory-382-20261101 / true | 382 | c1f8050c79695af906911c8a2f57d4483f2cd91e51170506650f9e5f83443d8e | 50 min / $0.6750 |

`RUN-REQUEST.json` equals `cleanup/g1.request.json`; G2 is `cleanup/g2.request.json`.
Own builds 0/2, spent/reserved $0/$0; maximum combined reservation $1.35 <= $1.4.
Project snapshot: used $73.2480, reserved $0, cap $88.96 unchanged (budget-prebuild.txt).
Session is the task window; both 50-minute envelopes and closing work fit after GO only if
that session window remains open. Refresh global budget before each submission.

## Continuation after GO

Dispatch G1 from the published review SHA; change only RUN-REQUEST.json to the prepared G2 request,
commit `[skip ci]`, push without force, refresh budget, dispatch G2 immediately after G1 submission.
The library tree must remain `cbe69760c8166d49acf1171c46185dfa3d58b270` for both builds.
Register `tools/k1g.sh watch UUID` for each build with CODEX_THREAD_ID and end the turn.
On queued completion read bounded K-1 summaries/inventories, match exact name sets and bound identities,
check tooling against `30f77e859903df14b442ff9294d4fbbd44827f20`, account own UUIDs and actual cost.
Evidence Brief / Select-Merge phases do not apply to K-1; use task-prescribed bounded K-1 interface.
Inventory establishes compilation/list membership, not formal proof acceptance.
Update RESULT-CLEANUP.md (<=40 lines) and mark CLEANUP ЗАВЕРШЁН only after both exact inventories pass.

P1 V5 CANDIDATE library tree cbe69760c8166d49acf1171c46185dfa3d58b270
