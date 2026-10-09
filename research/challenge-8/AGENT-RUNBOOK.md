## Current Cloud Build execution procedure

The permanent SmallSort execution provider is existing Cloud Build.
[Phase](cloud-build/PHASE.md),
[commands](cloud-build/README.md), [new ledger](cloud-build/BUDGET.json).
At most two project-wide queued/running/unresolved builds, one per agent owner
and ledger. Follow the [two-slot transition](cloud-build/PARALLEL-BUILDS.md);
this supersedes older shared single-slot and turn-alternation rules without
changing any phase deadline or budget. Exact published infrastructure and proof SHAs,
no-source pinned-object submission, unique BuildID bucketprefix, upload before
final verdict.
Use every gcloud invocation with explicit configuration/account/project and
region if applicable; no credentials inspection or administrative changes.
VPS static/edit/orchestration only. Historical Actions loop below does not
authorize Actions runs. Actual-proof work still requires its separate phase
authorization.

# Challenge 8 operating runbook

This is an operating procedure, not a progress log. Read [AGENTS.md](../../AGENTS.md)
and [STATUS.md](STATUS.md) first, followed by [PLAN.md](PLAN.md) and the phase
document linked from STATUS. The current authorization state and phase there
override historical instructions. The pre-reorganization runbook is preserved
verbatim in [the archive](AGENT-RUNBOOK-ARCHIVE-2026-10-06.md).

## Permanent execution policy

SmallSort CI, compilation, proof runners, source extraction and executable
checks use Cloud Build permanently. GitHub is the source/branch/pull-request/
documentation host. Do not dispatch or rerun GitHub Actions for proof or heavy
checks without direct owner instruction. Existing repository Actions triggers
are unchanged and may still run automatically; their exact current filters are
listed in [GITHUB-TRIGGERS.md](cloud-build/GITHUB-TRIGGERS.md). This policy
does not alter those workflow files.

The VPS may edit, hash committed inputs, publish source, orchestrate Cloud Build,
and read/verify evidence. Cloud input uses the approved credential-free pinned
Git-object archive: the original commits, trees, blobs, modes and selected file
bytes are verified on restore; no working-tree, index, Git configuration, hook
or GitHub credential enters the archive. The resulting partial repositories
retain their original commit IDs and do not fabricate commits. Cloud restoration
was validated by the accepted B/C builds linked from STATUS; preserve their
original SHA and profile scope when repeating a reviewed lane. The historical
GitHub dispatch procedure below is retained for audit context only and is not
current authorization.

## Working context

- Fork: `Tiramisu-Cake/verify-rust-std`; migration branch:
  `research/cloud-build-migration`. Historical research branch:
  `challenge-8/research`; always read STATUS for the active checkpoint.
- Upstream: `model-checking/verify-rust-std`; no external publication authorized.
- Source: `library/core/src/slice/sort/shared/smallsort.rs`.
- Historical workflow: `.github/workflows/smallsort-research.yml`; no current
  Actions dispatch is authorized by its presence.
- Requirements: [Challenge 8](../../doc/src/challenges/0008-smallsort.md) and
  [general rules](../../doc/src/general-rules.md).
- Current evidence: [STATUS.md](STATUS.md), [coverage](coverage.md),
  [experiment log](EXPERIMENT-LOG.md). Topic notes are indexed in [README](README.md).

The VPS only edits/orchestrates. No compiler, verifier, executable tests,
extractors, research runners or build dependencies there, including containers.
GitHub is used for source and review operations; non-executing static checks are
allowed locally. Proof work runs only in Cloud Build.

## Historical GitHub session procedure (not current execution authorization)

The following Actions-specific commands are preserved as historical procedure.
Do not use them unless the owner directly orders a GitHub Actions run.

Inspect local changes, remotes, current branch, remote heads and active research
runs before acting. Preserve user changes. In a clean clone with the fork as origin:

~~~bash
git status --short
git remote -v
git fetch origin
git switch challenge-8/research
git pull --ff-only origin challenge-8/research
gh auth status
~~~

Create a tracking branch if absent; do not blindly change an existing remote.
Check push AND workflow-dispatch access without exposing credentials. Use an
already authorized equivalent GitHub client if needed; otherwise ask for missing
access. Never replace unavailable Actions with server-side verification.

If STATUS is paused, a request to inspect/edit docs alone does not resume
experiments. Explicit owner approval of a named next phase is authorization:
record the instruction and boundary in STATUS before proof edits or dispatch.
If that approval is already recorded as READY, a continuation agent starts the
named phase without requesting the same permission again. A documentation-only
approval checkpoint need not dispatch a run. A stop cancels authorization for
further implementation/dispatch; identify any running job and report its state.
Save a minimal checkpoint when permitted; never apply an unfinished draft as part
of "checkpointing". This runbook is not a daemon or permission to work after stop.

## Experiment card: prepare before implementation/dispatch

Append a compact card to EXPERIMENT-LOG; keep only its current decision in STATUS:

- Actual std source path/function and the obligation this experiment advances.
- One falsifiable hypothesis; why the latest evidence supports testing it.
- Exact input domain, resources, safety premises and full normal/unwind target
  posts; distinguish a deliberately partial fixture from the final contract.
- Allowed Cloud Build lane, tool/pin/patch profile and hashes; any unresolved trust/admissibility
  assumptions. Do not quietly add a patch to the chain.
