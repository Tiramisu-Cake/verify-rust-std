# Approved phase: actual sort4_stable

Historical functional-phase scope. Its later follow-up is separately approved
in [SORT4-CONTRACT-PHASE.md](SORT4-CONTRACT-PHASE.md); use [STATUS](STATUS.md)
for current authorization. This phase's proof results and scope remain intact.

Approved 2026-10-06. State at approval: READY; no sort4 implementation or hosted
proof run yet. Consult [STATUS.md](STATUS.md) for subsequent execution state.
This phase implements stage 1 of the [approved roadmap](PLAN.md).

Execution closed on 2026-10-06: [functional proof results](SORT4-RESULTS.md)
and [generic-safety architecture checkpoint](SORT4-SAFETY-DECISION.md).
The approved scope below is retained as the record of the executed phase;
it does not authorize a repeated phase or later work after this closeout.

The approval permits autonomous proof/specification/runner edits, commits,
manual hosted runs, inspection and routine fixes within this document.
The preceding ManuallyDrop/insert_tail phase remains closed. This approval
does not authorize its integration work or any verifier semantic change.

## Entry evidence and fixed target

- Repository: `Tiramisu-Cake/verify-rust-std`; branch: `challenge-8/research`.
- Planning baseline: `25c590235c67107cffc92cf70b69568c388ac3ed`.
- Target: [actual SmallSort source](../../library/core/src/slice/sort/shared/smallsort.rs),
  `sort4_stable<T, F: FnMut(&T, &T) -> bool>`; source Git blob at approval:
  `e555fce440872898e47fd5114f32eb15401d07df`.
- Five comparator calls precede four `copy_nonoverlapping` operations.
  No loops, gap, `ManuallyDrop` or Drop guard occur in this body.
- Read [coverage](coverage.md), [UB checks](ub-checks.md),
  [tuple ownership](verifast-tuple-parser.md),
  [FnMut HRTB](verifast-fnmut-hrtb.md) and the
  [previous closeout](PREPARED-PHASE-2026-10-06.md) before designing probes.

Recheck the branch, actual source and active runs at entry. Record any source
difference; do not silently reuse evidence for another body. The existing
workflow has no sort4 selection at approval: implementing and auditing that
selection/runner is part of this phase, not a previously completed result.

## Work and deliverables

### 1. Contract and caller audit

Write a source-linked contract note before implementing harnesses. Separate
the full generic safety target from the narrower functional theorem.

Account for four initialized readable source elements; destination storage,
alignment, bounds, provenance and permissions; overlap restrictions at each
copy and across the sequence; and caller scratch ownership. Review the actual
call sites in `small_sort_general_with_scratch` and `sort8_stable`, including
scratch setup in `small_sort_general`. Derive requirements from
the code and callers rather than treating the short SAFETY comment as a
complete resource contract. If the stated contract has a gap, record it; do not
silently repair the target by assuming a stronger universal precondition.

Distinguish initialized bytes from ownership of a live `T`. Copying bytes to a
second buffer does not create a second independent `T.own` sequence or justify
double drop. Cover generic non-Copy/non-Freeze types and ZST as target
obligations even though the functional harnesses below do not cover them.

Specify normal and unwind resources, including `F` and frame resources.
Safety must allow stateful/interior-mutating and panicking comparators under
their valid Rust contracts; ordering/purity premises belong to functionality.
Describe panic at each of the five comparison sites. The sorting body has not
written to the destination before any such panic; this observation alone does
not restore borrows or imply that the callback left its reachable state
unchanged. Preserve permitted callback effects in the unwind postcondition.

### 2. Actual-body Kani functionality

Prove separate, clearly named claims using the real repository function:

| Harness | Domain and assumptions | Required postconditions |
| --- | --- | --- |
| Values | Four independently symbolic i32 inputs covering the full i32 range; pure, nonpanicking `<`; separate valid source/destination allocations of exactly four initialized cells | Destination is nondecreasing and has exactly the input multiset. Do not use only a sum or another lossy permutation surrogate. |
| Stability | Four concrete tagged items `{ key: i32, original_id }`; symbolic keys, fixed distinct input IDs 0..3; comparator reads only key; same fixed/disjoint buffer model | All complete input items occur exactly once, keys are nondecreasing, and equal-key outputs have increasing original_id. Instantiate the actual generic body with this item type. |

Keep the concrete tag representation and buffer initialization explicit.
An i32-only proof cannot distinguish the identities of equal values.
Four is this function's complete arity; the type/layout, buffer and comparator
restrictions still prevent calling either harness unrestricted generic safety.

Use assertions for the stated properties, nonvacuity covers for representative
reachable decisions, all-equal/mixed-duplicate inputs and extreme keys, and
sufficient unwinding assertions for any harness helper loops. Explain
unreachable covers from ordering constraints rather than deleting failures.
Do not change the target runtime body or substitute a hand-written network,
finite-domain table, assumed target summary or competitor proof.

