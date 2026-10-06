# Challenge 8 agent runbook

## Mission and working context

Build our own automated proof of the actual Rust SmallSort implementation.
The owner's mathematical background supports precise specifications; explanations
and progress reports should be in Russian. The existing small experiments are
scaffolding for an eventual submission that meets the full challenge.

- Fork: https://github.com/Tiramisu-Cake/verify-rust-std
- Working branch: challenge-8/research
- Upstream: model-checking/verify-rust-std; tracking issue #56.
- Requirements: doc/src/challenges/0008-smallsort.md and doc/src/general-rules.md.
- Target: library/core/src/slice/sort/shared/smallsort.rs.
- Workflow: .github/workflows/smallsort-research.yml, named SmallSort research.
- Kani pin: tool_config/kani-version.toml; currently
  152c6a8c875d9886a67e229247b4826d6105ccfd (Kani 0.67.0).

Read root AGENTS.md. Its prohibition on server-side builds and verification is
the owner's explicit instruction, not an optional performance recommendation.

## Handoff status — 2026-10-06, Europe/Moscow

Latest inspected success:
https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37389298278
at `ec5556cf37fc31af4b25d27476c88f5fbc8e77c9`, `insertion_all_4`, 90 minutes.
All three stages verify: contract 0/292 failures, 6/6 covers (22.868813 s);
summary-based research caller 0/288, 2/2 covers (5.359691 s); direct actual std
insertion 0/168, 7/7 covers (16.718891 s). All unwind assertions succeed.
Four incidental unreachable checks per stage, none undetermined. Exit 0;
runner including cold build/compilation: 5:38.03, peak RSS 1,944,792 KiB.
Pinned Kani/CBMC unchanged. See README for prior failure/fix history.
This is bounded i32 functionality with sorted-prefix assumptions, not completion.
Bootstrap remains verified at `34d008324e10a66bf59de705acd609d9509e7c36`
(run 37383583285), both harnesses, 5/5 covers, bounded fixed i32 positions only.

**Outer-loop experiment history:** `insertion_outer_invariant_4`, 90 minutes. A proof-only
injector adds allocation and range invariants to the actual outer pointer loop;
new harness uses arbitrary i32 inputs and comparator decisions, no sortedness
assumption. Inner loop remains bounded, default checks only. Generic contracts,
functional loop invariants, ownership/panic and explicit UB checks remain open.
The choice is exposed on default-branch workflow only (commit `985f790`).
Latest outer-loop attempt: [37390232978](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37390232978),
source `9dd5410ba262feccdd864140acfe716693d21cdc`, `insertion_outer_invariant_4`,
90 minutes. Compilation E0433: unqualified kani macro not in scope at line599.
No proof/covers checked; runner 4:04.95, exit1, peak RSS1,312,076KiB.
Fix uses `crate::kani::loop_invariant`; invariants/domain/checks unchanged.
Latest qualified outer attempt: [37390973809](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37390973809),
source `a3da2d490ca6129f0abd4c59063b8100ed73981b`, same selection/budget.
Compilation succeeds. CBMC warns "not enough arguments, inserting
non-deterministic value" for same_allocation_internal and pointer add inside
invariant; no final proof or seven-cover outcomes. SIGTERM/143 stops job at
14:55, before requested 90-minute budget; cause unspecified, no OOM/timeout
claim. All artifact/post steps skipped, zero artifacts. Full log fetched;
essential evidence in outer-invariant-diagnostic.md. Preserve this reproducer
and resolve instrumentation warnings before accepting/rerunning its proof.
Latest VeriFast probe: [37393312268](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37393312268),
source `8f1fc630b590c89c99270f23fd9bb7f2e32b8eb8`, `verifast_insert_tail_probe`,
90 minutes. VF26.09 parser now accepts contract and explicitly reaches actual
`smallsort::insert_tail`; first pointer bound fails at `tail.sub(1)` because
`req true` supplies no range. Source/ghost audit and refinement checker pass;
verifier/overall exit1, runner13.38s, RSS620,128KiB. This is frontend/model
viability evidence, not a safety proof. Full evidence fetched.

