# Disk cleanup inventory — 2026-11-20

Task base: `20784d58a8f95e99b976a8fe80b5dc9676141e2b`. One inventory stage. Inspected working copies were read only; no deletion, fetch, checkout, reset, stash, worktree mutation, build or CI was performed. Only INVENTORY.json and SUMMARY.md are deliverables.

Inventory time: 2026-11-20T17:14:54.733046+00:00 to 2026-11-20T17:22:12.562866+00:00. Every one of the 216 direct /root Git working copies is represented.

## Totals

| Class | Copies | GB (10^9 bytes) | GiB (2^30 bytes) |
| --- | ---: | ---: | ---: |
| SAFE_DELETE | 2 | 0.100495 | 0.093594 |
| ASK | 186 | 7.053345 | 6.568939 |
| KEEP | 0 | 0.000000 | 0.000000 |
| KEEP_PROTECTED | 28 | 5.307310 | 4.942818 |
| **Total** | **216** | **12.461150** | **11.605350** |

Sizes are allocated bytes from separate du -sx --block-size=1 calls. Shared storage and hardlinks can be counted repeatedly, so totals do not guarantee reclaimed space. Protected entries use directory mtime and deliberately skip status/publication analysis; null/skipped fields do not claim clean/published state.

## SAFE_DELETE — largest first

Commands are proposals for the coordinator; none were executed. Recheck activity before any later deletion.

| Working copy | GB | Newest tree mtime (UTC) | Removal command |
| --- | ---: | --- | --- |
| `/root/kani-fix-3300-c2-gatea` | 0.068473 | 2026-11-15T08:41:35.045355+00:00 | `rm -rf /root/kani-fix-3300-c2-gatea` |
| `/root/verifast-mdnew-final` | 0.032023 | 2026-11-15T08:42:03.036353+00:00 | `rm -rf /root/verifast-mdnew-final` |

## SAFE_DELETE verification sample

The task requested five rechecks. Only 2 copies qualified; all 2 were rechecked, and 2 passed. No uncertain copy was promoted to fill the sample.

