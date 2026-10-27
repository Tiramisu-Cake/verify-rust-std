# Towards #56: SmallSort verification disclosure (draft)

This is a review draft, not a claim that Challenge 8 is resolved. Submission remains conditional on the final requirements table, Linux/macOS partitions and the remaining correctness work. The working title is **Towards #56**. See [R8 §6–7][R8] and the [requirements table](W3-REQUIREMENTS.md).

Evidence below is source-reported: this documentation task did not rerun verification. Document review of `f2d97de0`/`d4ab49e9` returned GO_WITH_NITS; the coordinator supplied the corrections incorporated here on 2026-10-27. Final-code R9 for K-16s/K-11s/O3-s (`bf3e03f7`) is still in progress; those families are not accepted solely on the wave report’s blanket statement. Historical accepted results require gate true, completed covers, tooling checks and R9 review, as stated in the [wave 2 report][W2]. A diagnostic SUCCESS, an archive-integrity check, or a resource-lane gate does not establish acceptance in the submitted CI domain. The final integrated source SHA and its complete evidence index are **TODO — W3-L1, L1-6/L1-7** ([R8][R8]).

## Scope

The targets are the three `small_sort` trait methods (`StableSmallSortTypeImpl`, `UnstableSmallSortTypeImpl`, `UnstableSmallSortFreezeTypeImpl`), `swap_if_less`, `insertion_sort_shift_left`, `sort4_stable`, and `has_efficient_in_place_swap`. Reachable internal bodies include fallback, general/general-with-scratch, network, insertion tails, sort8, sort9/sort13 and bidirectional merge with merge_up/merge_down. Verification uses real bodies or separately checked contracts; unwind execution of `CopyOnDrop::drop` is excluded. These targets and the required domains come from the [requirements interpretation §2 A/B][REQ]; implemented coverage is recorded in [W1][W1] and [W2 §1][W2].

The small-sort domain is every length up to its route threshold: 0..=16 for fallback/stable default and 0..=32 for general/network/stable-Freeze. This is the project's interpretation of a valid trait call, not a committee ruling. Larger small-sort calls are outside this submission's claimed domain. `insertion_sort_shift_left` has no such threshold; its bounded results below do not prove safety for arbitrary lengths. See [requirements B1–B5][REQ] and [R8 §1][R8].

| Property / route | Measured domain and review status | Evidence |
|---|---|---|
| O1-A, no failed Kani checks in the stated comparator model: general and stable-Freeze | u64, every N0..32; corresponding transparent non-Copy trait/general paths | CircleCI 13 GiB, [W1][W1] and [W2, merge jobs 79–92][W2] |
| O1-A: network | u64, every N0..32 | CircleCI 13 GiB, [W1 short lengths][W1], [W2 network jobs 80/82][W2] |
| Fallback / stable default safety | K-16s: selected N0,1,2,15,16 for `Cell<i32>` and unstable `[u8;86]`; O3: every N0..16 for `Cell<K13Tagged>` | CircleCI 13 GiB, [K-16s and O3 job104][NET], [W2][W2]; final-code R9 `bf3e03f7` pending (coordinator, 2026-10-27) |
| Sortedness **and** full-value permutation: general / stable-Freeze | u64 N0..12 and N16; u8 N0..13 and N16 | CircleCI 13 GiB, [W2 correctness table][W2]; checked merge contracts at matching lengths, R4 |
| Sortedness and permutation: network | u64 N0..14; u8 N0..15. N0..8 are direct end-to-end proofs; for N9..15 permutation is composed from the structural network argument (below) and separately proved insertion-tail permutation, with full-route sortedness proved separately | CircleCI 13 GiB, [W2 correctness table][W2], [network night review][NET] |
| Sortedness and permutation: direct fallback | u64 N0..7; u8 N0..8 | CircleCI 13 GiB, [W2 correctness table][W2] |
| Insertion safety B4 | u64 N1..15, all valid offsets; N16..20 offset 1 | CircleCI 13 GiB, [network jobs 107–113][NET]; final-code R9 `bf3e03f7` pending (coordinator, 2026-10-27) |
| B4 / O3 split families | N13..18 all offsets; B4 N19 offsets 1..4; N20 offsets 1..4 and 17..20 | Cloud Build 16 GB, [builds d989b725, ae249f1f, bb656284, 64e7da65][L1], gate true; grouped template R9 GO `d5464a48`; the earlier ungrouped K-11s/O3-s template still awaits final-code R9 `bf3e03f7` |
| sort4, two separate checks | `proof_for_contract` with a pure strict comparator, plus ordinary safety proof with arbitrary comparator; u64 and `[u8;16]`, N4 | Cloud Build 16 GB, [build d065eab6-9c2e-4cf5-9022-67b2589d18f7][L1], gate true, R9 GO `ca32e652` |
| Efficient in-place swap predicate | the ten types enumerated in `w3_efficient_swap_c3`, including ZST | Cloud Build 16 GB, [build 70902589-d488-498d-9595-278e48013138][L1], cover 10/10, gate true, R9 GO `163cc955` |

