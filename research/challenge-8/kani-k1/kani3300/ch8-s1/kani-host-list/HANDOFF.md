# Worker13 — S1 list repair, one stage

Task `TASK-CH8-S1-LIST-W13.md`, g0 input `45498717e2d67a9e98aa5b6c1b398cc50f72f72c`.

Control `c03363b3b0a83fa9e78c4841720cb48ee7638c6a`, tree `8c51bd047ed6d3287572277eba23b28f458e7e87`, branch `uninit-ci/ch8-s1k-list-w13`, worktree `/root/kani-ch8-s1k-list-w13`. Sole parent stock tool `0aac16ef62da9e9d5645782d458593e5d78143ba`; std S′ remains `f22f84f316ad8ef6f3fccce86424bad927b09f78` / tree `e0dc89592926571e823797f8618cd6b4a7e11ff6`.

Option (a), justified by the source trace in DESIGN.md: standalone `list --std` builds/codegens every harness and offers no harness-filter option. List now has 1500 s, independently bound in the request. The same phase still starts before list and is capped at 4500 s. Job remains 120 min. All 23 literal rows, selectors, oracles, 600 s/root and 6 GiB caps are preserved; inventory binding and row validation functions are byte-identical. Plan metadata is updated from 300 s to 1500 s for list (rows estimate 2760 s). This does not establish that list or all proof rows will finish; existing phase/last-row reserve guards can stop trailing rows.

The runner writes atomic list receipts before execution, after process completion, and after inventory validation, including exit/timeout/signal/elapsed/sampled RSS and bounded stdout/stderr head+tail. Preflight/launch/invalid JSON/binding errors retain diagnostics. Fallback preserves completed receipts and labels interruption or missing execution UNKNOWN. Failed attempts cannot reuse an earlier frozen inventory.

`CI-REQUEST.json` records exact identities and manifest hash; `MANIFEST.sha256` covers all 8 control payload files. `STATIC-VALIDATION.json` records exact row/semantic-function/workflow comparisons. `VALIDATION.json` records 20 passing synthetic tests and static checks. The independent report and exact review packet are in `REVIEW.md` and `review-packet/`.

All commits use `[skip ci]` and author `Tiramisu-Cake <igkharin@gmail.com>`. No push, CI, publication, ledger, local cargo/rustc/Kani/CBMC, or raw-log operation was performed. Actual proof rows: ALL_23_NOT_RUN; obligations closed: 0; proof credit: NONE.

This stage prepares a reviewable control only. Coordinator may assess it for S1-03 in a later authorized stage; preparation neither reserves nor dispatches that run. An activation sibling, if separately authorized, must retain the exact tree and sole tool parent. No next execution stage is authorized here.
