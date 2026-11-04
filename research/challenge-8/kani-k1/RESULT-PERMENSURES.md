# RESULT-PERMENSURES — prepared, not submitted
No build or proof result yet; exact G1 packet awaits PRE-BUILD review/GO.
Claim scope: conditional model only for u8/u64; other T have trivial ensures. G1 verifies u8 only; u64 is unproved here.
Exact ensures on real swap_if_less (body/signature/requires/modifies unchanged):
```rust
#[cfg_attr(kani, crate::kani::ensures(|_|
    !<F as PairPermutation<T>>::has_model()
        || pair_values_are_permuted(
            old(unsafe { <F as PairPermutation<T>>::pair(v_base, a_pos, b_pos) }),
            unsafe { <F as PairPermutation<T>>::pair(v_base, a_pos, b_pos) },
        )
))]
```
The helper accepts exactly unchanged or exchanged full scalar pairs; a==b implies unchanged value.
| G1 row | Expected | Observed |
| --- | --- | --- |
| PFC u8 backing17 | SUCCESS | NOT_SUBMITTED |
| PFC u8 backing32 | SUCCESS | NOT_SUBMITTED |
| consumer u8 N17 | SUCCESS | NOT_SUBMITTED |
| consumer u8 N32 | SUCCESS | NOT_SUBMITTED |
| corrupt consumer u8 N17 | FAILED: permensures network tag mask | NOT_SUBMITTED |
| PFC u8 backing18 | SUCCESS | NOT_SUBMITTED |
| consumer u8 N18 | SUCCESS | NOT_SUBMITTED |
Domains: same u8/function-item arbitrary reading comparator and exact backing N; PFC full values/any in-bounds positions subsume fixed distinct identity tags in consumers.
Prepared, unsubmitted: PFC backing4/9/13/24 and consumer N24. No transfer across backing sizes is claimed.
Only swap uses verified stubs; real insertion/merge execute. Explicit order-violation panic is cut; claims concern normal return, without sortedness or panic-unwinding proof.
Task reports PERMTAGS N17 real-body time 335 s; reference is source-reported, not independently re-established. Stubbed comparison is pending.
N32 composition feasibility: not established until matching backing32 PFC and N32 consumer both pass, with covers inspected.
Uninit/value-validity checks remain disabled by existing tooling; no universal T/F or arbitrary-payload consumer theorem is claimed.
Own cap $3.00; G1 reserve $1.3500, spent $0. G2 requires new GO; no build authorized by this document.
