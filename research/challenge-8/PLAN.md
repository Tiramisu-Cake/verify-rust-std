# Challenge 8: approved roadmap

Approved by the owner on 2026-10-06 after review of the C verification research.
This decision supersedes the insertion-first ordering in earlier handoffs.
[STATUS.md](STATUS.md) remains the current execution checkpoint.
The [sort4 functional phase](SORT4-PHASE.md) is complete. After reviewing its
results, the owner approved the bounded
[contract-diagnostics and generic-proof-route phase](SORT4-CONTRACT-PHASE.md)
on 2026-10-06. That follow-up completed; [its closeout](SORT4-CONTRACT-RESULTS.md)
preserves the historical architecture proposal. The owner then opened the bounded
[no-patch feasibility phase](SORT4-NO-PATCH-PHASE.md); it is now closed with
[the source-grounded assessment](SORT4-NO-PATCH-ASSESSMENT.md). No new c1 candidate
was identified, so no experiment ran. The current recommendation is a bounded
contract/admissibility review, not selection of verifier development. Later sorting
stages and verifier implementation remain separate decisions.

## Decision and evidence

Start with the actual `sort4_stable` body. Its natural arity is four elements:
there is no arbitrary loop-length cutoff in a four-element functional proof.
It makes five comparisons before four copies and contains no loop,
`ManuallyDrop`, gap or `CopyOnDrop` cleanup. This removes several insertion
obligations from the immediate task. It does not remove generic comparator,
borrowing, ownership, pointer validity or unwind obligations.

The decision uses these findings:

| Evidence | Consequence for the plan |
| --- | --- |
| [C verification survey](C-VERIFICATION-SURVEY.md) and [pinned artifacts](C-VERIFICATION-ARTIFACTS.md) | Reuse contract and invariant ideas: permutation, stable ordering, separated ranges and modular callee contracts. C proofs do not establish Rust ownership, comparator or panic behavior. |
| [Sorting-model observations](SORTING-MODEL-OBSERVATIONS.md) | Finite models can guide hypotheses. Missing provenance and the gap from a rewritten model to the actual Rust body prevent treating them as target proofs. |
| Bounded Kani swap/insertion results in [coverage](coverage.md) | The existing actual-source harness route is useful for a finite functional theorem; its concrete type/buffer/comparator domain must remain explicit. |
| [Prepared-phase closeout](PREPARED-PHASE-2026-10-06.md) | Preserve the conditional recovery/Drop results. Defer insertion integration and verifier development until their source applicability and trust decisions are resolved. |
| [Tuple ownership](verifast-tuple-parser.md) and [FnMut HRTB](verifast-fnmut-hrtb.md) findings | A simpler sorting body can still hit the same generic callback blockers. Review existing evidence before proposing a new hosted diagnostic. |
| [Measured UB limits](ub-checks.md) | A functional pass cannot close all four required UB categories. Keep unsupported instrumentation and detector gaps visible. |

The completed immediate stages provide concrete functionality and contract
diagnostics with a precise boundary, followed by an owner decision on generic
safety. Building a general-purpose verifier or translation pipeline remains
outside the approved roadmap.

## Priorities and advancement criteria

