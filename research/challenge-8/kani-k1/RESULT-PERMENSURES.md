# RESULT-PERMENSURES — G1 closed
Build `a338036e-c5d4-4e4e-afca-dccd5bc3d336`, source `d86897746f1b3d6c0bbfed3ca3c03e96a46dbe96`, owner k1-merge; Cloud FAILURE, summary COMPLETE, gate/expectations false.
Model claim only for u8/u64; other T get trivial ensures. Established bounded evidence below is u8 only; u64 remains unproved here.
Exact ensures (runtime body/signature/requires/modifies unchanged):
```rust
#[cfg_attr(kani, crate::kani::ensures(|_|
    !<F as PairPermutation<T>>::has_model()
        || pair_values_are_permuted(
            old(unsafe { <F as PairPermutation<T>>::pair(v_base, a_pos, b_pos) }),
            unsafe { <F as PairPermutation<T>>::pair(v_base, a_pos, b_pos) },
        )
))]
```
Helper: `(after.0 == before.0 && after.1 == before.1) || (after.0 == before.1 && after.1 == before.0)`; full scalar snapshots, equal positions unchanged.

| G1 row | Status | Time s | Failed/total; covers |
| --- | --- | --- | --- |
| PFC u8 backing17 | SUCCESS | 33.189846 | 0/289; 7/7 |
| PFC u8 backing32 | SUCCESS | 36.972645 | 0/289; 7/7 |
| consumer u8 N17 | SUCCESS | 400.42688 | 0/463; 4/5 (1 unreachable) |
| consumer u8 N32 | TIMEOUT | not reported | not reported |
| corrupt consumer u8 N17 | TIMEOUT | not reported | expected mask failure NOT established |
| PFC u8 backing18 | SUCCESS | 34.21762 | 0/289; 7/7 |
| consumer u8 N18 | SUCCESS | 200.49629 | 0/463; 5/5 |

Domains match: same u8/function-item arbitrary reading comparator and exact backing N; full-value/any-position PFCs subsume consumers' fixed distinct identity tags. N17/N18 composition passed; N32 PFC alone gives no consumer credit.
Only swap is stub_verified; insertion/merge execute. Explicit order-violation panic is cut: normal-return permutation, no sortedness/panic-unwinding proof. N17 has no merge by source route; terse evidence does not label its unreachable cover individually.
Both timeouts have exact diagnostic `CBMC timed out.` at kani.log:2716/2724 via bounded k1g log-grep; configured limit 600 s each. Compilation succeeded, so the specialization-only repair authorization does not apply; no repair/retry/G2 was run.
N17 400.43 s versus task-reported PERMTAGS 335 s: +65.43 s (+19.5%); no speedup observed. Historical reference is source-reported, not independently reproduced or a controlled causal comparison.
N32 was not reached within 600 s by this composition; feasibility remains unresolved. Corruption control is unvalidated. Prepared backing4/9/13/24 PFCs and N24 consumer were not submitted; existing safety PFCs were retained, not rerun.
Source/request/build identities, standard4 pool and protected tooling matched base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`; checks off for uninit/value-validity. Verify wall 33:11.00; max RSS 3649684 KiB; N32 CBMC peak 2.69 GiB; OOM scan none_seen.
Own cost $0.5535, reserve $0, below $3.00; one authorized build consumed. No further dispatch without new coordinator authorization. Detailed packet and bounded evidence coordinates: PREBUILD-PERMENSURES.md.
