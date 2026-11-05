# RESULT-PERMENSURES — G1/G2 closed
G1 `a338036e-c5d4-4e4e-afca-dccd5bc3d336`, source `d86897746f1b3d6c0bbfed3ca3c03e96a46dbe96`: Cloud FAILURE, COMPLETE, gate false.
G2 `4662b386-b6a8-471b-a1c8-833d26262f36`, source `872c963fec2a18a8d217d7eb322dd1595ec9099e`: Cloud SUCCESS, COMPLETE, gate/expectations true; both k1-merge.
Model claim only for u8/u64; other T have trivial ensures. Established bounded evidence is u8 only; u64 remains unproved here.
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

| Stage / row | Status | Time s | Failed/total; covers |
| --- | --- | --- | --- |
| G1 PFC u8 backing17 | SUCCESS | 33.189846 | 0/289; 7/7 |
| G1 PFC u8 backing32 | SUCCESS | 36.972645 | 0/289; 7/7 |
| G1 consumer u8 N17 | SUCCESS | 400.42688 | 0/463; 4/5 (1 unreachable) |
| G1 consumer u8 N32 | TIMEOUT | not reported | not reported |
| G1 corrupt consumer u8 N17 | TIMEOUT | not reported | expected mask failure not established |
| G1 PFC u8 backing18 | SUCCESS | 34.21762 | 0/289; 7/7 |
| G1 consumer u8 N18 | SUCCESS | 200.49629 | 0/463; 5/5 |
| G2 PFC u8 backing24 | SUCCESS | 34.7287 | 0/289; 7/7 |
| G2 consumer u8 N24 | SUCCESS | 498.13196 | 0/463; 5/5 |
| G2 PFC u8 backing9 | SUCCESS | 31.553417 | 0/289; 7/7 |
| G2 corrupt consumer u8 N9 | FAILED (expected) | 25.809164 | 1/463; 1/5 (4 unreachable) |

Domains match: same u8/function-item arbitrary reading comparator and exact backing N; full-value/any-position PFCs subsume fixed identity-tag consumers. N17/N18/N24 composition passed; N9 control has matching backing9 PFC.
Only swap is stub_verified; insertion/merge execute; explicit order-violation panic is cut. Claim: normal-return tag permutation, not sortedness/panic unwinding/arbitrary payloads. N9's sole failed check is `permensures network tag mask` at permensures.rs:92; positive G2 covers all satisfied.
N17 400.43 s versus task-reported PERMTAGS 335 s: +65.43 s (+19.5%), no speedup observed; historical reference not independently reproduced or a controlled comparison. N24: 498.13 s. Backing4/13 PFCs remain unrun; existing safety PFCs retained, not rerun.
Both source/request/build identities, standard4 pool and tooling matched base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`; uninit/value-validity checks off. Own G1/G2 costs $0.5535/$0.2430, total $0.7965, reserve $0 < $3.00.
N32 composition remains unresolved: G1 PFC passes but consumer times out at configured 600 s; G1 N17 control also timed out (`CBMC timed out.`). G2 validates smaller N9 control. Both primary builds consumed; no compile error, repair or further dispatch. Details: PREBUILD-PERMENSURES.md and PREBUILD-PERMENSURES-G2.md.