Correctness gaps include fallback u64 N8..16/u8 N9..16, general/stable u64 N13..15/u8 N14..15, and merge routes N17..32. Network full correctness remains open above u64 N14/u8 N15: separate u8 sortedness at N16/17 does not establish tail permutation. **TODO — W3-L2, L2-1/L2-2:** determine which gaps can be closed. The split B4/O3 groups still awaiting results are **TODO — W3-L1, L1-5**. Baseline build `65a99021-7199-40e5-859d-4d0d5bc0c599` timed out at 1800 s for both old Tagged N20/N24 (gate false, no proof). The paired new-formulation build `9838655b-b07e-49b5-b50e-f89fbc751aea` and final split build `c122daa1-331e-4964-ac65-ffecab5df17e` have no result in the source snapshots used here; none of these pending/timeout rows is counted ([L2 result][L2], [L1 result][L1]).

## Type matrix (C3)

Monomorphizations are representatives of dispatch branches, not a proof for every `Sized T`. The following are the actual K-16s sample sets: G = {0,1,2,7,8,15,16,17,31,32}, S = {0,1,2,15,16}, and U = {8,9,12,13,17,18,31,32}. These are boundary/transition samples, not all intermediate lengths. Full u64 length coverage comes from separate O1 families. K-16s is documented in [network jobs 85–101 and final matrix][NET], with measurement gates reported in [W2 §1][W2]. The coordinator confirmed on 2026-10-27 that the final verdict for `bf3e03f7` had not been recorded; independent R9 is in progress. Final acceptance of K-16s/K-11s/O3-s remains pending.

| Type | Actual dispatch / callee distinction | Measured scope and limit |
|---|---|---|
| `()` | Freeze/Copy, size 0: unstable network, stable general; efficient swap true | Predicate only is accepted in [build 70902589][L1]. Trait-level sort results are diagnostic; see ZST below. |
| `u8` | unstable network, stable general; size≤8, size≤16, align 1 | K-16s unstable U / stable G, [jobs88/89/91][NET]; correctness only in the scope table above. |
| `i32` | Expected unstable network / stable general from dispatch | **TODO — W3-L1, L1-6:** identify or add a separately evidenced i32 instantiation. None was identified in the reports read for this draft; `Cell<i32>` covers a different branch. [Required by C3][REQ]. |
| `u64` | unstable network, stable general; size 8 boundary, align 8 | All lengths for O1; bounded correctness as above, [W1][W1]/[W2][W2]. |
| `u128` | unstable general, stable general; >8 and ≤16, presort8 for N≥16 | G on both routes, [jobs89/91/94][NET]. This represents the 9..16-byte interval; not full C3 correctness. |
| `[u8;16]` | general on both routes; presort8 size boundary | G on both routes, [jobs93–95][NET]; sort4 contract/arbitrary pair also [build d065eab6][L1]. |
| `[u8;17]` | general on both routes; presort4 for N≥16 | G on both routes, [jobs95–97][NET]. |
| `[u8;85]` | last size admitted to unstable general; stable general | G on both routes, [jobs99/100][NET]. Both separate sort4 checks TIMEOUT at 600 s in [build 9a62b6cf-b26c-41c7-a6a3-3f333f4fb402][L1]; no accepted sort4 proof for this instantiation. |
| `[u8;86]` | unstable fallback≤16; stable Freeze still general-with-scratch≤32 | Unstable S / stable G, [jobs100/101][NET]. The fallback size test does not apply to the stable Freeze route. |
| `Cell<i32>` | !Freeze, stable default / unstable fallback≤16 | S in K-16s, [job98][NET]. The additional mutating O3 families use `Cell<K13Tagged{key:u8,tag:u8}>`, not `Cell<i32>`; they do not establish this exact instantiation for every length. |
| Freeze !Copy with nontrivial Drop (`W2Drop(u8)`) | unstable general despite size≤8; stable general | G on both routes, [jobs97/98][NET]. Normal-return Drop/permutation checks are separate, below. |

