## Cloud Build concurrency — owner update 2026-10-09

Use at most two project-wide queued/running/unresolved builds, at most one per
stable agent owner and ledger. Follow [the two-slot protocol and transition](research/challenge-8/cloud-build/PARALLEL-BUILDS.md).
This supersedes shared single-slot and turn-alternation instructions in older
phase documents. Preserve all existing budgets, deadlines and proof scopes.

## Permanent execution boundary

For SmallSort verification, builds, executable tests, source extraction and
evidence packaging, Cloud Build is the permanent execution provider. GitHub is
used for source history, branches, pull requests and documentation. Do not
dispatch or rerun GitHub Actions for research or heavy checks without a direct
owner instruction naming that action. Existing automatic repository workflows
remain configured and can still fire under their recorded event filters; this
policy does not alter or disable those triggers. See the unchanged inventory in
[GitHub triggers](research/challenge-8/cloud-build/GITHUB-TRIGGERS.md).

The VPS edits, publishes, orchestrates Cloud Build, and reads/hashes evidence
only. All compilation, verification and executable tests run in the authorized
Cloud Build environment. Use credential-free pinned Git-object source delivery;
never transfer GitHub credentials or use the working tree/configuration/hooks
as build input. The archive contains committed objects only and restores the
original commit/tree/blob identities without creating a commit.

## Completed phase: CLOUD-BUILD-MIGRATION

The owner authorized the A/B/C migration checks in existing
`smallsort-ci/global`; this phase has its own remaining-build budget and only
the reviewed stock/constructor lanes. See [phase](research/challenge-8/cloud-build/PHASE.md)
and [commands](research/challenge-8/cloud-build/README.md). Use explicit gcloud
configuration/account/project and region where applicable. No fake GitHub
identity. One queued/running build. Semantic profiles/contracts frozen; do not
expand the lanes or begin actual-callee proof work. A/B/C are accepted in the
[reported scope](research/challenge-8/cloud-build/ACCEPTANCE.md); this phase is
complete and does not authorize further proof development. Older GitHub procedures
below are historical and require a direct owner instruction before use.

# Instructions for coding agents

## Project and first reads

This fork is Igor's original Challenge 8 (SmallSort) verification project.
Before acting, read:

1. [Current status and phase](research/challenge-8/STATUS.md).
2. [Approved roadmap](research/challenge-8/PLAN.md), the phase document linked
   from STATUS, and the [operating runbook](research/challenge-8/AGENT-RUNBOOK.md).
3. [Research index](research/challenge-8/README.md),
   [Challenge requirements](doc/src/challenges/0008-smallsort.md) and
   [general rules](doc/src/general-rules.md).
4. The actual SmallSort source, relevant specification and proof/runner files
   for the authorized task.

Work in `Tiramisu-Cake/verify-rust-std` on the branch named in STATUS
(current migration checkpoint: `research/cloud-build-migration`). Inspect the
working tree, remotes, branch heads and Cloud Build ledger; recorded status is
dated.
Preserve unrelated user changes. No force-push or destructive reset. Always use
explicit repository arguments so GitHub commands cannot target upstream.

## Authorization: autonomous within an agreed phase

The user's latest instruction takes precedence. `STATUS.md` is the single
current checkpoint; dated handoffs, reassessments and archived "next" instructions
are historical evidence, not standing authorization.

An explicit stop remains in force until the user resumes experiments or
explicitly approves a named next phase. A status check, documentation edit or
approval of operating rules alone is not that authorization. When STATUS records
a named phase as READY/approved, a continuation request can start that phase
without repeating the approval. Historical closed phases remain closed.
While paused, do only the requested read-only/documentation work: no proof
implementation, verifier changes or build submission.

After authorization, autonomously edit, commit, push, submit Cloud Build,
inspect and iterate WITHIN the phase and tool-profile allowlist linked from
`STATUS.md`. GitHub Actions remain outside this autonomy and need direct owner
instruction.
Do not ask the owner to click Run workflow or inspect routine failures.
A green fixture permits the next already-agreed step, not a new architecture,
tool extension or phase. At a phase boundary, unresolved material decision or
new trust requirement, checkpoint and ask the owner before expanding scope.

