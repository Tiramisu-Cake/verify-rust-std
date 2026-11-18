# Source trace: unchanged repaired delta on approved new main

Task09840da5715c0462ee09256930d8487712beebf3, current15/high/FastOFF,
no subagents or model changes. Approved upstream input is main 969f4648980a8e66cd0ca32fd3e714a55ac32cef,
tree c9a832dc1647c51ac3036429e5f97e73eb717ba7, sole parent faffcee3bca2770c03bd21c3bde89cc8f6f7a14e.
The new source is 3a770b5db51ba07acffce3483bde0901e6533f3a, tree 7a3d5c05b5d663d515c198b2bfa7c4926ae133ac, sole parent main969f.
SOURCE-PINS.json records exact object and file bindings.

The own repaired r1 patch is the implementation input. Frozen r1 g0
1d7ef5455f2ea790cd98dde9f38565edb59357ea, source e6aa083da3c93f3189039077795cc9a0d67d3a6d, tree 01140856c15e161ff6fc4c1ce460fd4208a298cd, and original
review54ea8a918b761dc67213f7f24ae5163b7f463b42 remain immutable.
SOURCE-TRACE-R1-FROZEN.md is a byte-identical historical copy of r1 source
analysis; its old-base drift gate and native observations are historical.
It is not relabeled as current-main evidence. NEWBASE-ANALYSIS.md covers the
relevant accepted upstream API/feature/toolchain changes explicitly.

The full repaired patch applied to a clean isolated main969f worktree without
conflicts, fuzz options, three-way resolution or manual edits. Additional
compiler adaptations: none. The final source has exactly three compiler and
eight fixture/oracle paths changed from new main, with 452 insertions and two
removals. TRANSFER.json records actual commands, exits and object identities;
RANGE-DIFF.txt compares the single old and new commits. Only the commit message
changes in that range diff. Removing only index blob-ID header lines makes the
old and new candidate diffs byte-identical, including hunk coordinates/content.
The same normalization makes old-main..new-main equal old-r1..new-source.
Thus every upstream content hunk survives the transfer.

The routing contract stays unchanged: FnStubPass reports only a validated
ordinary provider Instance, resets its per-body state and consumes it once.
BodyTransformation retains the requested cache identity and runs every pass.
Only FunctionWithContractPass chooses the validated body source for ordinary
Assert/Original cases. Explicit original PFC/verified selections keep their
requested instance and modes; provider selections use provider attributes and
closures. Recursive Check/Replace, closure errors, transitive/generic stubbing,
validation and replacement safety keep the repaired r1 behavior. Source pass
logic and tests have no additional semantic delta from r1.

W11-01 remains pending independent closure. Both repaired harnesses directly
call their selected provider in their own body before the copied f call.
The dedicated negative identity provider ensures result == 0: direct input 0
passes, copied input 1 fails that postcondition. All eight test/oracle files
are byte-identical to frozen repaired r1, including the i32 caller-overflow
reproducer and original controls. pfc_fixture_check.py supplies lexical and
mutation checks, not compiler FnDef or MIR evidence. W11-01-CLOSURE.md maps the
source repair to the original finding without claiming independent approval.

All31 upstream changed paths are inventoried. Every upstream path except the
contracts.rs file that also carries our unchanged hook has exactly the new-main
blob; its upstream feature-flag hunk is separately preserved by diff equality.
All16 workflow bytes, complete jobs/matrices, scripts/actions, library,
toolchain and dependency files retain new-main bytes. A fresh MAIN-CHECK.json
read-only lookup observes exactly the approved main969f, with no further drift.
No existing worktree/history/package/open PR or S3/tool0aac was modified.

The old native MRE/intake remains INCONCLUSIVE in its original faff scope.
It supplies no current969f main or fixed-candidate execution credit. Compiler,
cargo/rustc/rustfmt, expansion, Kani/CBMC, verifier/fullrunner, new native tests
and CI are NOT_RUN. Upstream commit-message testing statements are source
claims, not independently checked results here. The next gate is ONE same11
combined W11-01 + new-base delta review, then root exact GO; usercoordinator
alone launches the full standard push bundle, and owner alone publishes PR.
