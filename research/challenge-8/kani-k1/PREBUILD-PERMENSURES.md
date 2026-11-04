# PERMENSURES G1 — exact PRE-BUILD packet

Historical preparation packet; G1 has completed. Actual owner, source and outcome are recorded below.
Worktree `/root/verify-rust-std-kani-permensures`, branch
`experiment/kani-k1-permensures-20261105`, task commit `c8d85f424494cd6c00680a74b15df4bffac0a968`.
Library commit `7e7c80142fdd6be52fc965d9770d30e4b4c0657b`.
Tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`;
Kani pin `cd355b0bccd32300713bc2ce4f765dafa1510607`.

The coordinator accepted the Cell counterexample and replaced the universal T claim with a
cfg(kani) trait model using specialization, explicitly referencing the ENSURES mechanism at
`c0fbf091c42025e6eb5144bf2ca839f43fbe63e2`. Only that named mechanism was consulted there;
no competing PR, branch, diff, or PERMTAGS code was opened. The coordinator also authorized
all matching consumer backings and up to seven G1 rows, including an extra PFC/consumer pair.

## Contract and scope

`PairPermutation<T>` is implemented for every F with default `has_model() == false` and a
constant dummy pair `(0, 0)` that does not read T. Specializations for u8 and u64 return true
and snapshot both complete scalar values using `ptr::read`, represented exactly as two u64s.
No PartialEq implementation of a generic T, padding-byte read, comparator model or ordering
assumption is used. The specialization depends only on T, so any F has the same contract.
The generic function signature and its runtime body remain byte-for-byte unchanged.

```rust
#[cfg_attr(kani, crate::kani::ensures(|_|
    !<F as PairPermutation<T>>::has_model()
        || pair_values_are_permuted(
            old(unsafe { <F as PairPermutation<T>>::pair(v_base, a_pos, b_pos) }),
            unsafe { <F as PairPermutation<T>>::pair(v_base, a_pos, b_pos) },
        )
))]
```

`pair_values_are_permuted(before, after)` means exactly
`(after.0 == before.0 && after.1 == before.1) || (after.0 == before.1 && after.1 == before.0)`.
Equal positions have identical pre-values, so this also entails that their value is unchanged.
The old expression snapshots scalar values before the callback. u8/u64 have no interior
mutability through shared references. Other T, including Cell and byte arrays, have only the
trivial ensures; the default snapshot is harmless even if old expressions are evaluated eagerly.
This is a normal-return claim for valid Rust callbacks, not a guarantee for undefined behavior.
The existing requires/modifies and all existing safety-PFC roots remain unchanged. The new
u64 model has no newly dispatched PFC in G1; its verification is not claimed by u8 evidence.

## Exact G1 request

File `RUN-REQUEST.json`, SHA-256 `31f2f00a4ca32552a89f41861a78f65397804268b3a4cbb3392c18b95ba73b0c`.
Request `permensures-g1-20261105`, owner `k1-network`, kind diagnostic, standard4 pool,
controls true, jobs 1, ten minutes per row. The owner is selected for the review packet;
its availability is not inferred from historical runs. Dispatch requires coordinator GO and
that stable owner to be free; changing owner/request requires an updated exact review.
Names below have prefix `slice::sort::shared::smallsort::verify::permensures::`.

| Root | Expect | Domain |
| --- | --- | --- |
| swap_permutation_u8_backing17 | SUCCESS | full u8 backing17, symbolic in-bounds a/b, including equal |
| swap_permutation_u8_backing32 | SUCCESS | same with backing32 |
| unstable_network_permutation_u8_n17 | SUCCESS | distinct tags 0..16, actual Unstable entry, verified swap |
| unstable_network_permutation_u8_n32 | SUCCESS | distinct tags 0..31, actual Unstable entry, verified swap |
| rejects_network_corruption_u8_n17 | FAILED, `permensures network tag mask` | same N17 consumer, then v[0] = v[1] |
| swap_permutation_u8_backing18 | SUCCESS | same PFC with backing18 |
| unstable_network_permutation_u8_n18 | SUCCESS | distinct tags 0..17, first network length using merge |

All roots use unwind40. A single private function item `arbitrary_less(&u8, &u8) -> bool`
reads both arguments volatile and returns an independent kani::any bool on each invocation.
Every PFC and every consumer uses precisely this F, with no cast to a function pointer.
PFCs range over the full u8 array and any a/b < N. They assert model activation and the
unchanged non-pair frame; covers request both callback outcomes, equal/increasing/decreasing
positions, an exchange of distinct values, and normal return. SUCCESS and covers must be
inspected separately; no cover is asserted reached before a build exists.

Consumers construct fixed distinct identity tags 0..N-1 in backing exactly N, check model
activation, run `<u8 as UnstableSmallSortTypeImpl>::small_sort`, then check every output tag
is in range and its N-bit presence mask is full. With N slots and N distinct possible tags,
the full mask entails exact permutation. These are tag-lineage checks, not sortedness or
an independent proof over arbitrary original payload values/initial tag permutations.
They form a subset of the full u8 input domain of their corresponding PFCs.
Only swap_if_less uses stub_verified. Real network dispatch, insertion, merge and copies run.
For N >= 18, the existing pattern cuts only panic_on_ord_violation: cover, assume(false),
unreachable. No comparator answer is constrained before that boundary; the claim is limited
to normal returns and excludes panic unwinding. The same stub is declared for N17/control,
where that boundary is not on the route. Return and checked-mask covers request nonvacuity.
The negative duplicates one post-sort element, leaving one tag absent; its expected failure
is bound to the mask property, not an arbitrary panic, safety check or unwinding failure.

## Remaining prepared domains and interpretation

Separate new PFC roots exist for u8 backings 4, 9, 13, 17, 18, 24, 32. Consumers exist for
N17, N18, N24, N32. Only the seven rows above are submitted by G1; in particular backing24/N24
and backing4/9/13 remain unrun and need G2 review/GO. A failed/timed-out PFC cannot give proof
credit to its consumer even if that consumer passes. No transfer between backing sizes is
assumed. The optional u64 model is present but not an established proof domain of this packet.
The task reports PERMTAGS N17 at 335 s with real swaps; that is a source-reported reference,
not independently re-established here. Report the stubbed N17 time beside 335 s only after G1;
no speedup or N32 composition success is presumed. No new unstubbed benchmark is dispatched.

## Validation, budget and stop

The existing request validator accepted all seven rows with standard4 requirements.
Static checks confirmed every requested root is declared; only the corruption root expects
FAILED and names its mask property. Removing only the cfg(kani) trait/helper and ensures
restores smallsort.rs byte-for-byte to the task HEAD. Existing safety-PFC source is identical.
Protected lane paths match the tooling base; git diff --check passes. No local cargo/rustc/
Kani/CBMC, credentials, raw logs, tooling/workflow changes or subagents were used.
These checks establish packet consistency, not Rust compilation or successful verification.

Reserve: (7*10+30) min * $0.0135/min = $1.3500. Own spent $0, cap $3.00.
Preparation budget snapshot: 230 builds, used $97.4805, reserved $2.4300; with G1 reserve
at most $101.2605 < project cap $118.96. Dispatcher refreshes accounting before submission.
At most two primary builds, G2 only with new GO; at most one compile-error repair per build,
always within remaining own/project caps and exact-review restrictions.
After this library/research [skip ci] publication and non-force push, print
`PRE-BUILD REVIEW <full published HEAD>` as the final line and stop. Do not dispatch yet.
After exact GO, use k1g.sh dispatch on this branch, then k1g.sh watch BUILD and end the turn.
After its completion, use only bounded K-1 evidence, verify source/tooling identities and
covers, update RESULT-PERMENSURES.md (<=35 lines), publish REVIEW REQUEST / completion, stop.


## Authorized dispatch and observed G1 outcome

The coordinator gave GO for exact prepared HEAD
`097b2b70353996edcb428daf0f34c1fd5851a85b`, conditional on a free owner. The coordinator
identified k1-network as occupied by ENSURES G2 and k1-merge by VEIGHTINTEG
`03d45e6a-0553-414e-83ea-6f6c9ce87778`. A gate-only watch used
`K1_CACHE=/tmp/kani-k1-permensures-veightinteg-gate`; its completion notification was SUCCESS.
No dependency summary, source or diff was opened. The explicit authorization permitted
selecting k1-merge on release via a separate [skip ci] agent-only commit.

Commit `d86897746f1b3d6c0bbfed3ca3c03e96a46dbe96` changes exactly that request agent from
k1-network to k1-merge. The seven roots and all verification settings are unchanged; the
validator accepted the request again. Actual request SHA-256 is
`b50523137af441883f518375ce6dcae05a850db8cf6595aa17127e118dc5ab3f`.
The non-force push preceded the single dispatch as build
`a338036e-c5d4-4e4e-afca-dccd5bc3d336`; own watch was registered and the turn ended.
Dispatch accounting: used $98.5470, reserved including this build $1.3500, maximum
$99.8970 < project cap $118.96. No competing source or credentials were read.

The completion notification reported Cloud FAILURE. Bounded summary is COMPLETE, with
Kani exit 1, gate false and expectations false; it records successful compilation/run setup,
not a compiler error. The seven-row page has total=7, offset=0, next_offset=done and binds
this exact request hash, source SHA and build UUID. check-tooling passed standard4 pool,
all protected lane paths, source/build binding and all six tooling hashes against
`59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`.

| Root | Status | Time s | Failed/total | Unreachable | Covers |
| --- | --- | --- | --- | --- | --- |
| swap_permutation_u8_backing17 | SUCCESS | 33.189846 | 0/289 | 4 | 7/7 |
| swap_permutation_u8_backing32 | SUCCESS | 36.972645 | 0/289 | 4 | 7/7 |
| unstable_network_permutation_u8_n17 | SUCCESS | 400.42688 | 0/463 | 20 | 4/5 (1 unreachable) |
| unstable_network_permutation_u8_n32 | TIMEOUT | not reported | not reported | not reported | not reported |
| rejects_network_corruption_u8_n17 | TIMEOUT | not reported | not reported | not reported | not reported |
| swap_permutation_u8_backing18 | SUCCESS | 34.21762 | 0/289 | 4 | 7/7 |
| unstable_network_permutation_u8_n18 | SUCCESS | 200.49629 | 0/463 | 14 | 5/5 |

Bounded k1g log-grep locates the control at kani.log:2710 and its timeout at 2716;
N32 starts at 2718 and times out at 2724. Both exact terminal diagnostics are:
`CBMC timed out. You may want to rerun your proof with a larger timeout or use stubbing to reduce the size of the code the verifier reasons about.`
No verification time/check/cover result is reported for either timeout; the request limit
is 600 s, not an observed completed-proof time. In particular the expected failure of
`permensures network tag mask` was not established: TIMEOUT does not satisfy the control.

A second bounded grep locates N17's 4/5 cover summary at line2733, explicitly one unreachable;
N18's 5/5 at2746 and PFC backing18/32/17 7/7 at2757/2768/2779. It does not expose individual
cover labels. The source route has no merge at N17, making the declared order-panic cover
unreachable there; this explains the aggregate count by source inspection, not by a separately
reported per-label trace. All seven PFC covers and all five N18 covers were satisfied.
Unreachable checks are recorded separately and do not add independent proof credit.

The conditional model compiled with the pinned min_specialization toolchain. Thus the narrow
repair authorization (one repair only for a T-specialization compile error) does not apply.
No repair, unchanged retry or G2 was dispatched. The latest instruction authorized one Build;
any further experiment requires a new coordinator decision.

Bounded results establish the real swap's new permutation ensures for full u8 inputs and
symbolic positions on backings17,18,32. Consumers use the exact same T/F/backing and prove
the fixed distinct-tag permutation at N17/N18 on normal return, with real insertion/merge
and only the explicit order-violation panic cut. N32's matching PFC passes but its consumer
times out, so N32 composition is unresolved. The negative control is also unresolved.
u64 has a model but no proof result in this packet; no claim is made for other T.
Backing4/9/13/24 PFCs and N24 consumer remain prepared and unsubmitted; existing safety PFC
roots were preserved but not rerun. This does not establish a universal T/F theorem,
arbitrary-payload consumer theorem, panic unwinding or uninit/value-validity guarantees.

The stubbed N17 time 400.42688 s is 65.42688 s (19.53%) above the task-reported PERMTAGS
real-body reference 335 s. There is no observed speedup in this comparison; the historical
reference was not independently reproduced and does not establish a controlled causal effect.
N18 takes 200.49629 s; no direct N18 baseline is available here. Current composition did not
reach N32 within the configured ten-minute limit; impossibility is not inferred from timeout.

Whole verify run including compilation: 33:11.00, max RSS 3649684 KiB; sampled per-CBMC peak
2.69 GiB attributed to N32. dmesg OOM scan none_seen is not proof of memory headroom.
Bounded `k1g.sh budget BUILD` reports `1 0.5535 0.0000`: actual own cost $0.5535, reserve
zero, under the $3.00 own cap. Reporting changes only this document and RESULT-PERMENSURES.md
(<=35 lines). Publish [skip ci], non-force push, REVIEW REQUEST, then stop without more builds.
