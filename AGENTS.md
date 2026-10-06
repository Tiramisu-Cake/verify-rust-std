# Instructions for coding agents

## Project and first reads

This fork is Igor's original Challenge 8 (SmallSort) verification project.
Before acting, read:

1. [Current status and phase](research/challenge-8/STATUS.md).
2. [Operating runbook](research/challenge-8/AGENT-RUNBOOK.md) and
   [research index](research/challenge-8/README.md).
3. [Challenge requirements](doc/src/challenges/0008-smallsort.md) and
   [general rules](doc/src/general-rules.md).
4. The actual SmallSort source, relevant specification and proof/runner files
   for the authorized task.

Work in `Tiramisu-Cake/verify-rust-std` on `challenge-8/research`. Inspect the
working tree, remotes, branch heads and Actions runs; recorded status is dated.
Preserve unrelated user changes. No force-push or destructive reset. Always use
explicit repository arguments so GitHub commands cannot target upstream.

## Authorization: autonomous within an agreed phase

The user's latest instruction takes precedence. `STATUS.md` is the single
current checkpoint; dated handoffs, reassessments and archived "next" instructions
are historical evidence, not standing authorization.

An explicit stop remains in force until the user explicitly resumes experiments.
A status check, review, documentation edit or approval of these rules is NOT a
resume instruction. While paused, do only the requested read-only/documentation
work: no proof implementation, verifier changes or workflow dispatch.

After explicit resumption, autonomously edit, commit, push, dispatch, inspect and
iterate WITHIN the phase and tool-profile allowlist recorded in `STATUS.md`.
Do not ask the owner to click Run workflow or inspect routine failures.
A green fixture permits the next already-agreed step, not a new architecture,
tool extension or phase. At a phase boundary, unresolved material decision or
new trust requirement, checkpoint and ask the owner before expanding scope.

One relevant hosted experiment at a time. Keep `workflow_dispatch` as the only
research trigger; no push, pull_request or scheduled triggers, speculative jobs
or duplicate dispatches. No upstream PR, external comments, tool application or
bounty submission without separate user authorization.

## Hard rule: no verification or builds on the user's server

The server is an editing and orchestration machine only. ALL compilation,
verification and executable tests run on GitHub-hosted Actions runners.
Never run Kani, CBMC, VeriFast, Cargo builds/checks/tests, rustc, bootstrap/x.py,
research runners/extractors, scripts/run-kani.sh, or containers/remote subprocesses
that perform these tasks on the server. Do not install build/verifier dependencies,
run a "quick" compile check, use self-hosted runners or move to paid compute.

Local reading/editing, git/gh operations, downloading/reading Actions evidence,
`git diff --check`, `bash -n` and lightweight non-executing document/YAML parsing
are allowed. GitHub failure is not permission to verify locally.

## Frozen trust boundary and proof integrity

Develop our own specifications/proofs; do not import other solutions' proof code.
Verify the actual repository std source without changing its runtime behavior,
algorithms or generic signatures. Keep experiments under `research/challenge-8`;
injection/exact-source extraction happens only in disposable Actions checkouts.
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

Follow the runbook's exact-SHA dispatch/monitor loop. A changed source requires
a NEW run; rerunning an old run checks old code. After meaningful results, update
the compact `STATUS.md`, append evidence to `EXPERIMENT-LOG.md`, and update
`coverage.md`/the relevant design note when their claims change. Keep operating
instructions free of chronological run logs. Preserve failures, source/run/tool
identifiers and historical evidence; a documentation commit is not a proof run.

During an active authorized session, poll the specific run and continue routine
within-phase work; do not offload monitoring to the owner. Report concisely in
Russian. On stop or session limits, save a checkpoint with exact state, active
run ID (if any), draft status and the next permitted action. Do not promise work
after the session ends. Documentation-only changes require no verification run.
