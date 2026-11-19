# Coordinator14:45 — hypotheses for network-r2 (offline)

The coordinator saw actual bounded N01 insertion-loop progress and proposes per-partition `#[kani::unwind(N+1)]`, direct network calls avoiding insertion dispatch, and checking whether length is concrete or symbolic with an assume. These are inputs to source analysis, not implementation instructions or established causal proof.

Root correction from exact published source: all four proof entries declare unwind36, and34 is the symbolic buffer size. N01 chooses symbolic usize then assumes0<=n<=1. The real helper source returns for len<2, so a feasible source execution does not reach insertion. The bounded progress text establishes symbolic exploration, with no timestamped phase-at-kill or MIR/assumption trace. Preserve that discrepancy explicitly. Evaluate constant-length lowering/pruning and model/oracle costs as hypotheses.
