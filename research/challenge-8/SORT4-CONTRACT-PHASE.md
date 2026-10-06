# Approved phase: sort4 contract diagnostics and generic proof route

Approved by the owner on 2026-10-06 after review of the completed functional
phase. State at approval: READY; no overlap diagnostic has been implemented or
run yet. [STATUS.md](STATUS.md) is the current execution checkpoint.

Closeout: this named phase completed in [SORT4-CONTRACT-RESULTS.md](SORT4-CONTRACT-RESULTS.md).
It is CLOSED at the owner architecture decision; proposed future implementation
is NOT AUTHORIZED. The scope below is the historical approved execution contract.

The continuation agent was authorized to implement, commit, push, dispatch,
inspect and fix the bounded Kani diagnostics below, refine the research
contract, and prepare one concrete generic-safety architecture proposal.
No further start confirmation is needed. This documentation iteration records
the approval and does not run the phase.

## Baseline and first reads

- Repository `Tiramisu-Cake/verify-rust-std`, branch `challenge-8/research`;
  approval baseline `bea705d12062e515e69abc4ab4398944f9f82d65`.
- Actual target [smallsort.rs](../../library/core/src/slice/sort/shared/smallsort.rs),
  `sort4_stable<T, F: FnMut(&T, &T) -> bool>`; original Git blob
  `e555fce440872898e47fd5114f32eb15401d07df` stays fixed.
