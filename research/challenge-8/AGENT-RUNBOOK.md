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

**Latest inspected run:** [37400422055](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37400422055),
source `9d4a01fc9388b53d2bc4cfc53651a3b728914457`,
`verifast_insert_tail_range`,90min. Full logs/artifacts fetched; no active run.
New change removes incomplete ghost
FnMut generic arguments, preserving MIR inference and the actual Rust call.
All borrow preparation, quarter-token accesses, checked assertions, original
req and exact-byte/refinement audit remain. All quarter assertions and the two
actual &* expressions pass; comparator call next lacks Args tuple own with
two inferred lifetime placeholders at std/lib.rsspec:47. Function not proved.
Exactbyte/refinement0,VF1(.19s),refiner.11s,runner1:12.85,RSS617,796KiB.
Next prove the tuple ownership/lifetime match using supported complete generic
substitutions or tuple closing, without assuming caller resources.

**Latest tuple syntax run:** [37401170274](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37401170274),
source `661cee7cdf711f2996721bf0361151a34fb158b6`,range90min. Explicit tuple
own closure and complete ghost substitutions F,(&'cmp T,&'cmp T),'cmp; pinned
trait parser confirms this order. Full evidence fetched: parser rejects ghost
tuple value (a,b), requires supported numeric-field std_tuple_2_ constructor.
Exactbyte/refinement0,VF1(.09s),refiner.11s,runner13.32s,RSS634,536KiB.
No active run. Prepared constructor correction leaves original req/Rust bytes
unchanged. Independent pure generic size
target is prepared in new files; choice verifast_swap_size exposed on default
main by workflow-only commit79c6dc9, runner not yet reviewed/committed.

**Completed bounded milestones:** bootstrap two actual swap harnesses,5/5covers
at `34d008324e10a66bf59de705acd609d9509e7c36` (37383583285).
Insertion contract, summarized research caller and direct actual std insertion
all pass,15/15covers,unwind assertions pass,none undetermined, at
`ec5556cf37fc31af4b25d27476c88f5fbc8e77c9` (37389298278).
Verification22.868813+5.359691+16.718891s versus runner5:38.03,RSS1,944,792KiB.
These are four-cell i32 proofs with functional assumptions, not full Challenge8.

**Current generic direction:** actual insert_tail extracted mechanically with
CopyOnDrop and actual outer function, pinned VF26.09/nightly-2026-02-05.
Only insert_tail specified; the other bodies remain unverified. Original range
req has symbolic n>=2, writable initialized owned generic T cells and owned
comparator F, no sortedness or length cap. Ens true remains a weak diagnostic.
Run37397404058 at `91392b65f2dcc122a33a55f94377b6e372c74760` proved
interior_pointer_limits and first actual tail.sub(1), then lacked the reference
precreation token. Subsequent shared-cell preparation uses split arrays/Town,
full/shared borrows and reference initialization. Lifetime diagnostics located
half-token reservation at let_lft (37399825118): source verifast.ml:2629-2640
keeps half until block exit. Two quarter accesses address the available half.
Latest finished37400101276 at `86edc719f6aefcbe5acc66d1203bd6dbcf0e761a`
fails Incorrect number of type arguments at ghost::<'cmp> on FnMut. Exact audit
and refinement0,VF1(.11s),refiner.08s,runner11.53s,RSS621,304KiB. The active run
removes that incomplete list; MIR translator replaces the entire list when
annotated. Need Actions evidence for actual call/lifetime matching. Afterward,
exclusive access must be recovered before tail.read even though the binding
scope ends later. No completed generic function or guard/outer-loop proof.

**Concrete Kani blockers on unchanged pin:** actual insertion UB safety run
37396688760 at `43f133c72fcd4f3dffe033582aa96aa2500bf860` executes7/7covers,
no undetermined,sole1/469failure is unsupported copy_nonoverlapping validity
check. Pinned check_values.rs:387-393 inserts this unconditionally; do not
remove the copy or valid-value flag. Verification3.1836462s versus runner3:54.96,
RSS1,821,596KiB. Observed immutable-static write control37397720683 at
`75799de75efab17d9c386deea6c49047db16cb60` unexpectedly verifies0/205 and
1/1cover after write9/volatile-read/assert9, positive controls4/4covers.
Detector missing for observable modeled immutable-byte mutation; suite correctly
fails. Both categories remain open, no all-UB claim. See ub-checks.md.

**Other pending tool questions:** outer-loop instrumentation run37390973809
at `a3da2d490ca6129f0abd4c59063b8100ed73981b` compiles but emits missing-argument
nondeterministic substitutions, stopsSIGTERM143 before final properties/covers.
Never accept such a result. Frozen-pointer/const-address/stride rewrite is
prepared but unverified; retain reproducer and obtain GOTO call/formal evidence
on Actions before attributing the cause. See outer-invariant-diagnostic.md.
Generic compiler-generated Drop uses pinned drop_in_place's weak summary; a
method-local destructor contract alone does not explicitly provide restored
array ownership. See verifast-drop-diagnostic.md for source evidence and the
needed gating Actions probe; not yet a demonstrated cleanup-proof blocker.

Full chronological run evidence, exact pins/domains/counts and prior failures
are in README.md and topic notes. All completed runs above have fetched full
logs/artifacts; artifacts expire7days. Runtime std source is unchanged,
SHA256 `32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959`.

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
