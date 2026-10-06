# Abstract order and stability gate for `sort4_stable`

## Preexperiment card — stock VeriFast, not yet hosted checked

- **Actual obligation:** the repository `sort4_stable` at
  `library/core/src/slice/sort/shared/smallsort.rs:610–658`, blob
  `e555fce440872898e47fd5114f32eb15401d07df`, chooses `a,b,c,d`, then
  `min,max,unknown_left,unknown_right`, then `lo,hi` from five comparisons.
  [The shared index formulas](sort4-index.gh) transcribe lines 626–651; the
  four copies on lines 653–656 use the resulting order.
- **Falsifiable hypothesis:** if each comparison returns the strict order of
  four *unchanged* integer equivalence-class ranks, the exact choice network
  yields a permutation in nondecreasing rank order and retains increasing
  original occurrence IDs among equal ranks. No rank bounds are imposed.
- **Domain and full local post:** arbitrary verifier `int` ranks `r0..r3`,
  original logical IDs `0..3`, fixed rank comparison `<`, and static ranks
  across all five comparisons. The positive ghost lemma
  [`s4_rank_order_and_stability`](sort4-order-lemmas.c) proves `s4_final` and
  `s4_sorted_stable`: the four selected IDs each occur once; every adjacent
  output pair has smaller rank, or equal rank and increasing ID. With four
  slots, these adjacent facts give global nondecreasing ranks and stability.
  The lemma has no executable operations or unwind path. This is a functional
  normal-result theorem, not the normal/unwind resource post of the Rust call.
- **Tool profile:** unchanged official VeriFast 26.09, source
  `809de4596839b739dd999f9e462242c835e3af46`, pinned
  `nightly-2026-02-05` where applicable. No verifier patch, axiom, summary,
  memory model change or separate proof system. Compile/verification only in a
  manual GitHub-hosted Actions run; no local executable validation.
- **Expected positive:** `sort4-order-lemmas.c` verifies its ghost lemma's
  permutation and stable-order post. The proof splits Boolean choices and
  checks intermediate rank/ID inequalities.
- **Expected negative:** isolated [`sort4-order-negative.c`](sort4-order-negative.c)
  reaches `TARGET_ASSERTION`, then fails **there**: for four equal ranks, a
  mutant reverses only the two middle selected IDs, yielding `2,1`. A parser,
  setup, unrelated lemma or unreachable-path failure does not count.
- **Decision:** inspect full hosted logs. A positive pass and intended negative
  rejection accept only the abstract rank theorem. Correct ordinary annotation
  or proof errors with a new exact-SHA run. If the negative proves, quarantine
  the stock proof profile and preserve the reproducer. If unsupported, record
  the first causal blocker without claiming the theorem checked.

The rank abstraction covers every four-element instance of a *fixed strict weak
order*: the relation's incomparability classes are totally ordered; assign
successive integer ranks to the at most four classes. Two original values have
the same rank exactly when they are equivalent under that order, and `<` of
ranks agrees with the order. Original IDs remain attached to the values, so
equal-class occurrences stay distinguishable. This is a mathematical transfer
argument for the pure choice network; its correspondence with verifier-level
`T` values and actual callback answers still needs a checked bridge. In
particular, a legal `FnMut` may mutate state or panic. Functional application
requires that normal-returning calls preserve the keys/values and implement the
same fixed strict weak order throughout; these premises do not narrow the
general safety contract.

The theorem concerns **logical IDs**, including ZSTs whose distinct logical
occurrences may have identical numerical addresses. It proves no pointer
provenance, selection-callee behavior, reference validity, copy permission,
uninitialized-scratch handling, resource frame, panic restoration, or whole
Rust `sort4_stable` contract. No `T: Copy` or `T: Freeze` premise enters the
abstract theorem.