- Cases: positive outcomes and each negative's expected stage, predicate and
  source location. Baseline controls must not import an unrelated failing helper.
- Acceptance evidence: actual helper/callee/caller bodies, source/ghost-strip,
  MIR/AST, refinement, leak/unwind and relevant covers/UB checks.
- Decision for each plausible outcome: routine within-phase fix, advance to an
  already agreed step, or STOP for a new semantic/trust/architecture decision.
- Exact lane/timeout selection, total budget and stop boundary.

For a memory-safety claim, retain unrestricted target types/comparator behavior;
state ordering assumptions separately. Match pointer provenance and ownership,
not just equal numeric addresses. A compiler, refiner or unrelated helper failure
does not test the intended resource hypothesis.

## Historical GitHub edit → push → dispatch → inspect loop

Use this loop only for the recorded approved phase. On beginning a READY phase,
record IN PROGRESS and the selected within-phase step in STATUS.

1. Make the smallest evidence-backed change within its allowlist. Inspect the
   diff; use only allowed static checks locally. Do not run proof scripts.
2. Commit intended files and push normally. Confirm the remote matches the full
   source SHA before dispatch:

~~~bash
git push origin HEAD:refs/heads/challenge-8/research
git rev-parse HEAD
git ls-remote origin refs/heads/challenge-8/research
~~~

3. List relevant runs before dispatch. Monitor an applicable active run instead
   of duplicating it; record the existing IDs and time:

~~~bash
gh run list --repo Tiramisu-Cake/verify-rust-std \
  --workflow smallsort-research.yml --branch challenge-8/research \
  --event workflow_dispatch --limit 20 \
  --json databaseId,url,headSha,headBranch,status,conclusion,createdAt
~~~

4. Set `proof_selection` and `budget_minutes` from the authorized experiment
   card, not an old example or the workflow's default. These are placeholders,
   not instructions to run the historical bootstrap:

~~~bash
gh workflow run smallsort-research.yml \
  --repo Tiramisu-Cake/verify-rust-std --ref challenge-8/research \
  -f proof="$proof_selection" -f budget_minutes="$budget_minutes"
~~~

5. Resolve the new run by workflow, branch, event, full head SHA, creation time
   and logged selection. Do not blindly select the latest repository run. If
   listing is delayed, poll; do not dispatch a duplicate. Record its ID/URL.
   Do not push another proof change before resolving this dispatch to its SHA.
6. Poll that specific run roughly once a minute with short waits and progress
   updates. Do not stop merely because it is queued/building. After completion
   read the full log and artifacts, including successful runs:

~~~bash
gh run view "$run_id" --repo Tiramisu-Cake/verify-rust-std \
  --json databaseId,url,headSha,headBranch,status,conclusion,jobs
gh run view "$run_id" --repo Tiramisu-Cake/verify-rust-std --log
gh run download "$run_id" --repo Tiramisu-Cake/verify-rust-std \
  --dir "/tmp/challenge8-evidence-$run_id"
~~~

`run_id` must be the resolved ID. Download into a fresh directory and never
commit archives, generated source or large logs. Artifacts expire after seven
days; preserve essential diagnostics and identifiers in the committed record.

7. Check source/tool/profile hashes, requested case counts, actual named body
   execution, normal/unwind posts, intended negative diagnostics, covers and
   unwinding assertions, refinement and whole-unit exit codes. Trace duplicates
   and a green badge are not proof. Record "not run" separately from "passed".
8. Classify the FIRST causal failure: setup/build; frontend/export/decode;
   unsupported operation; resource/postcondition proof; refinement; timeout/OOM;
   infrastructure. Fix only within the existing phase and frozen trust boundary.
   A new semantic change or insufficient source applicability requires STOP.
9. After source edits, dispatch a NEW exact-SHA run. An old-run rerun checks the
   old commit. On success, advance only to the next agreed within-phase step.
   At the phase boundary checkpoint and seek the owner's next decision.

Default total budget is 90 minutes, including setup/build; supported choices
are 30/60/90/120. A retry at 120 is justified only by a measured budget bottleneck
within the authorized phase. Keep `--jobs 1` for the initial Kani experiments.
No blind unchanged retries, speculative jobs, self-hosted or paid-compute fallback.

## Workflow and checkpoint discipline

The current execution trigger is the explicit Cloud Build submission described
in [cloud-build/README.md](cloud-build/README.md). New selections must remain
inside the authorized phase; semantic tool changes require a separate decision.
Do not change GitHub workflow triggers or dispatch Actions without a direct
owner instruction. The existing automatic events are documented in
[GITHUB-TRIGGERS.md](cloud-build/GITHUB-TRIGGERS.md). Never merge/fast-forward
research history into main just to expose a choice.

After each meaningful result, update STATUS's latest run, evidence boundary,
blocker and permitted next action; append the full result to EXPERIMENT-LOG.
Record source SHA, run ID/URL, selection/budget, tool/patch hashes, domain/posts,
case/cover/check outcomes and cost (verification versus setup, time/RSS).
Update coverage/design claims when they change. Preserve historical failures.
Do not add another chronological handoff block to this runbook.

Documentation-only changes need static review, not a cold verification run.
On interruption record any active run and unapplied drafts without overstating
what was verified. Stopped experiments resume only by explicit owner instruction.
