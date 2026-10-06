# Challenge 8: approved roadmap

Approved by the owner on 2026-10-06 after review of the C verification research.
This decision supersedes the insertion-first ordering in earlier handoffs.
[STATUS.md](STATUS.md) remains the current execution checkpoint.
Only the bounded [sort4 phase](SORT4-PHASE.md) is authorized for execution;
the later stages below are priorities for subsequent decisions.

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

The immediate aim is a useful result with a precise boundary, followed by a
decision on generic safety. It is not a commitment to build a general-purpose
Rust verifier or a Rust-to-C translation pipeline.

## Priorities and advancement criteria

| Order | Target | Intended result | Gate before moving further |
| --- | --- | --- | --- |
| 1 — authorized | `sort4_stable` | Full target contract and caller/aliasing review; actual-body Kani sortedness/permutation for four arbitrary i32 inputs; separate tagged-item stability proof; generic-safety feasibility assessment | Close [SORT4-PHASE](SORT4-PHASE.md) with exact evidence, remaining UB/ownership/comparator gaps and a recommended decision. A functional result alone does not close this public safety target. |
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

- **Kani:** unchanged repository pin, actual-source finite functional proofs and
  explicitly identified memory-check evidence. See the phase for exact profiles.
- **VeriFast:** unchanged pinned release for a justified generic-safety
  feasibility diagnostic, only after existing evidence leaves a concrete new
  question. Historical patched successes stay conditional on their recorded
  source/profile; they are not permissions to import those patches.
- **Frama-C, ACSL and Coq:** reference contracts, invariants and theorem designs.
  This plan does not introduce a new tool, import others' proof code, or assume
  an automatic proof bridge between languages or verifiers.

Runtime source and generic signatures stay unchanged. Every reused summary
requires a proved actual callee at the matching source/profile. Source fidelity,
refinement, full normal/unwind resources and the challenge's four UB categories
remain separate acceptance obligations.

## Execution and reporting

The owner approved this roadmap and the bounded sort4 phase. The documentation
iteration records that approval without running experiments. A continuation
agent may implement and run the named phase without asking for the same approval
again, subject to any newer instruction or checkpoint.

Use [AGENTS.md](../../AGENTS.md) and the [runbook](AGENT-RUNBOOK.md) for autonomous
edit/commit/dispatch/inspection on GitHub-hosted Actions. Keep one relevant
experiment active, explicit budgets and exact-SHA evidence. At phase closeout,
report proven properties, actual domain, remaining safety obligations and the
next decision separately. No later phase, semantic tool change or external
publication is authorized by this roadmap.