Declare the Kani check profile before running. A functional baseline with
repository default checks is a distinct claim from an explicit
uninitialized/validity/pointer-check diagnostic. Retain each configuration and
result: never turn a failed stronger check green by disabling it, or report
the baseline as covering that missing UB category. Existing unsupported
`copy_nonoverlapping` validity instrumentation and the immutable-write
detector gap remain unresolved unless new applicable evidence establishes
otherwise. A duplicate demonstration of a known limitation is not required.

### 3. Generic-safety feasibility

First map each sort4 obligation to existing source/tool evidence. In
particular, inspect tuple-argument ownership, higher-ranked `FnMut::Output`,
five shared-reference borrow/recovery boundaries, direct unwind, copying
permissions and single ownership of the resulting values.

The absence of insertion's gap/ManuallyDrop does not establish that unchanged
VeriFast can prove the generic comparator calls. Do not rerun an already
understood failing callback probe merely under a new target name. A hosted
diagnostic is justified only by a written new, falsifiable existing-semantics
route and a result that would change the decision. At most one such route is
in scope; routine fixture/setup fixes may be attempted when evidence supports
them, but discovering a required semantic extension ends that route.

Use the unchanged pinned release only. If a needed capability is missing,
write an architecture decision describing the first blocker, exact evidence,
normal/unwind obligations, minimal proposed capability, trust/admissibility
questions and acceptance/rejection criteria. Do not implement or import the
capability. A static no-go assessment is a valid feasibility result; it must
not be presented as an executed proof.

A blocked generic route does not cancel independent functional work already
authorized in step 2. Complete what can be completed within this phase, then
report the separate outcomes.

### 4. Closeout

Save the contract, harness/runner sources, experiment cards and results.
Update STATUS, EXPERIMENT-LOG and coverage. Produce a closeout containing:

- Exact proved properties, source SHA/blob, run URLs, tool/configuration hashes,
  domain, assumptions, assertions/covers and setup versus verification cost.
- A separate result for each required UB category: dangling/misaligned access,
  uninitialized reads, immutable-byte mutation and invalid values.
- Generic ownership, comparator effects, panic and aliasing obligations still
  open; distinguish source inspection, a checked proof and an unsupported case.
- Go/no-go for a next phase or a specific architecture decision. Do not begin
  that next phase automatically.

No full Challenge 8 completion, generic safety, arbitrary allocation/type
coverage or cross-tool composition follows from the functional theorem alone.

## Tool and edit allowlist

| Area | Allowed in this phase | Boundary |
| --- | --- | --- |
| Kani | Unchanged pin `152c6a8c875d9886a67e229247b4826d6105ccfd` from [kani-version.toml](../../tool_config/kani-version.toml); repository toolchain; initial `--jobs 1` | No pin, compiler, CBMC, memory-model or instrumentation changes |
| VeriFast | Unchanged release 26.09, source `809de4596839b739dd999f9e462242c835e3af46`, Rust `nightly-2026-02-05`; retain existing release/export/decoder/refinement audits | No tuple/HRTB/ManuallyDrop/lifetime/Drop patches, prelude overlays, RawPtr support changes or AST/unwind rewriting |
| Proofs/specifications | Own sort4 harnesses, contract, proof-only adapters and diagnostic fixtures under `research/challenge-8` | Actual runtime body/signatures unchanged; injection/exact-source extraction only in disposable Actions checkouts |
| Automation | Sort4 runner and narrowly scoped selection/routing in [.github/workflows/smallsort-research.yml](../../.github/workflows/smallsort-research.yml) | Manual trigger only; preserve existing selections and audits. A necessary default-branch exposure follows the runbook's narrow workflow-only procedure. |
| Documentation | Current checkpoint, cards/results, coverage, contract, feasibility/closeout and index links | Preserve earlier failures and conditional evidence |

All compilation, verification, executable tests and extractors run only on
GitHub-hosted Actions. Local work is editing/orchestration and the static
checks allowed in [AGENTS.md](../../AGENTS.md). No new tool integration,
Frama-C/Coq execution pipeline, external publication or submission is in scope.

## Budget, stops and next permitted action

Use the [runbook](AGENT-RUNBOOK.md): one relevant run at a time, explicit
selection and full source SHA, inspect successful and failed logs/artifacts.
Default budget is 90 minutes per run including setup; 30/60 are available for
a justified smaller diagnostic, and 120 only after a measured budget bottleneck.
Record an outcome-to-next-action decision before each dispatch. No blind
unchanged retry or speculative expansion.

Stop the affected route when it needs a new tool semantic/trust decision, a
changed target/contract, or repeated failure without new evidence. Checkpoint
any applicable independent result before requesting a new decision.
At completion or a phase-wide blocker, save a precise status and stop;
later roadmap stages require their own approval.

First action for the continuation agent: read the current instructions/status,
audit the exact sort4 body and callers, write the contract and first experiment
card, then implement the actual-source functional harnesses and hosted runner.
Routine execution of this approved phase needs no further start confirmation.