Rechecked HEAD/branch/common-dir identity, all local branch tips, every publication witness, porcelain status, newest tree mtime, du, worktree registration, current recent research/TODO references, tmux panes and /proc/*/cwd. The acquired GitHub tip snapshot was reused without fetching. Per-record sample_recheck contains the detailed results.

- `/root/kani-fix-3300-c2-gatea`: PASS
- `/root/verifast-mdnew-final`: PASS

## ASK — one-line reasons

- `/root/cbmc-zst-prready-ci` — tree modified <2 days ago.
- `/root/kani-5183-merge` — 10 local branch tips not confirmed published (shared common-dir scope); tree modified <2 days ago.
- `/root/kani-b3-t1` — 9 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-5151-edition-w13` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-5151-w13` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-b-census-w14` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-b-pprime-w14` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-c-ctl-w14` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-c-ctl-w14-pprime` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-c02-intake-w14` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-e-ctl-w15` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-e02-w15` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-issue-mre-w14` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-issue-mre2-w14` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-prof-off-intake-w11` — HEAD UNPUBLISHED; 9 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-prof-off-w11` — HEAD UNPUBLISHED; 9 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-prof-on-w15` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-prof02-w11` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-s1-04-depth-w13` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-s1-04-w13` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-s1-04-yaml-w13` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-s1-05-intake-fix-w13` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-s1-05-w13` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-s1-06-intake-w13` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-s1-07-w13` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-s1-08-cell-retry-fix-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (2 matches).
- `/root/kani-ch8-s1-08-cell-retry-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-s1-08-fix-w13` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-s1-08-go-control` — 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (1 matches).
- `/root/kani-ch8-s1-08-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-s1k-batch-w13` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-s1k-list-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-s1k-nolist-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-s1k-pprime-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-s1k-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-s2-batch-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (6 matches).
- `/root/kani-ch8-s2-cfg-r1-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (11 matches).
- `/root/kani-ch8-s2-diagnostics-r2-r1-w11` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (26 matches).
- `/root/kani-ch8-s2-diagnostics-w11` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (13 matches).
- `/root/kani-ch8-s2-r14-03-gate-backlog-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (23 matches).
- `/root/kani-ch8-s2-r2-packed-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (6 matches).
- `/root/kani-ch8-s2-r2-r1-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (8 matches).
- `/root/kani-ch8-s2-r2-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-s2-r3-final-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (28 matches).
- `/root/kani-ch8-s2-r3-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (3 matches).
- `/root/kani-ch8-s2-r4-final-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (12 matches).
- `/root/kani-ch8-s2-r4-r1-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (26 matches).
- `/root/kani-ch8-s2-r4-r2-final-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (29 matches).
- `/root/kani-ch8-s2-r4-r2-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (7 matches).
- `/root/kani-ch8-s2-r4-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-s2-r5-final-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-s2-r5-package-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (37 matches); tree modified <2 days ago.
- `/root/kani-ch8-s2-r5-r1-final-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (49 matches); tree modified <2 days ago.
- `/root/kani-ch8-s2-r5-r1-stable-final-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (58 matches); tree modified <2 days ago.
- `/root/kani-ch8-s2-r5-r1-stable-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (10 matches); tree modified <2 days ago.
- `/root/kani-ch8-s2-r5-r1-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (1 matches); tree modified <2 days ago.
- `/root/kani-ch8-s2-r5-ready-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (6 matches).
- `/root/kani-ch8-s2-r5-release-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-ch8-s2-r5-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (5 matches).
- `/root/kani-ch8-s3-1-control-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (195 matches); tree modified <2 days ago.
- `/root/kani-ch8-s3-1-final-control-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (23 matches); tree modified <2 days ago.
- `/root/kani-ch8-s3-1-r1-control-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (35 matches); tree modified <2 days ago.
- `/root/kani-ch8-s3-1-r2-control-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (87 matches); tree modified <2 days ago.
- `/root/kani-ch8-s3-2-r1-control-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (20 matches); tree modified <2 days ago.
- `/root/kani-ch8-s3s4-bridge1-control-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (14 matches); tree modified <2 days ago.
- `/root/kani-ch8-s3s4-bridge1-r1-control-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (33 matches); tree modified <2 days ago.
- `/root/kani-ch8-s4-next-control-w15` — HEAD UNPUBLISHED; 4 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (25 matches); tree modified <2 days ago.
- `/root/kani-ch8-s4p-1-control-w13` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (43 matches); tree modified <2 days ago.
- `/root/kani-ch8-s4p-2-control-w13` — HEAD UNPUBLISHED; 4 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (11 matches); tree modified <2 days ago.
- `/root/kani-ch8-s4p-2-r1-control-w13` — 4 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (56 matches); tree modified <2 days ago.
- `/root/kani-confirm-main-w15` — 10 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (1 matches).
- `/root/kani-f4-confirm-w15` — 10 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (12 matches).
- `/root/kani-f4-fix-w15` — HEAD UNPUBLISHED; 10 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (19 matches).
- `/root/kani-f4-uninit-only-w15` — HEAD UNPUBLISHED; 10 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (17 matches).
- `/root/kani-fix-3300-c2-gateb-w15` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-fix-3300-c2-slices-w14` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-fix-3300-c2-slices-w15` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-fix-3300-sel1` — referenced by recent research/TODO (1 matches).
- `/root/kani-fix-3300-sel1-c2-w14` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-fix-3300-sel1-c2-w15` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-fix-3300-sel1-replay-w15` — HEAD UNPUBLISHED; 1 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-fix-autoharness-uninit-reset-w14` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (10 matches).
- `/root/kani-fix-ch8-pr02-final` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-fix-ch8-pr02-reset-ci-w15` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-fix-ch8-pr02-reset-u02-ci` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-fix-ch8-pr02-reset-u02-source` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-fix-ch8-pr02-reset-u03-ci` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-fix-ch8-pr02-reset-u03-source` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-fix-ch8-pr02-reset-w15` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-fix-ch8-w0-a1-r3-w15` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-fix-ch8-w0-a1-w15` — 55 local branch tips not confirmed published (shared common-dir scope).
- `/root/kani-fix-delayed-ub-recursion-w14` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (4 matches).
- `/root/kani-issue4591-fix-main-r2-w15` — HEAD UNPUBLISHED; 10 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (13 matches); tree modified <2 days ago.
- `/root/kani-issue4591-fix-r1-w15` — HEAD UNPUBLISHED; 10 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (7 matches); tree modified <2 days ago.
- `/root/kani-issue4591-fix-w15` — HEAD UNPUBLISHED; 10 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (10 matches); tree modified <2 days ago.
- `/root/kani-issue4591-singlecall-r3-w15` — HEAD UNPUBLISHED; 10 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (38 matches); tree modified <2 days ago.
- `/root/kani-issue4591-test-reduction-r4-w15` — HEAD UNPUBLISHED; 10 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (15 matches); tree modified <2 days ago.
- `/root/kani-pr5183-cleanup-w11` — 10 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (9 matches); tree modified <2 days ago.
- `/root/kani-pr5183-slop-readonly-20261119` — 10 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (6 matches); tree modified <2 days ago.
- `/root/kani-pr5184-slop-readonly-20261119` — HEAD UNPUBLISHED; 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (5 matches); tree modified <2 days ago.
- `/root/kani-pr5195-cleanup-w11` — 10 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (15 matches); tree modified <2 days ago.
- `/root/kani-pr5195-slop-readonly-20261119` — 10 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (6 matches); tree modified <2 days ago.
- `/root/kani-review-3300` — 29 tracked changes; HEAD UNPUBLISHED.
- `/root/kani-stub-contract-control-w15` — HEAD UNPUBLISHED; 10 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (18 matches); tree modified <2 days ago.
- `/root/kani-stub-contract-push-control-w15` — 10 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (20 matches); tree modified <2 days ago.
- `/root/kani-stub-contract-source-w15` — 10 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (17 matches); tree modified <2 days ago.
- `/root/kani-upstream-3300` — referenced by recent research/TODO (3 matches).
- `/root/kani-upstream-ch8-s1` — 55 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (307 matches).
- `/root/smallsort-watcher-prepared` — 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-i-actual-glue` — HEAD UNPUBLISHED; 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-maintainer-c4-composition-20261010b` — HEAD UNPUBLISHED; 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-maintainer-native-h` — HEAD UNPUBLISHED; 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-maintainer-slice-i` — HEAD UNPUBLISHED; 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-manuallydrop-review` — HEAD UNPUBLISHED; 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-mdnew-clean` — 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-mdnew-pr` — HEAD UNPUBLISHED; 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-mdnew-validation` — HEAD UNPUBLISHED; 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-merge-actual-glue` — 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-merge-allocation-span` — HEAD UNPUBLISHED; 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-merge-incoming-span` — HEAD UNPUBLISHED; 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-merge-r23-source-adapter` — 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-merge-selected-drop` — 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-network` — 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-network-n13` — 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-select-compatible-strict-cut-20261010` — 2 tracked changes; 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-select-native-c1-bound-20261010` — 2906 tracked changes; 1 untracked files of uncertain value; 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-select-native-compose-20261010` — 3 tracked changes; 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-select-sort4-c2-bind-20261010` — 4 tracked changes; 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-select-sort4-c3-bind-20261010` — 4 tracked changes; 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-select-sort4-c4-bind-20261010` — 4 tracked changes; 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-select-sort4-native-20261010` — 4 tracked changes; 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-select-sort4-opaque-20261010` — 2906 tracked changes; 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verifast-slice-upstream-l` — HEAD UNPUBLISHED; 15 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-ch8-c-ctl-w14` — HEAD UNPUBLISHED; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-ch8-c-ctl-w14-pprime` — 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-ch8-profiles-w11` — 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-ch8-s1-04-w13` — 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-ch8-s1-08-w13` — 14 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (10 matches).
- `/root/verify-rust-std-ch8-s1-pprime-w13` — 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-ch8-s1-w11` — HEAD UNPUBLISHED; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-ch8-s1-w13` — HEAD UNPUBLISHED; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-ch8-s2-batch-w13` — 14 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (10 matches).
- `/root/verify-rust-std-ch8-s2-cfg-r1-w13` — 14 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (13 matches).
- `/root/verify-rust-std-ch8-s2-r2-final-w13` — 14 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (9 matches).
- `/root/verify-rust-std-ch8-s2-r2-packed-w13` — HEAD UNPUBLISHED; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-ch8-s2-r2-w13` — HEAD UNPUBLISHED; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-ch8-s2-r3-w13` — 14 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (22 matches).
- `/root/verify-rust-std-ch8-s2-r4-r1-w13` — 14 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (145 matches).
- `/root/verify-rust-std-ch8-s2-r4-w13` — HEAD UNPUBLISHED; 14 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (7 matches).
- `/root/verify-rust-std-ch8-s2-w15` — HEAD UNPUBLISHED; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-ch8-s3-1-final-w13` — 14 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (71 matches); tree modified <2 days ago.
- `/root/verify-rust-std-ch8-s3-1-w13` — HEAD UNPUBLISHED; 14 local branch tips not confirmed published (shared common-dir scope); tree modified <2 days ago.
- `/root/verify-rust-std-ch8-s3-2-r1-w13` — 14 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (13 matches); tree modified <2 days ago.
- `/root/verify-rust-std-ch8-s3s4-bridge1-w13` — 14 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (175 matches); tree modified <2 days ago.
- `/root/verify-rust-std-ch8-s4-next-w15` — 14 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (16 matches); tree modified <2 days ago.
- `/root/verify-rust-std-ch8-s4p-1-w13` — 14 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (116 matches); tree modified <2 days ago.
- `/root/verify-rust-std-ch8-s4p-2-w13` — 14 local branch tips not confirmed published (shared common-dir scope); referenced by recent research/TODO (47 matches); tree modified <2 days ago.
- `/root/verify-rust-std-ch8-w0-a1-r3-w15` — HEAD UNPUBLISHED; 4 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-ch8-w0-a1-w15` — HEAD UNPUBLISHED; 4 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-coordinator-v3` — 7 tracked changes; 10 untracked result-like files; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-coordinator-v4-refinedrust` — 3 tracked changes; 10 untracked result-like files; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-docs` — 6 tracked changes; 10 untracked result-like files; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-g1-review` — 6 tracked changes; 10 untracked result-like files; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-i-actual-glue` — 7 tracked changes; 10 untracked result-like files; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-kani3300-gateb-prime` — HEAD UNPUBLISHED; 2 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-kani3300-pr02-reset-u02` — HEAD UNPUBLISHED; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-kani3300-pr02-reset-u03` — HEAD UNPUBLISHED; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-kani3300-replay-w15` — HEAD UNPUBLISHED; 1 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-kani3300-t0` — 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-merge` — 2 tracked changes; 10 untracked result-like files; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-merge-origin` — 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-networks` — 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-pr694-audit` — 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-refinedrust-feasibility-20261011` — 8 tracked changes; 10 untracked result-like files; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-review-v6` — 7 tracked changes; 10 untracked result-like files; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-select-night` — 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-verifast-bound-j` — 6 tracked changes; 10 untracked result-like files; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-verifast-compose2` — 6 tracked changes; 22 untracked result-like files; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-verifast-compose3` — 6 tracked changes; 31 untracked result-like files; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-verifast-compose4` — 6 tracked changes; 13 untracked result-like files; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-verifast-glue-k` — 6 tracked changes; 10 untracked result-like files; HEAD UNPUBLISHED; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-verifast-infra` — 5 tracked changes; 13 untracked result-like files; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-verifast-native-h` — 6 tracked changes; 16 untracked result-like files; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-verifast-select` — 6 tracked changes; 20 untracked result-like files; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-verifast-slice-i` — 6 tracked changes; 16 untracked result-like files; 14 local branch tips not confirmed published (shared common-dir scope).
- `/root/verify-rust-std-verifast-upstream-l` — 6 tracked changes; 16 untracked result-like files; 14 local branch tips not confirmed published (shared common-dir scope).

## KEEP_PROTECTED

- `/root/cbmc-fix-zst-bits2expr` — common-dir owner with linked worktrees; protected upstream PR branch: https://github.com/diffblue/cbmc/pull/9487; HEAD is protected upstream PR head.
- `/root/cbmc-pr9487-slop-readonly-20261119` — HEAD is protected upstream PR head; working copy of explicitly protected upstream work.
- `/root/kani-5159-followup-main` — explicit TASK.md protected path; working copy of explicitly protected upstream work.
- `/root/kani-5159-followup-w11` — explicit TASK.md protected path; working copy of explicitly protected upstream work.
- `/root/kani-5159-merge` — working copy of explicitly protected upstream work.
- `/root/kani-5172-fixup-w11` — working copy of explicitly protected upstream work.
- `/root/kani-ch8-s4p-1-r1-control-w13` — common-dir owner with linked worktrees.
- `/root/kani-fix-3300-c2-s5` — common-dir owner with linked worktrees.
- `/root/kani-fix-3300-c2-s6` — common-dir owner with linked worktrees.
- `/root/kani-fix-5206-w13` — explicit TASK.md protected path; working copy of explicitly protected upstream work.
- `/root/kani-fix-b1-upstream` — protected upstream PR branch: https://github.com/model-checking/kani/pull/5172.
- `/root/kani-fix-zst-b3` — common-dir owner with linked worktrees.
- `/root/kani-fix-zst-b3-v4` — protected upstream PR branch: https://github.com/model-checking/kani/pull/5176.
- `/root/kani-pr5159-cleanup-w13` — working copy of explicitly protected upstream work.
- `/root/kani-pr5159-slop-readonly-20261119` — working copy of explicitly protected upstream work.
- `/root/kani-pr5172-cleanup-w11` — working copy of explicitly protected upstream work.
- `/root/kani-pr5172-copilot-w15` — explicit TASK.md protected path; working copy of explicitly protected upstream work.
- `/root/kani-pr5172-slop-readonly-20261119` — working copy of explicitly protected upstream work.
- `/root/kani-pr5176-cleanup-w13` — working copy of explicitly protected upstream work.
- `/root/kani-pr5176-slop-readonly-20261119` — working copy of explicitly protected upstream work.
- `/root/ozon-warehouse` — Ozon-related; common-dir owner with linked worktrees.
- `/root/ozon-warehouse-agent-first` — Ozon-related.
- `/root/ozon-warehouse-pr93` — Ozon-related.
- `/root/verifast` — common-dir owner with linked worktrees.
- `/root/verify-rust-std` — common-dir owner with linked worktrees.
- `/root/verify-rust-std-evidence-brief` — explicit TASK.md protected path.
- `/root/verify-rust-std-kani3300-g0` — explicit TASK.md protected path.
- `/root/verify-rust-std-kani3300-sel1-swap` — common-dir owner with linked worktrees.

## Findings and limits

- There are 19 common Git directories. Owners with linked worktrees are protected because deleting an owner breaks dependent worktrees.
- Local branches belong to a common repository. The task requires publication of every local branch tip, so one unpublished shared branch blocks SAFE_DELETE for all its working copies.
- Protected upstream head branches were resolved from live GitHub PR metadata for kani#5172, #5176, #5210, verify-rust-std#752 and diffblue/cbmc#9487. The explicit #5206 path and copies named for protected upstream work are retained.
- Publication uses all GitHub refs returned by git ls-remote, including PR refs. Equality has a recorded tip; ancestry is accepted only after merge-base --is-ancestor succeeds against a tip object already present locally. No fetch was used.
- The initial read-only pass failed on a script input-encoding error. The final tips snapshot was reacquired once per repository and reused across all working copies; no per-directory remote queries were made.
- Review-named worktrees resolve their repository family from the common-dir owner. A missing local publication witness is UNPUBLISHED (UNKNOWN on query/inspection errors); this does not prove GitHub lacks the commit.
- Recent references were searched by literal absolute path (including descendants) or current branch with token boundaries in 3505 source files (g0 research modified within three days plus TODO.md). Inventory outputs were excluded to avoid self-reference.
- 136 raw/log/archive files were excluded from content search under Evidence Brief policy. No raw evidence content was read. All four source patches over 8 MiB were searched with rg; no source-size search cap remains.
- Untracked files are counted individually; up to ten result-like and ten uncertain names are recorded. Result-like or unknown untracked material remains ASK.
- All protected Ozon entries received only minimal structural metadata, directory mtime and du. Explicit protected paths that are not direct Git working copies are outside this inventory and remain protected.
- No files were removed and no disk space was reclaimed in this stage.

- Concurrent g0 commit 94dac9c1a17539ab8b975da71bb541139f7aac4e added research/challenge-8/kani-k1/item2-status-report-20261120/TASK.md during inventory. It is preserved. Results will be committed on top; this inventory does not rewrite concurrent work. Per-directory Git fields are point-in-time observations, with separate closeout rechecks for all SAFE_DELETE entries.

## Removal by coordinator — 2026-11-20 (owner approved)

Coordinator re-classified linked worktrees: removing a linked worktree keeps its branches and objects in the common repository, so unpublished shared branches do not block it. Criteria: clean porcelain status, no process/tmux cwd, no reference in documents of the last 3 days, age ≥ 2 days, detached HEAD reachable from a local branch, ignored files only `__pycache__`. Excluded for non-cache ignored content: `kani-fix-3300-c2-slices-w15`, `verifast-mdnew-clean`, `verify-rust-std-select-night`.
Removed 82 linked worktrees with `git worktree remove` (no `--force`, 0 failures; list in `REMOVAL-LOG.json`) and the two SAFE_DELETE clones with `rm -rf`. Free space 5.1 GB → 8.1 GB.
