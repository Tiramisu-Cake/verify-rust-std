# DIRECTFOUR G2 PRE-BUILD REVIEW (compile-error branch)

Status: WAITING FOR NEW COORDINATOR GO. G2 not submitted.
G1 Build 37d72ac9-af24-4969-8754-e1e01ef6be88 @88d57dea95 (GO 88d57dea95): Cloud FAILURE, summary COMPILE_ERROR,
row NOT_RUN; cost $0.1080; whole-run max RSS 1306248 KiB (kani-compiler 1287724 KiB), wall 45.98 s, OOM none_seen;
check-tooling vs 30f77e8599 PASS. Evidence: g1.{summary.md,status.json,rows.txt,cost.txt,peaks.txt,tooling.txt,
error-lines.txt}, runs.json.
Cause (log, bounded excerpt g1.error-lines.txt): 3x E0599 in directfour.rs:15/16/23 — `StrictU8::set_probe`,
`StrictU8::probe`, `StrictU8::CMP` are associated items of trait `specfix::Profile`, which mergestep.rs imports
but the child did not ("trait `Profile` ... is implemented but not in scope"). My PRE-BUILD missed it.

## Fix (g2-fix.diff, one line)

directfour.rs import `specfix::merge_profile` -> `specfix::{Profile, merge_profile}` (the exact import line
of mergestep.rs:12). Nothing else changed: same fixture/call/check_merge4/6 covers, annotations
(PFC merge_profile + unwind34, no stub/stub_verified), request, row, flags, pin, tooling.
Library commit 248b2725c6cd528a6d87aa5928e362dc11e74522, tree 7996f9c151be2011be23bb44d04f286ea2905810;
directfour.rs sha256 d8f694728de2393e…; mergestep.rs unchanged since G1 (2ae7e36d…).
Request unchanged: directfour-direct-merge4-baseline-20261102, SHA256 82bc61a1…85d5fb (same bytes as G1).

## Static (not proofs)

static_check.py PASS (refreshed static-check.json; statement equality with the old composed root, 6 covers,
ordinary200, cfg405); pfc_order 25/bad0; rustfmt wrapper PASS both .rs; git diff --check PASS; lane/tooling
== 30f77e8599. Remaining risk (cannot check locally): later rustc/Kani phases did not run in G1.

## Budget / slots (observed after G1, k1g.sh budget)

builds170; used$79.1475; unfinished reserve$0.6750 (NETTEN-LEAVES, owner k1-merge, not attributed here).
Own: spent$0.1080 + G2 reserve$0.540 = $0.648 <= stage cap$1.10. Project $79.1475+$0.675+$0.540=$80.3625 <=
$88.96. Slots: project 1 unfinished + G2 = 2 <= 2; k1-network 0 -> 1 <= 1. Refresh again after GO.
No G3: any G2 outcome (incl. another compile error) is recorded and STOP.