For the two-cell `swap_if_less` contract, K-9s checks the representative types at positions {0,1} with a pure repeatable comparator; the listed scalars/arrays/Drop/Cell use their documented strict comparisons and arbitrary full payloads. This does not establish arbitrary comparator behavior for that correctness contract. ZST K-9s was prepared but NOT_RUN, and no separate i32 result is asserted. The all-position frame proof is specifically for u8/u64; [network K-9s jobs121–123/150 and R9][NET].

## Comparator model

O1 relies only on **variant (A)**, without `should_panic`. On each call the comparator reads both input values through `read_volatile` and returns an arbitrary bool (CD-2); the reads prevent an unread reference from making memory checks vacuous. Comparator-originated panic is excluded. The sole manually cut branch is `panic_on_ord_violation`, replaced by `kani::assume(false)`; separate covers establish reachability of that call. This proves the absence of failing Kani checks only on the retained paths, under the stated CI flags. It does not prove the behavior of the cut path or its unwind recovery. See [R6 §2 item 3][R6], [W1 CD-2][W1], [W2 O1-A][W2].

For correctness, the compared values follow the particular pure strict ordering in the harness. Arbitrary bool safety is not a sortedness claim under an inconsistent comparator. For `Cell<K13Tagged{key:u8,tag:u8}>`, O3 reads both values and writes fresh keys; only safety is claimed for the larger families. Label permutation is checked only at N2..4, across three entry points sharing two bodies. See [network night R9 and O3 results][NET], [W2 §1][W2].

ZST diagnostics deliberately use `ptr::read` instead of `read_volatile` for zero-sized values. This is an explicit exception to CD-2, isolating a tool-model limitation; it does not silently substitute the ZST result into the ordinary O1-A family. See [Z-1 classification and R7][L1U].

## Reductions and premises

**Network permutation.** `sort9_optimal` consists of 25 compare-exchanges and `sort13_optimal` of 45, using constant distinct in-range indices and no other writes to the input array. The checked `swap_if_less` contract preserves or exchanges the two full values and frames the other cells. A composition of these operations preserves the multiset. This is a structural argument from the source and checked contracts, not a standalone full-width end-to-end permutation proof for every network instantiation. The argument and R9 GO_WITH_NITS are recorded in [network night review, e658b246..be1aa9b8][NET], as required by [R6 §2 item 4][R6]. Accepted network sortedness proofs run at full u8/u64 width on real bodies; no 0–1 or narrow-width reduction is used. Earlier phase-2 0–1 harnesses (jobs 18/23/25, gate false) are not part of the basis. See [K-10 results and handoff][NET]. For N9..15, the permutation claim composes this structural argument with separately proved insertion-tail permutation; full-route sortedness is proved separately. A full-route multiset check for N10+ is not claimed ([K-10 handoff][NET]).

