# Same independent11 — combined W11-01 + new-main delta review

PREPARED: root supplies exact committed main-r2 package/source/main pins.
Read TASK-KANI-4591-MAIN-REBASE-W15.md. Prior review54ea8a918b761dc67213f7f24ae5163b7f463b42
REQUEST_CHANGES W11-01; unreviewed intermediate r1g01d7ef5455f2ea790cd98dde9f38565edb59357ea
sourcee6aa remains immutable. This single review must close W11-01 AND examine
transfer to main969f4648980a8e66cd0ca32fd3e714a55ac32cef/treec9a832dc1647c51ac3036429e5f97e73eb717ba7,
whose soleparent is oldmainfaff. No broad unrelated compiler reaudit.
Check provider exact FnDef reachable in each affected PFC harness; direct call
positive while copied-body call has intended negative; no masked failing direct
call, no weakened reachability, no compile-error oracle substitution. Inspect
all affected source routing and new-main contracts/attributes/toolchain API
changes, actual patch conflict/resolution/semantic invariance. Preserve ordinary,
verified/PFC/unstubbed modes and replacement safety; no fake passing i32 issue
example. New native/typecheck/compiler tests NOT_RUN; oldfaff MRE not new-main credit.
Verify exact package/source/tree/sole969fparent/replays/manifest/oracles, native
push inventories against969f (all workflow/scripts/newtoolchain/lock unchanged),
future nonskip same-tree sibling/one-commit969f..final gate. Full native PUSH-CI
only, no research workflow/cron/enable/dispatch; PR-only scope deferred unchanged.
Own output `wave0/issue4591-fix-main-review-w11-r2/` immutable inputs/report/tests/
manifest/HANDOFF, W11-01 CLOSED or localized findings; never edit candidate.
Findings original15 immutable repair, same11nextdelta. ExactAPPROVE/no blockers
->root exactGO only; usercoordinator launches one full standard pushCI31/31.
PR/issues/comments/openPRpush publications owneronly. No compiler/cargo/rustc/
rustfmt/Kani/CBMC/expansion/verifier/fullrunner/CI/push/PR/issues/rawlogs/archives/
GCS/ledger/reservation/budget/subagents/model changes. Current high/FastOFF, STOP
only a real blocker, exact ownpaths [skip ci].