**Current direction:** generic VF range-bound proof (no length cap), followed
by the prepared actual insertion safety runner with measured UB flags. The Kani outer rewrite now freezes the initial
pointer outside the invariant, uses explicit const pointer allocation arguments
and address bounds, and adds an inductively checked element-stride obligation.
It preserves input domain and all original obligations; arity-warning cause
remains a hypothesis, rewrite not verified. Latest owned-range result: [37394022890](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37394022890),
source `2ba502bc71cd25657584592fb83da044a7323252`,
`verifast_insert_tail_range`, 90 minutes. Symbolic generic range contract parses;
actual insert_tail still fails first tail.sub(1) pointer-limit proof. Exact-source
and refinement audits pass, verifier/overall1, runner14.10s RSS636,068KiB.
No completed safety proof. Next expose/prove interior-pointer facts, no assumed
conclusions or length narrowing. Default workflow choice commit `8016336`.
Latest UB controls: [37394356873](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37394356873),
source `6e0503febfe9c162e2e89a7ccfbd6126c9ca3be9`, `ub_detector_controls`,90min.
All7 execute. Both positives pass2/2covers each; uninit/invalidbool/misaligned
controls have their intended failures. NULL check fails explicitly plus
uninit/OOB: conservative classifier inconclusive,4 checks undetermined.
Immutable-static write passes: missing detector for that concrete case.
Suite1/notvalidated,497s cold build+compilations vs summed verification1.775s,
maxRSS1,808,612KiB. Full logs/artifacts fetched. Keep immutable-byte gap explicit;
investigate pinned compiler/CBMC lowering before claiming full required UB.
Prepared actual insertion UB safety runner has the same profile but cannot
establish the missing immutable-byte category. Latest array-inv result:
[37395348422](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37395348422),
source `6851c1a9edc96f26f724efca2bc78acc78ef2a42`, range90min. Ghost call
accepted; same first pointer-bound failure. Exact-source/refinement0;
VF1(.10s),refiner.09s,runner15.66s,RSS620,480KiB. No completed proof.
Next generic work: proved interior-pointer lemma from endpoints, no assumed
conclusion or length restriction. Also prepare observed immutable-static write
control after pinned-source audit showed write and pointer checks were modeled,
but no mutability property emitted (--no-assert-contracts not its explanation).
Next Actions selection: insertion_ub_safety_4,90min, actual bounded i32 safety
without loop injection/sortedness assumptions; same UBflags and explicit
immutable-byte gap. Latest actual safety attempt:
[37395779522](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37395779522),
source `fe7567964629b627cf2bcb96ab71b8834316abcc`,safety90min. Kani uninit
frontend ICE at initial_target_visitor.rs:107, unsupported Formatter function
pointer resolution (#3300); no harness/property/covers verified. Runner3:56.45,
RSS1,631,772KiB,overall1. Hypothesis: formatted range-index panic in harness.
Prepared equivalent from_raw_parts_mut slice construction under unchanged
valid len/offset assumptions, initialized array and comparator domain; no std
runtime change/check suppression. Active
[37396479423](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37396479423),
source `da5f16efdcf604582e3646b9f4518bbce71165b6`,range90min: own interior
pointer ghost lemma, derived index0<=n-2<=n, endpoint/monotone-multiplication
proof; no new input assumption or numeric cap. Inspect lemma positivity/algebra
and first actual target obligation, refinement audit and covers/target counts.
Then choose safety retry or observed immutable-store diagnostic; one run at a time.

## Repository map and verifier details

- smoke.rs: two original swap_if_less bootstrap proofs.
- insertion-4.rs: actual insert_tail behind a monomorphic proof-only adapter;
  a caller using verified summaries; a separate direct proof of the actual
  insertion_sort_shift_left.
- insertion-contract.md: specification, assumptions and proposed invariants.
- run-smoke.sh and run-insertion.sh: Actions entrypoints; do not execute locally.
- insertion-safety-4.rs and inject-outer-invariant.py: actual outer-loop safety prototype.
- outer-invariant.md and coverage.md: prototype scope and challenge obligations.
- extract-verifast-insertion.py, run-verifast-probe.sh and verifast-probe.md:
  exact-source approved-tool feasibility probe, no completed proof yet.
- README.md in this directory: experiment scope and run log.

The insertion order is prove_tail_contract_4, prove_composition_4,
prove_direct_insertion_4. The runner stops on the first failure; the summarized
caller must not be accepted if the callee failed. The direct stage is a separate
check, not a modular proof of the real outer loop.
The domain is arbitrary i32 values in a four-element backing array, symbolic
valid lengths/offsets, and unwind 6. Values include duplicates and extremes.

The pinned std integration uses kani::cover(condition, message), not cover!.
scripts/run-kani.sh already enables function/loop contracts and related unstable
features. Check API syntax against the PINNED Kani source before inventing flags
or annotations; if compilation is needed, create an Actions experiment.
The workflow caches Cargo downloads, not the complete verifier build. Cold
build time counts toward the chosen budget. Artifacts expire after seven days.

## Start or resume a session

Inspect git status, current branch and remotes. Fetch the fork and use
challenge-8/research without overwriting user changes. In a clean clone, a
typical setup is:

~~~bash
git status --short
git remote -v
git fetch origin
git switch challenge-8/research
git pull --ff-only origin challenge-8/research
gh auth status
~~~

If the branch does not exist locally, create it tracking the fork's remote branch.
If origin is not the fork, use the actual fork remote; do not blindly change it.
Check authentication for git push AND workflow dispatch. Never print tokens.
If gh is unavailable or unauthorized, use an already authorized equivalent
GitHub API client if available; otherwise request only the missing setup.
Do not substitute server-side verification.

## Autonomous edit → push → dispatch → inspect loop

The examples below use GitHub CLI. Consult installed gh help if an option differs.
Official references:
https://cli.github.com/manual/gh_workflow_run
https://cli.github.com/manual/gh_run_list
https://cli.github.com/manual/gh_run_view
https://cli.github.com/manual/gh_run_download

1. Choose one concrete proof obligation from the plan. State its domain,
   preconditions, expected properties and what will remain unproved.
2. Make the smallest useful implementation. Locally inspect the diff and use
   only permitted static checks (for example git diff --check or bash -n).
   Never execute the proof runners on this server.
3. Commit only the intended files and push normally to the fork's research branch.
   Verify its remote SHA matches git rev-parse HEAD. Do not dispatch unpushed code.
   After confirming origin is the fork and you are on the research branch:

~~~bash
git push origin HEAD:refs/heads/challenge-8/research
git rev-parse HEAD
git ls-remote origin refs/heads/challenge-8/research
~~~
4. Inspect existing research runs before dispatching. Resume monitoring a relevant
   active run instead of duplicating it. Record the pre-dispatch time/run IDs.
5. Dispatch explicitly against the fork and branch:

~~~bash
gh workflow run smallsort-research.yml \
  --repo Tiramisu-Cake/verify-rust-std \
  --ref challenge-8/research \
  -f proof=insertion_all_4 \
  -f budget_minutes=90
~~~

Available insertion selections are insertion_all_4, insertion_contracts_4,
insertion_direct_4 and insertion_outer_invariant_4. The choice all means the two BOOTSTRAP harnesses, not every
research proof. Other bootstrap choices select the individual harnesses.

6. Capture the returned URL if the installed CLI supplies one. Otherwise query
   runs and select the newly created run matching the branch, event and expected
   full headSha. Do not blindly take the latest run from the repository:

~~~bash
gh run list --repo Tiramisu-Cake/verify-rust-std \
  --workflow smallsort-research.yml --branch challenge-8/research \
  --event workflow_dispatch --limit 20 \
  --json databaseId,url,headSha,headBranch,status,conclusion,createdAt
~~~

   If listing is delayed, poll again; do not immediately dispatch a duplicate.
   If multiple candidates exist, compare the pre-dispatch list/time and run
   metadata/logged selection before accepting any evidence. Save the exact run ID,
   URL, SHA, selection and budget in the checkpoint. Do not push further proof
   changes on this branch until the intended dispatch has resolved to its SHA.

7. Poll the specific run roughly once per minute until completed. Use short
   waits so progress updates remain possible; do not end the turn just because
   the job is building or queued. Read-only polling runs locally, verification
   runs entirely on GitHub:

~~~bash
gh run view "$run_id" --repo Tiramisu-Cake/verify-rust-std \
  --json databaseId,url,headSha,headBranch,status,conclusion,jobs
~~~

8. After completion fetch the full log and artifacts, even on success:

~~~bash
gh run view "$run_id" --repo Tiramisu-Cake/verify-rust-std --log
gh run download "$run_id" --repo Tiramisu-Cake/verify-rust-std \
  --dir "/tmp/challenge8-evidence-$run_id"
~~~

   run_id above is the ID you verified, not a placeholder to execute literally.
   Do not commit downloaded archives, injected source or large logs. Keep a
   compact, committed result record before artifacts expire; save essential
   diagnostics and source/tool identifiers there.

9. Check the artifact environment/source SHA, expected selection, all requested
   harnesses, verification outcome, all covers, unwind assertions and exit code.
   A green badge alone is insufficient. Distinguish compilation failure,
   verifier failure, unreachable covers, timeout/OOM and infrastructure failure.
10. On failure, diagnose the first causal error and make an evidence-based fix.
    Preserve proof obligations. Push and dispatch a NEW run after source changes;
    gh run rerun on the old run would verify its original commit.
    On success, record the precise proven scope and advance to the next plan item.
    Do not ask the user to launch or inspect the next run.

Default budget is 90 minutes, with choices 30/60/90/120. A justified retry at 120
is authorized when the log shows the budget was the bottleneck. Repeated timeout
or unchanged failure calls for a different experiment or better contracts, not
blind reruns. Keep --jobs 1 for these initial experiments. Never switch to a
self-hosted runner or chargeable external compute as a workaround.
Documentation-only commits do not require a cold verification build.

Keep workflow_dispatch as the only trigger for the research workflow. For a new
experiment, update its runner and workflow choices explicitly. GitHub requires
the dispatchable workflow to exist on the default branch. If a default-branch
workflow update is necessary, commit only that reviewed workflow change there;
do not merge all research results into main merely to expose a new choice.

## Plan after the pending insertion run

1. Resolve compilation and verify all three insertion stages. Record contract,
   modular caller and direct outcomes separately, including verification costs.
2. Develop a reusable contract and loop invariants for actual insert_tail and
   insertion_sort_shift_left, without changing runtime behavior/signatures.
   Track the sorted processed prefix, conserved multiset, untouched suffix,
   pointer bounds, logical gap, held value and CopyOnDrop restoration.
   Prototype one obligation per experiment using the pinned tool's supported
   annotations. If the tool blocks a generic contract, document a minimal
   Actions reproducer and evaluate an approved alternative or hybrid approach.
3. Test modular reuse on an actual std caller. The current three-call research
   harness is only a composition experiment, not std's pointer loop.
4. Expand domain/type coverage and separate safety harnesses from functional
   ones. Bounded lengths up to 16 are optional performance milestones;
   arbitrary valid lengths remain the requirement. Develop merge specifications
   after establishing the insertion approach.
5. Cover sort4_stable and the other SmallSort primitives, then the three trait
   implementations. Maintain a coverage table for the seven safety targets,
   three sorting contracts, specialization paths, generic types/ownership,
   comparator panic/unwind behavior and each required UB category.
6. Address length-32 scalability and uninitialized-read detection explicitly.
   Measure the supported checks rather than assuming default Kani checks cover
   every required UB. Compare approved tools on concrete blockers.
7. Prepare an automated, reviewable candidate acceptable to upstream CI. Clearly
   document assumptions and remaining gaps. Ask the owner before upstream
   publication or bounty submission.

## Durable progress record

After each meaningful result, update this runbook's handoff/next action and the
README run log in a small commit, then push it. Record:
- Full checked source SHA, run ID/URL and selection/budget.
- Tool pin and exact domain/preconditions, checked properties and enabled checks.
- Harness/cover outcomes and failure diagnosis; time/memory with build time
  distinguished from verification time.
- Whether a result is a real implementation proof or a caller using a verified
  summary, and the source/version supporting that summary.
- The next concrete experiment, any blocker and any active run to resume.

Never infer that a later documentation commit was verified by an older run.
If the session must stop, checkpoint this information before stopping. Autonomous
polling continues only while an agent session is active; this file is not a daemon.

## Prepared alternate-tool diagnostic

The Kani outer run is now incomplete with instrumentation warnings. Evaluate
`verifast_insert_tail_probe` (90 minutes). This uses the approved repository pin
VeriFast 26.09 and nightly-2026-02-05, exact source extraction, ghost-only copy
and refinement-checker. The diagnostic contract is `req true; ens true;` on
actual insert_tail; it intentionally lacks ownership and is expected to fail.
Never label a frontend result or a skipped target as a proof. No ignore-unwind,
allow-assume or assume_correct flags. See verifast-probe.md.
The manual choice/routing is exposed by default-branch workflow commit `4e32d41`;
research source must be pushed before dispatch, and only one experiment active.
Kani loop invariants alone do not enlarge the four-cell harness allocation;
this probe investigates a mathematical arbitrary-length ownership model.