**K-9s allocation sizes.** The earlier arbitrary-position proof in `[T;17]` was extended to exact `[T;N]` arrays for every N9..16, u8/u64, with the same comparator as K-10 and frame checks on all other cells. N17 was retained and rerun. [Build d065eab6-9c2e-4cf5-9022-67b2589d18f7][L1] and [build d989b725-5f5a-46b6-ae1f-c31c8152541e][L1] have gate true and R9 GO `924e2266`. Thus the former sizes 9..16 gap is closed for those exact types/allocations. Transfer to other allocation sizes, enclosing scratch buffers or types remains a locality premise: the body touches only the two addressed cells and local temporary storage, while callers must establish all alignment, liveness, initialization, distinctness and access premises. See [network transfer argument][NET] and [R8 §7][R8].

**K-8r shift invariance.** Jobs154/155/157/159 prove the `insert_tail` contract for 120 exact regions in `[u64;17]`: start 1..15 and tail=start+1..16, including frame properties outside the region. Start 0 had earlier evidence in job58. This removes the shift argument only for those regions. A second merge region, scratch48 and subregions of other allocations are not covered. Transfer there would require a separate argument that the body depends only on pointers/differences within the region and not on absolute address or enclosing allocation size; it is not a machine-checked general lemma. See [K-8r and final R9 clarification][NET], R9 GO_WITH_NITS for `a15216a1`/`4dd2272f`.

**B4 above 20.** The insertion safety families are bounded and unwind their loops. Even a completed all-offset family through 20 does not prove the requirement for arbitrary lengths. No universal loop invariant is claimed. Correctness of a checked `insert_tail` region also does not by itself prove full insertion correctness for every length/offset. See [requirements B4/B5][REQ], [W2 B4][W2] and [W3-L1 split progress][L1].

**H1 tagged encoding.** The new merge formulation uses unique arbitrary tags<64, a u64 mask equal to the input region's mask, and an explicit key↔tag relationship against the input snapshot. Keys remain full-width; tags of a second region need not start at 0. `Tagged` is 16 bytes and follows general, not the u8/u64 unstable network dispatch. The actual contract/stub selection is checked at N4/8, including key-loss, tag-loss and bad-label controls, in [build 6e32e784-7096-4dfb-ba0c-743181d525b3][L2], gate true and R9 GO `edda4bbe`. **TODO — W3-L2, L2-1:** old/new N20/24 comparison, N32 and length-domain outcome. N4/8 is not proof of those larger lengths, and Tagged evidence does not transfer to network merely because its fields are u64 ([R8 L2-0/L2-1][R8], [L2 route table][L2]).

## What is not checked

**Uninitialized reads (E1).** Ordinary organizer CI does not enable `-Z uninit-checks`. U-1 explicitly enabled it in an out-of-CI diagnostic on pin `9461e07a`, [build d044a528-b330-4754-96af-6a4ea38b5fda, source216e1d6b][L1U]. All nine harnesses failed with an unsupported check while creating `MaybeUninit`, before the sort or control read; subsequent covers were 0. The exact messages are:

```text
Checking memory initialization of type [mem::maybe_uninit::MaybeUninit<u64>; 48] is not supported. Cannot determine layout for a type that contains union of type mem::maybe_uninit::MaybeUninit<u64> as a field.
Interaction between raw pointers and unions is not yet supported.
```

The first occurs at `uninit.rs:283/339`, the second at 317/327/378 on that source SHA. Both positive and negative controls are unsupported; no paired negative-FAILED/positive-SUCCESS control was accepted under rule U-a. Real network sorting with uninit-checks was not run: the network-layout controls are not a network proof. U-1 establishes a feasibility limitation, not absence or presence of an uninitialized read in the algorithm. Closing E1 would additionally require a supported tool configuration and committee-approved CI coverage; globally adding the flag is not proposed here. See [U-1 classification][L1U], [R8 §4][R8].

**Aliasing and UB categories.** No aliasing proof is claimed. Mutation of immutable caller bytes and invalid-value coverage must be qualified by what this pin/configuration actually checks; the draft does not claim complete coverage of all four challenge UB categories or an accepted exemption under #733. **TODO — coordinator, final disclosure review:** settle that boundary with the committee. See [requirements E1/E2][REQ], [W2 exclusions][W2], [R6 §2][R6].

