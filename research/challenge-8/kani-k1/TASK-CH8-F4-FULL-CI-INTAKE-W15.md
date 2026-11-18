# W15 — F4 push CI intake and upstream PR draft

PREPARED_NOT_ISSUED. Coordinator issues to fresh15/current model+Fast only after
all three run IDs below are terminal. Owner has authorized this intake and draft;
terminal failure still requires intake, not a retry. No subagents. STOP only for a
real blocker, not volume/context; unavailable fields remain UNKNOWN. Correctness
verification, not security work. Keep this stage compact.

Worktree `/root/verify-rust-std-kani3300-g0`; paths below relative to
`research/challenge-8/kani-k1/`. Read `STYLE-UPSTREAM-RULES.md` before writing text.

## Exact inputs and scope decision

- Final published Kani head `b5a9678fd7c2a0f67c3fcafd90057fc2afaf9b5d`, branch
  `fix/per-harness-global-transforms`, tree `8585336ed35a14fe0fc157a7ca4e0d52075c0e49`,
  direct parent/upstream main `faffcee3bca2770c03bd21c3bde89cc8f6f7a14e`, no skip
  directive. Same reviewed tree as `cab66681c912a3e5ee01a106faaeee5237ca0232`;
  original source worktree `/root/kani-f4-fix-w15` may remain on cab: inspect Git
  objects, do not switch branches or edit source.
- Source package `7485bbb27a72dd463d4a9628c8627689d30e7e56`, source review
  `cbfd888f274a0666f09af79d98ef4b8b8061f497`, plan package
  `9743a4a1d073e5c1591a1a20ab4756140241d57e`, plan review
  `4d79ed98f46d3d89feb25509cffa0704a0398cad` APPROVE/F4-R14-1 CLOSED,
  GO request `45726b201a5186fb2dfe3cafdc17a2aef1bb6cc1` remain immutable.
- Main confirmation intake `06ff67af4aa1dd8df2cdbf2eec58bf3863008748`, run
  `44177926794`: DEFECT_PRESENT for the compact fixture. Both cfg variants are
  distinct from actual compilation order; runtime cache causality remains UNKNOWN.
- Owner/coordinator explicitly changed execution scope after GO preparation:
  fork **push** workflows only, as for F3/#5184. No fork PR against unsynchronized
  fork main. PR-only release.yml, verify-std-check.yml and bench-pr.yml, including
  release's 14 instances and labeled benchmark comparisons, are DEFERRED_TO_UPSTREAM_PR,
  not executed/passed/waived by this intake. extra_jobs is PR metadata-only too.
  This decision supersedes the seven-workflow prerequisite for the fork attempt;
  it does not rewrite the approved plan/review or establish upstream PR results.
- Ledger reservation `1ab634309d79b98bb32e09129dba2f1c9e71f64d`, run record
  `73ffdca390ef753fa4ac2118c4480c6844af3dd3`: item1 **28/28**, item2 **10/14**,
  total **38/42**. Reference only; do not charge/refund/reserve/change anything.

## Intake

1. Confirm terminal Tiramisu-Cake/kani metadata, event=push, exact final head/ref,
   expected attempt1, actual workflow versions and native run conclusions:
   Kani CI `44274306776` (.github/workflows/kani.yml),
   Format `44274306711` (format-check.yml), Deny `44274306733` (deny.yml).
   Preserve unexpected attempts/identity mismatches as findings, never substitute.
2. Read complete bounded run/job/step/check summaries and available compact
   structured reports through connected tools/reporting interfaces. Keep provenance,
   URLs, snapshot times and available digests. No full/raw logs or archives, local
   raw copies, GCS/Cloud Logging bypass or compiler/verifier/full runner. If a
   failure/checkout/test detail is unavailable, state exact missing evidence for
   coordinator; do not infer a cause or request a new run yourself.
3. Derive required job/matrix inventory from frozen native workflows: all five
   regression OSes, benchcomp-tests, full perf, LLBC, documentation, format/clippy,
   audit and their actual conditions. Preserve each native outcome, failure,
   cancellation, skip, continue-on-error and partial coverage. Publication-only
   documentation skip is distinct from a missing required candidate job. Record
   actual checkout identity where reported; head metadata/expected source behavior
   alone is not a measured checkout. No PR merge-tree substitution is involved.
4. Establish what the delayed-shared-body regression actually ran and reported;
   bind available results to exact head/source and native script-based-pre suite.
   Keep main observed failure vs fixed execution separate from synthetic expectations.
   Aggregate green status alone is not an invented per-harness property inventory.
   Preserve initialized singleton/paired and intended unsafe controls and both cfg
   variants when exposed; missing details remain UNKNOWN. No repeated compiler audit.
5. Report first retained meaningful failed step/reason and classification:
   FORK_PUSH_CI_PASS, FORK_PUSH_CI_FAILED or INCONCLUSIVE. Every required job must
   be accounted for. Do not declare a dependency/baseline issue harmless without
   evidence; do not fix source/CI, rerun or alter native conclusions. Measured perf
   only; separate compiler/PR benchmark comparisons remain deferred.

## Draft and delivery

Write only `kani3300/wave0/f4-fix-ci-intake/head-b5a9678fd7/`: compact RESULT.json/md,
INPUTS/PROVENANCE/MANIFEST, HANDOFF.md and PR-DRAFT.md (reuse structured data, no
new parser/test framework). Immutable source/packages/reviews/old evidence/ledger.

PR draft follows STYLE-UPSTREAM-RULES exactly: two short paragraphs, first sentence
reproducible via cargo kani -Z uninit-checks, upstream terminology, actual main vs
fixed test behavior, short Testing with at most one run link, standard Apache/MIT
license sentence and required AI disclosure. No head/parent SHAs, test counters,
internal F4/receipt/proof labels or invented compilation-order/cache causality.
Testing must truthfully reflect failures/UNKNOWN and deferred upstream PR checks;
do not write fixed PASS/green standard CI if evidence is missing or red. Mark draft
readiness separately from CI readiness. Use old PR-DRAFT only as prose input.

No CI/push/PR/publication/labels/events/rerun/cancel/reservation/ledger/budget or
source changes. Publication requires owner command. S2/S3 outside scope.
Stage exact own paths, commit --only, `[skip ci]`, author
Tiramisu-Cake <igkharin@gmail.com>. Final `READY <full g0 SHA> <classification>`
and one compact handoff: observed results, remaining evidence, draft readiness.