One relevant Cloud Build per agent owner, at most two across the project. Use only reviewed lanes and no speculative
jobs or duplicate submissions. Do not dispatch GitHub Actions without direct
owner instruction. Do not modify existing workflow triggers under this policy;
their current automatic filters are listed in
[GitHub triggers](research/challenge-8/cloud-build/GITHUB-TRIGGERS.md). No
upstream PR, external comments, tool application or bounty submission without
separate user authorization.

## Hard rule: no verification or builds on the user's server

The VPS is an editing and orchestration machine only. ALL compilation,
verification and executable tests run in the authorized Cloud Build environment
for SmallSort.
Never run Kani, CBMC, VeriFast, Cargo builds/checks/tests, rustc, bootstrap/x.py,
research runners/extractors, scripts/run-kani.sh, or containers/remote subprocesses
that perform these tasks on the VPS. Do not install build/verifier dependencies
there or run a "quick" compile check. Use only the authorized Cloud Build
configuration; no self-hosted runner.

Local reading/editing, git/gh operations and downloading/reading authorized
Cloud Build evidence,
`git diff --check`, `bash -n` and lightweight non-executing document/YAML parsing
are allowed. GitHub failure is not permission to verify locally.

## Frozen trust boundary and proof integrity

Develop our own specifications/proofs; do not import other solutions' proof code.
Verify the actual repository std source without changing its runtime behavior,
algorithms or generic signatures. Keep experiments under `research/challenge-8`;
injection/exact-source extraction happens only in disposable Cloud Build
checkouts.
Do not commit generated/injected source, downloaded logs or build output.

Verifier pins, parser/translator semantics, kernel, memory/alias model, prelude
and refinement checker are frozen at the phase's explicitly named profile.
Existing experimental patches are NOT a blanket license to use or extend them.
New semantic changes or a different patch chain require a separate decision,
written rationale, trust/admissibility review and an explicit regression gate
BEFORE implementation. A "kernel-free", "frontend-only" or proof-only AST rewrite
still changes trusted semantics and is subject to this rule.

Before each experiment, record the actual std obligation, a falsifiable
hypothesis, exact domain and full target normal/unwind posts, tool profile,
expected positive/negative stage/predicate/location, and outcome-to-next-decision
mapping. Distinguish a deliberately partial diagnostic from the target contract.
Repeated failures without new evidence require reassessment, not more patches.

Do not obtain green results by weakening posts, deleting resources/assertions/
covers, adding Freeze/Copy/purity restrictions to unrestricted safety, assuming an
ownership bridge, hiding unsupported cases or disabling unwind, leak, dead-code,
uninitialized/validity or refinement checks. Safety and ordering premises are
separate. A pointer rewrite must preserve provenance/permissions and applicability
to the actual source; satisfying the refiner alone is not justification.

Verify an actual callee at the same source version before using its summary.
Isolate fixtures so an unrelated new helper cannot block baseline controls.
A negative counts only at its intended proof obligation; setup, frontend,
unsupported-operation and unrelated helper failures are not intended negatives.
Green microfixtures or regression counts prove neither a whole std function nor
the soundness/admissibility of a patched verifier. Inspect full logs and artifacts.

## Evidence and continuity

Follow the runbook's exact-SHA Cloud Build submit/monitor loop. A changed source
requires a NEW build; rerunning an old build checks old code. After meaningful
results, update the compact `STATUS.md`, append evidence to `EXPERIMENT-LOG.md`,
and update `coverage.md`/the relevant design note when their claims change. Keep operating
instructions free of chronological run logs. Preserve failures, source/run/tool
identifiers and historical evidence; a documentation commit is not a proof run.

During an active authorized session, poll the specific run and continue routine
within-phase work; do not offload monitoring to the owner. Report concisely in
Russian. On stop or session limits, save a checkpoint with exact state, active
run ID (if any), draft status and the next permitted action. Do not promise work
after the session ends. Documentation-only changes require no verification run.