- [Functional closeout](SORT4-RESULTS.md), proof SHA
  `1bc9cb718efc07315082334cded2d2362ecbbde1),
  [run 37459631500](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37459631500):
  exact i32 multiset and tagged stability passed, 18/18 covers, in separate
  initialized buffers with pure comparison. Those results remain established.
- Read [AGENTS](../../AGENTS.md), [PLAN](PLAN.md), [runbook](AGENT-RUNBOOK.md),
  [contract/caller audit](SORT4-CONTRACT.md),
  [generic-safety assessment](SORT4-SAFETY-DECISION.md) and [coverage](coverage.md).
  Review referenced tuple/HRTB, borrow and direct-unwind evidence before design.

The existing functional phase and insertion/ManuallyDrop phase remain closed.
This approval opens only this named follow-up; it does not resume old patch
experiments or authorize a generic VeriFast proof implementation.

## 1. Reproduce the two distinct overlap questions

Prepare an experiment card before implementation/dispatch. Use the unchanged
actual function, i32 storage and pure nonpanicking `<`. Build pointers from
one valid backing allocation where overlap is intended; do not introduce
conflicting live Rust references or dangling/unaligned pointers in the harness.
Snapshot input values by value before the call. Isolate each case and select
its exact harness name so an intended failure cannot mask another result.

| Case | Initial domain | Hypothesis and intended evidence |
| --- | --- | --- |
| Positive control | Separate four-cell source/destination buffers | Reuse the existing actual-body values harness unchanged under the same profile. Its posts and 12 covers must pass, validating the baseline in this diagnostic suite. |
| Coincident ranges | Initialized mutable i32 array `[0,1,2,3]`; source and destination at its base | Ascending decisions select source 0 for destination 0. Expect a failure of the actual first `copy_nonoverlapping` non-overlap obligation. Read/write validity alone does not rule out this case. |
| Shifted overlapping ranges | One initialized i32 array `[0,1,2,3,4]`; source slots `[0,4)`, destination slots `[1,5)` | Individual copies on this ascending route use distinct one-cell regions, but each write overwrites the next source. Predict destination `[0,0,0,0]` and failure of exact multiset preservation against the original `[0,1,2,3]`, while default memory checks pass. |

These are hypotheses until observed. The coincident case tests a missing
safety premise. The shifted case tests preservation of original values;
it must not be described as UB merely because its multiset post fails.
Sortedness alone would not detect four equal output values. A concrete example
does not classify every overlap pattern or prove a generic contract.

Keep the two negative outcomes distinguishable in automation:

- Record raw tool exit codes, actual failed property IDs/descriptions/locations,
  counterexample values and all other check results.
- Accept the coincident negative only at the intended actual-copy overlap
  obligation. Predeclare the permitted failed-property set; the tool may
  report multiple instances of the same violation. Do not draw conclusions
  from execution after the first UB boundary.
- Accept the shifted negative only at the explicit original-multiset assertion,
  with the intended destination trace and no unexpected memory-check failure.
  A separate consistent witness harness may confirm the output if needed.
- An expected-negative suite can finish green only when its positive control
  passes and each negative matches its declared failure. A generic nonzero
  exit, build failure, unsupported operation, timeout or unrelated assertion
  does not count as the counterexample.
- If observation differs, report the actual first cause and revise the
  hypothesis from evidence. Never suppress a check to obtain the expected result.

Use the existing Kani default-check profile; retain all checks, unwinding
assertions and source audits. Known explicit validity/uninitialized/immutable-
write instrumentation limits remain as recorded. No stronger generic UB
coverage is inferred from these diagnostics.

## 2. Refine the contract and its applicability

Update [SORT4-CONTRACT.md](SORT4-CONTRACT.md) with explicit preconditions and
normal/unwind resource postconditions, using named predicates or mathematical
notation where useful. Separate established facts, sufficient assumptions and
open proof obligations; a list of topics alone is not the deliverable.

Distinguish:

1. The short current SAFETY comment and what the body actually requires.
2. Conditions sufficient for safety, including each copy's validity and
   non-overlap, independently of ordering assumptions.
3. Conditions for stable preservation of the original elements across the
   whole copy sequence; explain why the callers' separated scratch suffices.
4. The narrower theorem already checked by Kani.
5. Any proposed strengthening/clarification that would need acceptance before
   claiming the original public target is fully covered.

Account for source/destination initialization, alignment, bounds, provenance
and permitted callback effects; non-Copy/non-Freeze types and ZST; ownership
of original and copied representations; and any prior destination resources.
Actual callers use `MaybeUninit` scratch: the generic contract must account
for uninitialized destination storage, independently of the old harnesses'
initialized-destination assumption.
State which range can subsequently be treated as owning and dropped. Do not
invent a second independent ownership sequence from byte copying or equate
every resource-accounting issue with a demonstrated UB.

Give full normal and all five comparator-panic posts, preserving permitted
changes to `F`, interior state and frame resources. No destination write by
the sorting body precedes those panics, but callback effects and borrow recovery
still require accounting. Pure/orderly comparison is a functional premise,
not a restriction on the unrestricted safety target.

Map the proposed premises to the real `small_sort_general_with_scratch` and
`sort8_stable` call sites. Reuse their existing source audit; investigate
specific gaps rather than restarting broad literature research. Keep proposed
contracts/comments in research documents: do not edit the std source or silently
declare a stronger research contract to be the challenge's accepted contract.
If organizer clarification is needed, record the precise question without
sending it externally.

## 3. Select one concrete generic-proof architecture proposal

Review the existing experimental patches, pinned sources, regression results
and failed routes. This is read-only analysis of verifier changes, not permission
to apply, build, extend or dispatch them. Use existing evidence first.

Update [SORT4-SAFETY-DECISION.md](SORT4-SAFETY-DECISION.md) with one recommended
technical route and:

- A minimal dependency table: needed capability, exact existing patch/source
  and hashes where applicable, observed result, unproved gap, and whether the
  capability can be reused, needs redesign or is unnecessary for sort4.
- A source-exact route through tuple-2 argument ownership, the higher-ranked
  `FnOnce::Output = bool` projection, all five callback continuations and
  direct-unwind exits, copying permissions and the proposed ownership post.
- A clear separation between existing supported semantics and any proposed
  semantic additions. Passing tuple/HRTB setup alone does not solve resource
  recovery; name every remaining dependency rather than hiding it.
- The first bounded implementation experiment that would test this route:
  hypothesis, fixed tool/patch profile, full normal/unwind target posts,
  positive and intended-negative regression matrix, source/refinement checks,
  trust/admissibility questions and go/no-go criteria. Mark it NOT AUTHORIZED
  for implementation in this phase.

Do not reproduce a known failing unchanged-VeriFast callback probe, promise a
generic theorem based on the concrete Kani result, or present an unbounded menu
of tool experiments. If no viable route can be justified, deliver a specific
no-go with the missing prerequisite and the owner's next decision instead of
inventing a solution.

## Allowed work, budget and stop boundary

Kani stays at `152c6a8c875d9886a67e229247b4826d6105ccfd`, repository Rust
`nightly-2026-02-05`, unchanged default checks through `scripts/run-kani.sh`,
exact harness selection and `--jobs 1`. The existing functional harness,
source body, tool pins, checker semantics and runtime signatures remain intact.

Allowed edits are own diagnostic harnesses/runners under `research/challenge-8`,
contract/decision/evidence documents, and a narrowly scoped manual workflow
selection. Proposed selection: `sort4_contract_diagnostics`; it does not exist
at approval. Implement and audit it before dispatch. Preserve existing selections
and `workflow_dispatch` as the only research trigger. A necessary default-branch
exposure follows the runbook's workflow-only procedure.

VeriFast 26.09, source `809de4596839b739dd999f9e462242c835e3af46`, and its
historical profiles are reference evidence only in this phase. No new VeriFast
run, patch application/build, prelude/model/refinement change, replacement
verifier or tool integration is authorized. No later sorting target or external
publication is included.

All executable work stays on GitHub-hosted Actions. Keep one relevant run
active, all cases isolated and processed serially. Default budget is 90 minutes
for setup/build and the diagnostic suite; record common workflow preparation
separately. Use 30/60 for a justified smaller run; 120 only after a measured
budget bottleneck. Inspect full successful and failed logs/artifacts, exact
source/tool/configuration hashes, case results and cost. Reuse the unchanged
functional values harness as the positive control; no separate cold rerun of
the closed stability proof is needed merely to refresh evidence.

Routine harness/runner/fixture fixes are authorized. A needed semantic change
or repeated failure without new evidence ends the affected diagnostic route;
continue independent contract/architecture work where possible. Do not turn
an unresolved diagnostic into a reported counterexample.

At closeout, update STATUS, EXPERIMENT-LOG and coverage; save a concise new
`SORT4-CONTRACT-RESULTS.md` with the observed cases, contract delta, one chosen
architecture proposal and exact next decision. Keep the old functional
closeout and evidence intact. Stop at that decision: implementation of the
proposed verifier capability requires separate owner approval.
