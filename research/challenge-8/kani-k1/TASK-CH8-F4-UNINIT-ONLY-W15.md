# W15 — F4 clone only for enabled delayed UB instrumentation

ISSUED by coordinator after owner chose A and granted +1 item1 (cap29).
Correctness verification, not security work. Fresh /new, preserve current pane
model/service tier; owner is disabling Fast when panes become idle, do not toggle
it yourself. No subagents. STOP only real blocker, not volume/context.
Read STYLE-UPSTREAM-RULES.md. Paths from
`/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/`.

Exact published baseline head **b5a9678fd7c2a0f67c3fcafd90057fc2afaf9b5d**,
tree8585336ed35a14fe0fc157a7ca4e0d52075c0e49, parent/main
faffcee3bca2770c03bd21c3bde89cc8f6f7a14e. Same reviewed tree as cab66681c9;
source package7485bbb27a/reviewcbfd, plan9743/review4d79, prior CI intake
b560173271ffd7da13a5717caac0ad5f3b3219a5. Old head/packets/results immutable.
Old push Kani44274306776:8SUCCESS,macArmNO_RUNNER/NOT_RUN; FormatSUCCESS,
DenyEXTERNAL_ADVISORY, owner no rerun old macOS job. No all-green/five-OS claim.

Create isolated `/root/kani-f4-uninit-only-w15` from exact b5; preserve old source
worktree `/root/kani-f4-fix-w15` and published branch. New candidate parent **b5**.
Minimal compiler change: full BodyTransformation clone per harness only when
DelayedUbPass is enabled, using the **same effective predicate as is_enabled**:
`args.ub_check.contains(&ExtraChecks::Uninit)`. Otherwise pass the shared unit
transformer as on frozen main. Preserve warmed cache, passes/body modification
flags/loop metadata consistency and on-mode F4 isolation. DumpMirPass alone reads
MIR and does not require isolation; a nonempty global-pass list is not the guard.
Keep code small; no COW/cache-overlay refactor, pass disabling or unrelated reset.
No local compilation/cargo/rustc/Kani/CBMC/rustfmt/full runner.

Extend the existing single delayed-shared-body fixture/check.py to verify BOTH
modes, retaining both feature call-path variants and singleton/paired comparisons:
- With uninit-checks: initialized control succeeds alone/paired, delayed and
  independent unsafe controls still fail as intended; same semantic inventories.
- Without uninit-checks: shared-transformer path and ordinary checking behavior
  preserved; verify exact disabled feature/selection/native outcomes and initialized
  result, compare singleton/paired ordinary inventories. Do not carry the enabled
  mode's expected uninit failures into disabled mode or disable other checks.
  Derive precise ordinary expectations from source/API and label unexecuted results
  as expected, not observed baseline evidence. Keep the intended unsafe fixture.
No invented compilation order, fixed quotas, metrics or runtime PASS. Avoid
additional fixture directories/dependencies. Arg/env separation must prevent a
mode silently inheriting uninit-checks. Main-vs-fix regression remains valid.

Validation now: targeted Python oracle fixtures for both modes/feature-mismatch/
missing or partial results/unsafe controls, shell/AST/static checks, exact patch and
hash invariants. No compiler, verifier or full test runner. Actual two-mode native
runtime and performance remain NOT_RUN until the authorized new CI.

Write only g0 `kani3300/wave0/f4-uninit-only/`: source SHA/tree/parent, narrow delta
fromb5/full main patch, changed-file hashes, test/oracle/validation/provenance,
manifest, STYLE PR draft, CI-REQUEST and HANDOFF for14. All16 standard workflows,
scripts/library/toolchain/dependencies unchanged except the existing regression
test files needed here. Root separately edits `/root/smallsort-pr-drafts/PR-F4-DRAFT.md`;
do not edit that file. Explain cache prewarming is conditional on harness ordering;
avoid absolute claims that local transformations never recompute.

CI preparation: full native **push** suite on exact new final head: kani.yml all
jobs/matrices (including normal macOS entries), format-check.yml, deny.yml; unchanged
conditions/retries/continue-on-error. PR-only release/std/bench remain deferred to
upstream PR by owner. Old CI covers old head only. New final trigger/head must
match reviewed new tree and be a no-skip same-tree sibling with parentb5 (candidate
may use [skip ci]); don't push skipped candidate or include skip commits in the
pushed b5..HEAD range. Owner/coordinator creates/publishes head after review+GO.

After READY -> independent14 review -> root exact GO-request for one new full
push-CI bundle, prospective item1 **29/29**. Owner +1 authorizes cap, not dispatch
by this task. Current usage28/29,item2 provisional10/14,total38/43 reference;
r1S2 accounting remains owner-only. No CI/rerun/cancel/push/PR/labels/ledger/
reservation/budget action. Publication remains owner command.
Exact ownpaths commit --only, `[skip ci]`, Tiramisu-Cake <igkharin@gmail.com>.
Final `READY <full g0 SHA> <source SHA/tree/parent> <static validation>`.
