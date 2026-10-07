# Independent bidirectional merge proofs

Geometry and functional stages accepted for the exact scalar mathematical model
of pinned SmallSort merge_up/merge_down/bidirectional_merge, arbitrary n>=2.
Actual Rust transfer remains open. Worktree/branch isolated; unchanged stock
VeriFast26.09, hosted-only executable checks, original total1800 jobsecond budget.

- [STATUS](STATUS.md): current accepted proof SHAs, runs, budget and boundaries.
- [RESULTS](RESULTS.md): exact A/B statements, assumptions and acceptance evidence.
- [Original geometry report](GEOMETRY-RESULTS.md): retained G2 baseline.
- [PLAN](PLAN.md), [journal](EXPERIMENT-LOG.md), [coverage](coverage.md).
- [SOURCE-MAP](SOURCE-MAP.md): pinned calls, cursors and occurrence schedule.
- [INTEGRATION](INTEGRATION.md): scalar/pointer guard and remaining Rust obligations.

Proof components: unchanged geometry.c; functional-ids.c guard-conditional exact
permutation/write theorem; functional-order.c exact stable rank-key induction;
functional-swo.c constructive general SWO pullback, using unchanged rechecked
networks/swo-rank.c bodies. The latter are shared mathematical lemmas; no network
adapter runs or network budget were reopened.

Own workflows are manual selections merge_geometry, merge_functional_ids,
merge_order on challenge-8/merge, with exact published SHA and one own run at a
time. Completed results need no additional run for documentation closeout.