**Unwind and Drop.** `-Cpanic=abort` excludes unwind recovery. Neither a panicking comparator nor `CopyOnDrop` restoration during unwinding is verified. Normal-return O2 uses the pair “Drop counter equals N” and “labels are a permutation”; a counter alone cannot detect duplication plus loss. That pair is checked at fallback/insertion N2/4/8 and general/stable N2/4/8/16, with two negative controls; it is not a panic-safety result. See [W2 O2/K-14r][W2], [merge result and review][MERGE], [R6 §2][R6].

**ZST volatile reads.** `z1_volatile_unit` reproduces four dereference failures on a local `()` without sorting; replacing volatile read with `ptr::read` succeeds. The diagnostic builds are [5aee04a2-8039-4cae-8160-e76a19ab9608 and 3e8d706e-87e8-4931-8322-be51a69e10a4][L1U]. This is classified as a Kani model limitation and tracked in [model-checking/kani#5072](https://github.com/model-checking/kani/issues/5072), opened by the coordinator under the owner’s decision. The coordinator reports reproduction in a standalone crate on both pin `9461e07a` and the latest release (2026-10-27). With the ZST-aware comparator, stable trait lengths 1,2,7,8,16,17,31,32 and network N8 succeeded diagnostically; network N9/17 remained TIMEOUT/resource-limited. These are not accepted all-length ZST CI proofs. See [Z-1 final classification and handoff][L1U].

**Latent ZST network loop.** For network N≥18, the region-pointer loop cannot progress for zero-sized elements because pointer addition does not change the address. The coordinator supplied Kani evidence in builds `ebedbd9b` and `1dc574db`, branch `experiment/kani-k1-zstloop-20261027` (2026-10-27). Public stable/unstable sort callers return for ZST before reaching this trait route. The latent path is tracked in [rust-lang/rust#165041](https://github.com/rust-lang/rust/issues/165041), opened by the coordinator under the owner’s decision; no publicly reachable failure or upstream resolution is claimed. See [network K-16s ZST argument][NET], [Z-1 classification][L1U].

**Other exclusions.** Sortedness/permutation is established only for u8 and u64 with a pure strict order; other C3 types have safety results only. The separate Tagged N4/8 experiment validates a merge-contract encoding, not full-route C3 correctness ([L2-0 results][L2]); final-code R9 for the K-16s safety matrix is pending as noted above. Stability, correctness for arbitrary user-defined orders, generic verification for every Sized T, small-sort inputs above the route threshold and an unbounded insertion proof are not claimed. Missing correctness through the actual thresholds remains a substantive gap, not an exclusion that closes the requirement. See [requirements B/C/D/E][REQ], [R8 §1/§6][R8].

## Trust ledger

| Item | Meaning and evidence |
|---|---|
| Tool pin and flags | Kani `9461e07a`; the lane follows organizer `scripts/run-kani.sh`. Invocation: `kani verify-std -Z unstable-options ./library`, with `-Z function-contracts -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing`, `--no-assert-contracts`, request-specific arguments, then `--cbmc-args --object-bits 12`. Panic strategy is `-Cpanic=abort`. See [EXPERIMENT §1/§5–5b][LANE], [W2 pin and caveats][W2]. **TODO — W3-L1 L1-6:** recheck flags against the final upstream snapshot. |
| std runtime precondition checks | At this pin Kani evaluates `Operand::RuntimeChecks` (`ub_checks`, `contract_checks`, `overflow_checks`) as false. Thus std `assert_unsafe_precondition!` execution is not an extra safety guarantee; Kani's own memory/arithmetic checks are distinct. See [R6 §2 item 2, compiler source location 60–64][R6], [C-5 job76][W2]. |
| `--no-assert-contracts` and verified stubs | This flag does not justify treating unchecked callees as safe. R11 deliberately violates preconditions under `stub_verified`: network job5 fails `a_pos != b_pos`; merge job8 fails the sorted-halves condition. The u8 insertion R11 fails `k1_tail_pre` in [build 6e32e784][L2]. These are specific controls, not a blanket theorem about every contract. See [network R11][NET], [merge R11][MERGE]. |
| R4 | The callee contract must have been proved for the exact length used by its caller, together with the relevant type, comparator and region premises. A successful proof at N16 does not authorize a stub at N13/14/15, N20 or a new Tagged instantiation. See [W2 correctness section][W2], [L2 route table][L2]. **TODO — W3-L1 L1-6:** publish final stub↔proof inventory. |
| Manual stub | `panic_on_ord_violation → assume(false)` is the explicit path cut used by variant A. Covers witness reachability of its call, not behavior after it. No handwritten algorithm summary is claimed. See [R6 §2/§5][R6], [W2 O1-A][W2]. |
| Assumptions / covers | Length, offset, sorted-prefix, label-domain and valid-allocation premises must be explicit. Accepted positive rows require the relevant covers. U-1's 0 covers are failure to reach the intended experiment. Negative controls may fail before their final cover; their failed check must be localized and match the intended condition. See [EXPERIMENT][LANE], [L1 grouping ledger][L1], [L2 controls][L2], [U-a][L1U]. |
| Architecture / resources | Historical proofs are Linux lane measurements, not macOS results. There is no generic claim over architecture or type layout. See [EXPERIMENT §5–5b][LANE] and [R8 §2.1/L1-8][R8]. |
| Runtime correspondence | Runtime std changes are forbidden; final integration must retain that property. The controls `check-cfg` declaration in `library/core/Cargo.toml` is a tooling declaration to disclose, not a runtime change. **TODO — W3-L1 L1-6:** publish final diff against current upstream and the verification-only inventory. See [R8 L1-6][R8], [EXPERIMENT §5b controls][LANE]. |

`should_panic` is not used as the basis for the submission's safety claim. CD-1 found that it masks assertion-class failures, including ordinary assertions, index/overflow assertions and contract assertions. C-5 nevertheless made all four tested non-assertion controls fail: `assume`, `unchecked_add`, overlapping `copy_nonoverlapping`, and `ptr.add` outside the allocation. Neither observation licenses removing a check. See [R6 §2][R6] and [W2 C-5, merge job76][W2].

## Controls and mutants

Existing controls live alongside the experimental harnesses under `library/core/src/slice/sort/shared/smallsort/kani_k1/`: `merge.rs` and `network.rs`; Z-1/U-1 use `uninit.rs`, and Tagged controls use `correct.rs` on the W3-L2 branch. These are intermediate locations, not a claim that the submitted tree already separates them. R11, C-5, Drop/permutation and Tagged controls have the outcomes recorded in [merge][MERGE], [network][NET], [L1u][L1U] and [L2][L2].

The final submission must exclude expected-FAILED controls from ordinary CI using **`cfg kani_smallsort_controls`**. The base lane supports an opt-in request field `"controls": true`, which sets `RUSTFLAGS="--cfg kani_smallsort_controls"`; ordinary organizer CI does not set it. The lane validates that this cfg cannot change arbitrary runtime code. See [EXPERIMENT §5b controls][LANE]. **TODO — W3-L1 L1-6/L1-9:** move/gate all expected-failure harnesses, document their final module paths and full names, and record reproduction outcomes on the final source SHA.

The planned reproduction is to check out that final SHA, enable `--cfg kani_smallsort_controls`, and select the documented control harness with the same Kani pin/CI flags above (or use a lane request with `"controls": true` and the exact harness name). The expected result is a localized FAILED on the specified check, paired with the matching positive proof. This is a reproduction recipe, not a build executed by W3-DOC; final commands, names and check texts are **TODO — W3-L1 L1-6/L1-9** ([R8][R8], [lane controls interface][LANE]).

L1-9 requires five algorithm mutants: inverted `swap_if_less` condition, `insert_tail` off-by-one, wrong `merge_up` advancement, removed final `bidirectional_merge` check, and incorrect `presorted_len`. Their killed/not-killed matrix is **TODO — W3-L1 L1-9**; the existing local controls do not establish that all five were killed ([R8 L1-9][R8]).

## Extended layer: evidence outside CI

The original u64 merge contract (formulation 1) succeeded at N20 in 3460.9 s on [build a06eb982-3175-4375-8bd3-b16c75c4e54e][EXT], and at N24 in 14011.6 s on [build f745482f-1c58-4966-b901-b3077d25b151][EXT]. R9 GO is recorded for `e55e9f3c6adfd6dd55e8422bd9f2e1490119eb23`. These were Cloud Build **32 GB resource** runs. They provide additional evidence for those exact lengths but exceed 600 s and do not count toward ordinary CI. N28/32 were not run; extrapolations are not proofs. See [RESULT-ext][EXT], [W2 extended-layer table][W2], [EXPERIMENT §5a][LANE].

E-2 separately checks B4 insertion safety for u64 N16..20 with **every offset 1..N**: `ext_b4_u64_n16`…`ext_b4_u64_n20`, [build 177675c6-c058-4a77-9c27-f3ed937288cf][EXT], R9 GO_WITH_NITS `51e17cbe8d0f50674c2a28e3204a682a9d1e81dd`. This is also the **32 GB resource lane, outside CI credit**. SUCCESS within 600 s on that lane does not establish the primary-lane acceptance criterion. Moving B4 N16..20 into the primary layer using offset groups is **in progress — W3-L1, L1-5** ([E-2 results and review][EXT], [L1 split progress][L1]).

The earlier K-1 experiments expose an instrumentation limit as well as solver cost. On CircleCI 13 GiB, job35 with the permutation counter and a trivial loop invariant OOMed in `goto-instrument`, while removing the counter in job40 allowed instrumentation to complete. On the separate 32 GB resource lane, full-invariant instrumentation also hit SIGKILL near 30.5 GiB, including [build 929ef63e-58d2-4838-8a42-c5465d96797a][MERGE]. Ordinary proofs of the loop-invariant formulation also timed out at 60 minutes on the 32 GB lane, with and without that invariant ([K-1 phase7 B/C][K1]). These are distinct experiments; job35-vs40 is the intended tracking-issue reproduction, not an N32 proof. See [REPORT-K1 §3][K1], [R4 §4 item 2][R4]. **TODO — coordinator after final measurements:** prepare the tracking issue with the exact recorded requests; no external issue submission is performed by this draft.

The early R4 estimate of roughly 3.2× growth per extra 4 elements and the later N20/N24 timings are observations on different experiments, not a complexity theorem or a precise N32 runtime prediction. For the original formulation the later measurements show a time bottleneck even when measured process RSS is modest. The new Tagged formulation is still under controlled evaluation; no speedup is asserted ([REPORT-K1][K1], [W2 §1][W2], [L2 comparison protocol][L2]).

## SAFETY comments

The known `merge_down` SAFETY-comment deficiency is recorded by the plan as rust-lang/rust#135984. This draft records that source-reported issue; it does not claim to have changed upstream or audited the issue's current resolution. **TODO — coordinator, final PR:** include the applicable upstream reference and any additional comment findings. See [R4 §4 item 7][R4] and [requirements E5][REQ].

## CI resources — placeholder for W3-L1 stage C

Historical CircleCI uses a 13 GiB verify cgroup on a 15 GB/4 CPU Linux VM. The primary Cloud Build lane is `gcb-e2-standard-4`,4 vCPU/16 GB, bounded by machine memory rather than that cgroup. Neither alone reproduces organizer partitions. 32 GB resource results are outside CI credit, regardless of observed RSS. See [EXPERIMENT §5–5b][LANE], [R8 §2][R8].

The acceptance target is the actual organizer partition layout with baseline repository harnesses included: four count-based partitions, Linux `KANI_JOBS=2`, and the organizer macOS architecture/memory/parallelism. A single-harness measurement gate does not establish aggregate wall time, concurrent memory, swap/OOM behavior or completeness. See [R8 §2.1 and L1-7/L1-8][R8].

| Required final measurement | Current disclosure | Owner |
|---|---|---|
| Final upstream/submitted SHA, pin, flags and total harness count | TODO | W3-L1 L1-6/L1-7 |
| Linux partitions 1/2/3/4: source/build IDs, wall time, aggregate memory, swap, OOM, all harnesses completed | TODO; not measured in the evidence used here | W3-L1 L1-7, coordinator |
| macos-latest: architecture, available memory, actual jobs and all four partition results | TODO; no accepted measurement | W3-L1 L1-8, coordinator |
| Controls absent from ordinary partitions; separate mutant reproduction | TODO | W3-L1 L1-6/L1-9 |
| Residual macOS/resource limitations and accepted deviations | TODO; do not infer feasibility from a larger executor | W3-L1 stage C / coordinator |

All entries in this placeholder follow [R8 L1-6…L1-9][R8]. This draft does not claim that H1/H2/H4 have been met.

## Evidence snapshots

This draft uses base `1052dee57addafe3bf2389894eb99c381f4aa4f0`, plan branch `73ed3906fa25fba9efed3e0669b0b6aeae377d91`, W3-L1 `be8b306dc89e239ce63bcfe5b95b3b175fa2e5cf`, W3-L2 `27a2d280dc007d6d81bd5be361d98cd2fe5afd73`, and completed W3-L1u input at `b0f457cc51f5ad39c4e6d5c2bcdc21b3dc658ece`. The current W3-L1/W3-L2 RESULT tails were fetched and reread before the review request. Full build IDs, source revisions, checks and R9 decisions are in the linked result files. Further agent results require an explicit update of this disclosure. The coordinator’s 2026-10-27 review message additionally supplies the E-2 confirmation, pending `bf3e03f7` R9 status, and ZST issue/reproduction evidence incorporated here; no new W3-DOC run is implied.

[REQ]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/73ed3906fa25fba9efed3e0669b0b6aeae377d91/research/challenge-8/REQUIREMENTS-INTERPRETATION-2026-10-24.md
[R8]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/73ed3906fa25fba9efed3e0669b0b6aeae377d91/research/challenge-8/CH8-PLAN-R8-2026-10-27.md
[R6]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/73ed3906fa25fba9efed3e0669b0b6aeae377d91/research/challenge-8/CH8-MINIMAL-PLAN-R6-2026-10-26.md
[R4]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/73ed3906fa25fba9efed3e0669b0b6aeae377d91/research/challenge-8/CH8-MINIMAL-PLAN-R4-2026-10-26.md
[W1]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/1052dee57addafe3bf2389894eb99c381f4aa4f0/research/challenge-8/kani-k1/REPORT-W1-2026-10-26.md
[W2]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/1052dee57addafe3bf2389894eb99c381f4aa4f0/research/challenge-8/kani-k1/REPORT-W2-2026-10-27.md
[K1]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/1052dee57addafe3bf2389894eb99c381f4aa4f0/research/challenge-8/kani-k1/REPORT-K1-2026-10-26.md
[LANE]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/1052dee57addafe3bf2389894eb99c381f4aa4f0/research/challenge-8/kani-k1/EXPERIMENT.md
[NET]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/b0f457cc51f5ad39c4e6d5c2bcdc21b3dc658ece/research/challenge-8/kani-k1/RESULT-network.md
[MERGE]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/b0f457cc51f5ad39c4e6d5c2bcdc21b3dc658ece/research/challenge-8/kani-k1/RESULT-merge.md
[EXT]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/b0f457cc51f5ad39c4e6d5c2bcdc21b3dc658ece/research/challenge-8/kani-k1/RESULT-ext.md
[L1U]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/b0f457cc51f5ad39c4e6d5c2bcdc21b3dc658ece/research/challenge-8/kani-k1/RESULT-w3-l1u.md
[L1]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/be8b306dc89e239ce63bcfe5b95b3b175fa2e5cf/research/challenge-8/kani-k1/RESULT-w3-l1.md
[L2]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/27a2d280dc007d6d81bd5be361d98cd2fe5afd73/research/challenge-8/kani-k1/RESULT-w3-l2.md
