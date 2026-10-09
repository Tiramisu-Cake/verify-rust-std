## Accepted work policy — owner decision 2026-10-09

Read [WORK-POLICY](research/challenge-8/WORK-POLICY.md) and
[COMPLETION-PLAN](research/challenge-8/COMPLETION-PLAN.md) before new experiments.
They govern scope, priorities, evidence replay and the narrow permission for
small isolated local classifier/parser tests. This explicitly supersedes older
blanket bans on executable tests and any requirement to rebuild the verifier
for a classifier-only change. Compiler/verifier/proof execution remains Cloud-only.

Use the current assigned worktree/branch and authorized phase, not an old branch
name or workflow example below. Research Actions dispatch is not authorized by
historical instructions. Keep two project-wide queued/running/unresolved Cloud
Builds at most, one per stable owner/ledger; preserve the v2 coordinator protocol.
Sessions last two hours, with up to 30 minutes only to finish the current step
and checkpoint; the assignment supplies the Cloud budget. This policy adds none.

Fetch and integrate these documentation updates at the next safe step or before
the next session. Record the policy revision read. Do not interrupt a useful
running build or change its pinned inputs. No proof status is upgraded by docs.

# Instructions for coding agents

## Project and first reads

This fork is Igor's original Challenge 8 (SmallSort) verification project.
Read these before making changes:
1. research/challenge-8/AGENT-RUNBOOK.md (handoff, workflow commands, next steps).
2. research/challenge-8/README.md and insertion-contract.md (evidence and scope).
3. doc/src/challenges/0008-smallsort.md and doc/src/general-rules.md.
4. library/core/src/slice/sort/shared/smallsort.rs and the relevant proof/runner files.

Work in Tiramisu-Cake/verify-rust-std on challenge-8/research. Check the actual
working tree, remotes, branch heads and Actions runs first; handoff status is dated.
Preserve unrelated user changes. Do not force-push or reset away local work.
Use explicit repository arguments for GitHub commands to avoid targeting upstream.

## User authorization and autonomy

The user has explicitly authorized the agent to implement our proofs, fix failures,
commit and push its changes to the fork's research branch, dispatch the research
workflow on GitHub, wait and inspect results, and iterate without asking the user
to click Run workflow or approve each routine step. After a successful milestone,
continue to the next step in the plan; do not stop merely to offer to continue.

Keep workflows manually dispatched; do not add push, pull_request or scheduled
triggers for these experiments. "Manual" describes the trigger type: the agent
must dispatch it itself. Run one relevant experiment at a time, inspect its result,
then decide the next change. Do not queue speculative duplicate jobs.
Do not publish an upstream PR, post comments to others, or submit a bounty claim
without a separate user instruction.

## Execution boundary and local service-test exception

All compilation and proof verification run in authorized Cloud Build lanes.
Never run Kani, CBMC, VeriFast, Cargo builds/checks/tests, rustc, bootstrap/x.py,
proof runners/extractors or equivalent container/subprocess tasks on the VPS.
Do not install build/verifier dependencies or use a self-hosted runner.

Local reading/editing, Git operations, evidence reading/hashing, syntax and
non-executing parsing remain allowed. WORK-POLICY section 4 additionally permits
small isolated executable classifier/parser tests on saved or synthetic data.
Inspect imports/entrypoints first; do not execute proof toolchains or modify live
evidence/coordinator state. This exception is not permission for local proof work.
An access failure does not expand these permissions.

## Proof integrity

Develop our own specifications and proofs. Existing PRs may inform requirements,
review concerns and performance observations; do not copy their proof code.
Verify the actual standard-library code from this repository. Do not change its
runtime behavior, algorithms or generic signatures to make a proof pass.
Keep experiments under research/challenge-8; runners inject cfg(kani) modules
only in disposable Actions checkouts. Never commit injected copies or build output.

A bounded i32 experiment is a milestone, not completion of Challenge 8. The
challenge requires arbitrary valid slice lengths, all seven safety targets,
and functional contracts for all three small_sort implementations.
Track generic ownership, comparator behavior/unwinding, specialization and the
required UB checks explicitly, including uninitialized reads.

Keep safety assumptions separate from functional sortedness/order assumptions.
Do not silently shrink domains, disable checks, remove failing assertions/covers,
or use unverified stubs to obtain green results. Verified summaries require a
successful proof of the actual callee at the same source version. Inspect
harness counts, covers and unwinding assertions, not just the Actions badge.
Retain the pinned verifier unless a documented experiment justifies changing it.

## Evidence and continuity

Follow the dispatch-and-monitor loop in AGENT-RUNBOOK.md. After source changes,
dispatch a NEW run for the pushed commit; rerunning an old run checks old code.
Record run ID/URL, source SHA, selection, tool pin, assumptions, outcome, covers,
verification time versus cold build time, and the next concrete step in the
research notes. Update the runbook's current status after each meaningful result.
Documentation-only updates need no additional verification run.

Wait and poll within the active session; do not tell the user to check later.
Keep concise progress updates in Russian. If context/session limits interrupt
work, save and push a checkpoint with any active run ID and exact next action.
Do not promise unattended work after the session has ended.
Stop only for a real blocker such as missing authentication, required permissions,
an unresolved material decision or an enforced platform limit. Report the exact
blocker and smallest user action needed; keep the ban on local execution intact.

