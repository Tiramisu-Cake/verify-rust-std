# worker13 — one-stage handoff

Scope: TASK-CH8-S1K-HOST-W13.md, g0 input ea3cec4078a2b1598d4d4f5d3bd62db9c1a13dde.

Kani worktree `/root/kani-ch8-s1k-w13`, branch `uninit-ci/ch8-s1k-w13`.
Control `36db70978a16144624abf94d480a593dae684451`, tree `f3d36d51f58bf7937f6f8778260e3e2816996b48`, sole parent `0aac16ef62da9e9d5645782d458593e5d78143ba`.
Exact export std `75a4d1ea6eb60c63c27c1b18e662740d93bafb08`; unchanged upstream tool `0aac16ef62da9e9d5645782d458593e5d78143ba`.

`CI-REQUEST.md` and `.json` contain the request and manifest identity. `MANIFEST.sha256` covers all control payload files including in-control CI-REQUEST. `BATCH-IDENTITY.json` records equality with f88bf3f0ea. `VALIDATION.json` gives checks and reproduction commands. `REVIEW.md` contains the independent Luna High decision for the committed candidate; packet/spec are retained alongside it.

All original 23 rows/oracles/caps/flags and runner bytes preserved. Stock Kani workflows removed in the control commit. Tests cover new host checks plus existing runner and wrapper error paths. No algorithm, production source, tool, premise or proof scope changed.

Both stage commits use the requested author and `[skip ci]`. No push, CI, publication or ledger operations. All actual proof rows NOT_RUN, no proof credit. Preparation is complete after review; no further stage is authorized here.

Next coordinator action: assess the contingency against any std-host run, obtain dispatch authorization and activate at most one host. The current `[skip ci]` message suppresses a push run. To activate, coordinator must create and record a separately authorized same-tree sibling commit without that marker and with the same sole tool parent; a child commit violates the parent check. No activation or duplicate cancellation was performed in this stage.