| Order | Target | Intended result | Gate before moving further |
| --- | --- | --- | --- |
| 1a — complete | `sort4_stable` functionality | Actual-body sorted exact i32 multiset and tagged stability; 18/18 covers in run37459631500, plus contract/caller and generic-feasibility notes | [Functional closeout](SORT4-RESULTS.md) records the concrete domain. Generic safety and full UB coverage remain open. |
| 1b — complete | `sort4_stable` contract and proof route | Reproduce coincident/shifted-overlap cases; refine full contract and caller mapping; review existing patches and select one minimal generic-safety architecture proposal | [Closeout](SORT4-CONTRACT-RESULTS.md): run37466906281 validates both distinct negatives/control/witness, full contract and one proposed direct-unwind recovery gate. Owner decision required before semantic implementation. |
| 1c — complete | `sort4_stable` no-patch feasibility | Compare checked annotations on official26.09, released26.10 and one integrated alternative (Kani); obstacle matrix and no-run rationale | [Assessment](SORT4-NO-PATCH-ASSESSMENT.md): no evidence-backed full-resource c1 candidate; no generic coverage gained. Stop for owner contract/admissibility decision; historical patched proposal not authorized. |
| 2 — later decision | `swap_if_less` | A reusable compositional compare-exchange contract separating unrestricted safety from ordering assumptions | Extend beyond the existing four-cell/fixed-index i32 result; account for actual `ManuallyDrop`, ownership and normal/panic behavior. |
| 3 — later decision | Actual `sort9_optimal` / `sort13_optimal` networks | Composition from verified compare-exchange calls; explicit formal bridge for any zero-one argument | Establish the theorem's comparator/order assumptions and its correspondence to the real Rust network. Exhaustive Boolean evaluation of a rewritten model is insufficient. Do not infer stability for these networks. |
| 4 — later decision | `insert_tail`, then `insertion_sort_shift_left` | Full normal/unwind inner contract, then an arbitrary-valid-length outer-loop proof | Resolve first false return/direct panic, held references, gap ownership and late panic before relying on a callee summary. Do not replace the proof by a larger unrolling bound. |
| 5 — later decision | `merge_up`, `merge_down`, then `bidirectional_merge` | Pointer/range, permutation and progress invariants adapted to both directions | Reconcile C forward-merge ideas with the real pointer topology, ownership, comparator effects and unwind behavior. |
| 6 — later decision | Three `small_sort` trait implementations | Compose verified helpers across specialization, dispatch, thresholds and scratch storage | Cover all required entrypoints and arbitrary valid slice lengths with integrated, admissible automation. |

This order is a planning priority, not evidence that each stage automatically
unlocks the next. Review dependencies and measured costs at each boundary.
The isolated generic size-helper result is retained and can later support
dispatch reasoning; it does not prove its callers.

## Tool roles and trust boundary

- **Kani:** unchanged repository pin for actual-source functional proofs and
  contract diagnostics, with explicitly identified check profiles and claims.
  The completed phase isolates observed safety and functional counterexamples.
- **VeriFast:** official26.09/26.10 source comparison completed without execution
  in stage1c. Repository pin remains26.09; no new experiment justified. No new run
  or patch build/application authorized after closeout. Historical patched results
  stay conditional on recorded profiles; the proposal remains historical.
- **Frama-C, ACSL and Coq:** reference contracts, invariants and theorem designs.
  This plan does not introduce a new tool, import others' proof code, or assume
  an automatic proof bridge between languages or verifiers.

Runtime source and generic signatures stay unchanged. Every reused summary
requires a proved actual callee at the matching source/profile. Source fidelity,
refinement, full normal/unwind resources and the challenge's four UB categories
remain separate acceptance obligations.

## Execution and reporting

The original sort4 functional phase has closed. The owner approved stage 1b
after reviewing its results and the proposed next task. Stage1b has now completed
its hosted diagnostics and closed at the architecture decision; the original
approval does not authorize its proposed future verifier experiment. The separate
stage1c authorization explicitly excluded that patched route; stage1c is closed.
Its no-patch findings do not prove all unmodified-tool strategies impossible.

Stage 1b separates the two overlap questions: violation of an actual copy's
non-overlap requirement, and corruption of original values across individually
non-overlapping copies. Its contract must keep safety, ordering and resource
assumptions distinct. Its architecture deliverable is one concrete technical
option, not permission to implement that option.

Use [AGENTS.md](../../AGENTS.md) and the [runbook](AGENT-RUNBOOK.md) for autonomous
edit/commit/dispatch/inspection on GitHub-hosted Actions. Keep one relevant
experiment active, explicit budgets and exact-SHA evidence. At phase closeout,
report proven properties, actual domain, remaining safety obligations and the
next decision separately. No later phase, semantic tool change or external
publication is authorized by this roadmap.
