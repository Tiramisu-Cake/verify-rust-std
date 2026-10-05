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

## Hard rule: no verification or builds on the user's server

The server is an editing and orchestration machine only. All compilation,
verification and executable tests must run on GitHub-hosted Actions runners.
Never run Kani, CBMC, VeriFast, Cargo builds/checks/tests, rustc, bootstrap/x.py,
the research run scripts, scripts/run-kani.sh, or a container/remote subprocess
that performs those tasks on the user's server. Do not install verifier/build
dependencies there. This prohibition also applies to "quick" compile checks.
Never configure this server as a self-hosted Actions runner.

Local reading, editing, git/gh operations, downloading/reading Actions evidence,
git diff --check, bash -n and lightweight non-executing document/YAML parsing
are allowed. A GitHub access failure is not permission to run locally.

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
