# RESULT-PERMENSURES — G1/G2/G3 closed

Builds: G1 `a338036e-c5d4-4e4e-afca-dccd5bc3d336` FAILURE; G2 `4662b386-b6a8-471b-a1c8-833d26262f36` SUCCESS; G3 `5fb82a5e-fa7c-403a-bd85-84a97a4005b0` FAILURE. Summaries COMPLETE, gates false/true/false, owner k1-merge; exact sources/requests in phase packets.
Model claim only for u8/u64; other T have trivial ensures. Established bounded evidence is u8 only; u64 unproved here. Exact ensures (runtime body/signature/requires/modifies unchanged):
```rust
#[cfg_attr(kani, crate::kani::ensures(|_|
    !<F as PairPermutation<T>>::has_model()
        || pair_values_are_permuted(
            old(unsafe { <F as PairPermutation<T>>::pair(v_base, a_pos, b_pos) }),
            unsafe { <F as PairPermutation<T>>::pair(v_base, a_pos, b_pos) },
        )
))]
```
Helper: `(after.0 == before.0 && after.1 == before.1) || (after.0 == before.1 && after.1 == before.0)`; complete scalar snapshots, equal positions unchanged.

| Stage / row | Status | Time s | Failed/total; covers |
| --- | --- | --- | --- |
| G1 PFC u8 backing17 | SUCCESS | 33.189846 | 0/289; 7/7 |
| G1 PFC u8 backing32 | SUCCESS | 36.972645 | 0/289; 7/7 |
| G1 consumer u8 N17 | SUCCESS | 400.42688 | 0/463; 4/5 (1 unreachable) |
| G1 consumer u8 N32 default | TIMEOUT | not reported | not reported |
| G1 corrupt consumer u8 N17 | TIMEOUT | not reported | expected mask failure not established |
| G1 PFC u8 backing18 | SUCCESS | 34.21762 | 0/289; 7/7 |
| G1 consumer u8 N18 | SUCCESS | 200.49629 | 0/463; 5/5 |
| G2 PFC u8 backing24 | SUCCESS | 34.7287 | 0/289; 7/7 |
| G2 consumer u8 N24 | SUCCESS | 498.13196 | 0/463; 5/5 |
| G2 PFC u8 backing9 | SUCCESS | 31.553417 | 0/289; 7/7 |
| G2 corrupt consumer u8 N9 | FAILED (expected) | 25.809164 | 1/463; 1/5 (4 unreachable) |
| G3 consumer u8 N32 kissat | TIMEOUT | not reported | not reported |
| G3 PFC u8 backing28 default | SUCCESS | 34.31302 | 0/289; 7/7 |
| G3 consumer u8 N28 default | TIMEOUT | not reported | not reported |

Domains match: same u8/function-item arbitrary reading comparator and exact backing N; full-value/any-position PFCs subsume fixed identity-tag consumers. Only swap is stub_verified; real insertion/merge execute, explicit order-panic is cut: normal-return permutation, no sortedness/panic-unwinding/arbitrary-payload theorem. N9's sole failed check: `permensures network tag mask` (G2 source line92); backing9 PFC matches. Backing4/13 PFCs unrun; old safety PFCs preserved, not rerun.
N17 400.43 s versus task-reported PERMTAGS 335 s: +65.43 s (+19.5%), no speedup observed; historical reference not independently reproduced or a controlled comparison. All source/request/build identities, standard4 pools and tooling match base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`; uninit/value-validity checks off. Own G1/G2/G3 costs $0.5535/$0.2430/$0.3915, total $1.1880, reserve $0 < raised cap $4.00.
Composition established at N17/N18/N24; N28 default and N32 default/kissat remain unresolved after configured 600-s timeouts (`CBMC timed out.`), despite successful matching PFCs. No impossibility is inferred. Three authorized builds consumed, no compile error or repair; no further dispatch. Full identities/evidence/limits: PREBUILD-PERMENSURES.md, PREBUILD-PERMENSURES-G2.md, PREBUILD-PERMENSURES-G3.md.
