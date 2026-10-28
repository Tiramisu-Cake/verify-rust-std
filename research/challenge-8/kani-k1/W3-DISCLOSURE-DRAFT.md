# Towards #56: SmallSort verification disclosure (draft)

This is a review draft, not a claim that Challenge 8 is resolved. Submission remains conditional on the final requirements table and the integrated organizer CI run; the macOS candidate run is recorded below with its resource limits. The working title is **Towards #56**. See [R8 §6–7][R8] and the [requirements table](W3-REQUIREMENTS.md).

The evidence below distinguishes historical verification records, the Cloud Build calibration runs and the separate macOS report. Historical accepted results require a true measurement gate, completed covers and successful tooling checks, as recorded in the [wave 2 report][W2]. A diagnostic SUCCESS, an archive-integrity check, or a resource-lane gate does not establish acceptance in the submitted CI domain. The final integrated candidate is `ac0dbbf0fbf1ee8b90ca77c186c2058a96acbbad`; its three-harness integration measurement passed ([integration result][L1D]). The older source `5c713131f8b92c629f0c16b68605ec2bf2547007` underlies the historical partition measurements. Neither is proof credit for the unmeasured final whole suite. Linux results are recorded per partition below; the completed macOS candidate result is recorded separately.

## Terms used in this draft

| Term | Meaning |
|---|---|
| Harness / cover | A Kani verification entry point / a reachability witness for an intended input or path. |
| Lane / gate | A configured verification environment / its automated check of expected outcomes, required covers and resources for that run mode. A true gate alone does not give CI proof credit; runner, mode and review also matter. |
| CD-2 | The comparator model reads both arguments through `read_volatile` before returning its result. |
| O1-A | Safety family with arbitrary comparator results, using variant A: only `panic_on_ord_violation` is cut; no `should_panic`. |
| O3-s | Safety family with a comparator that reads both `Cell` values and mutates their keys. |
| R4 / R11 | Composition rule requiring a proved contract at the matching length/type/comparator / negative controls checking that violated callee preconditions fail under a verified stub. |
| K-9s / K-8r | `swap_if_less` exact exchange-or-preserve and frame proofs / `insert_tail` proofs on explicitly shifted regions. |
| K-11s / K-16s | Bounded insertion safety family / representative type-and-route safety matrix. |

These labels follow [EXPERIMENT][LANE], [R6][R6], [R8][R8] and the [wave 2 report][W2]. Requirement IDs such as B4 and C3 refer to the [requirements interpretation][REQ].

## Scope

The targets are the three `small_sort` trait methods (`StableSmallSortTypeImpl`, `UnstableSmallSortTypeImpl`, `UnstableSmallSortFreezeTypeImpl`), `swap_if_less`, `insertion_sort_shift_left`, `sort4_stable`, and `has_efficient_in_place_swap`. Reachable internal bodies include fallback, general/general-with-scratch, network, insertion tails, sort8, sort9/sort13 and bidirectional merge with merge_up/merge_down. Verification uses real bodies or separately checked contracts; unwind execution of `CopyOnDrop::drop` is excluded. These targets and the required domains come from the [requirements interpretation §2 A/B][REQ]; implemented coverage is recorded in [W1] and [W2 §1][W2].

The measured external stable-Freeze route uses **scratch = 48**; this is not evidence for every permitted scratch size ([W1] and [W2]). The small-sort domain is every length up to its route threshold: 0..=16 for fallback/stable default and 0..=32 for general/network/stable-Freeze. This is the project's interpretation of a valid trait call, not a committee ruling. Larger small-sort calls are outside this submission's claimed domain. `insertion_sort_shift_left` has no such threshold; its bounded results below do not prove safety for arbitrary lengths. See [requirements B1–B5][REQ] and [R8 §1][R8].

| Property / route | Measured domain and limits | Evidence |
|---|---|---|
| O1-A, no failed Kani checks in the stated comparator model: general and stable-Freeze | u64, every N0..32; corresponding transparent non-Copy trait/general paths | CircleCI 13 GiB, [W1] and [W2] |
| O1-A: network | u64, every N0..32 | CircleCI 13 GiB, [W1] and [W2] |
| Fallback / stable default safety | K-16s: selected N0,1,2,15,16 for `Cell<i32>` and unstable `[u8;86]`; O3: every N0..16 for `Cell<K13Tagged>` | CircleCI 13 GiB, [K-16s and O3 results][NET], [W2] |
| Sortedness **and** full-value permutation: general / stable-Freeze | u64 N0..12 and N16; u8 N0..16 | CircleCI 13 GiB, [W2 correctness table][W2], plus GS u8 N14/15 from [L2-2][L2], build `be2555c0-d29b-412c-aa42-046c7233bc07`, gate true. The latter uses the stated scratch48 composition premises below. |
| Sortedness and permutation: network | u64 N0..14; u8 N0..15. N0..8 are direct end-to-end proofs; for N9..15 permutation is composed from the structural network argument (below) and separately proved insertion-tail permutation, with full-route sortedness proved separately | CircleCI 13 GiB, [W2 correctness table][W2], [network results][NET] |
| Sortedness and permutation: direct fallback | u64/u8 N0..16 | CircleCI 13 GiB, [W2 correctness table][W2], plus [L2-2][L2] builds `1e932304-105e-4f26-9556-e3b9c2b63dde`, `b436b6d6-7982-4230-839a-ec1c582d0103`, `be2555c0-d29b-412c-aa42-046c7233bc07`, gate true for every added fixed length. |
| Insertion safety B4 | u64 N1..15, all valid offsets; N16..20 offset 1 | CircleCI 13 GiB, [network insertion results][NET] |
| B4 / O3 split families | B4 = u64; O3 = `Cell<K13Tagged>`; N13..20, every valid offset | Cloud Build 16 GB, [builds d989b725, ae249f1f, bb656284, 64e7da65, c122daa1; L1-5 final table][L1], gate true; grouped harnesses passed measurement; the split insertion family is complete. N15..20 use 56 grouped harnesses with a cover for each offset. Maximum including N13/14: 146.13629 s; sampled aggregate RSS ≤4.37 GiB across sequential builds, not continuous per-harness peaks. |
| sort4, two separate checks | `proof_for_contract` with a pure strict comparator, plus ordinary safety proof with arbitrary comparator; u64 and `[u8;16]`, N4 | Cloud Build 16 GB, [build d065eab6-9c2e-4cf5-9022-67b2589d18f7][L1], gate true |
| Efficient in-place swap predicate | the ten types enumerated in `w3_efficient_swap_c3`, including ZST | Cloud Build 16 GB, [build 70902589-d488-498d-9595-278e48013138][L1], cover 10/10, gate true |

L2-2 adds 17 ordinary fallback callers (u64 N8..16 and u8 N9..16), GS u8 N14/15, and the supporting u8 prefix/scratch proofs, for 21 ordinary harnesses. These close the stated fallback ranges and GS u8 N14/15; the remaining GS u64 and network bounds are disclosed below. Network full correctness remains open above u64 N14/u8 N15: separate u8 sortedness at N16/17 does not establish tail permutation. H1 STOP for lengths 17..32 remains. L1-5 is complete: B4/u64 and O3/`Cell<K13Tagged>` N13..20 with all valid offsets are in the primary layer ([split insertion results][L1]). The imported `correct.rs` is unchanged; no Tagged, `K1MergePerm` or `new bm` contract is included. All experiments not accepted into the ordinary layer remain behind `cfg kani_smallsort_controls`.

## L2-2 correctness additions and disclosed bounds

The imported layer consists of 17 fallback callers (u64 N8..16 and u8 N9..16), GS u8 N14/15, and the u8 prefix and scratch supporting proofs: 21 ordinary harnesses total. The exact full-width u8/u64 domains, `lt_u8`/`lt_u64`, equal keys with distinct full values, exact-size arrays, and the unchanged `correct.rs` are recorded in the [L2 result][L2]. The GS u8 route uses stable-trait exact arrayN plus scratch48 and a separate direct-general proof. Moving the existing `bm` contract to prefix scratch48 is the D-B4 analytical transfer argument; it is not a separate machine-checked scratch48 merge proof. Scratch u8 checks retain their explicit frame outside the active region. This does not establish E1/uninitialized-memory behavior.

| Route gap | Recorded result and boundary | Status |
|---|---|---|
| Fallback u64 N8..16; fallback u8 N9..16 | All individual lengths are closed by the accepted caller layer. | Closed for these exact type, comparator and length instances. |
| GS u8 N14/15 | Closed within D-B4 using exact arrayN and scratch48; the supporting prefix/scratch u8 proofs are included. | Closed within the stated route and premises. |
| GS u64 N13/14 | TIMEOUT120 on each solver sweep is screening only. No full 600-s measurement of these solver candidates was run; the required scratch u64 prerequisite is absent. | Disclosed, not closed. |
| GS u64 N15 | Caller result SUCCESS at 388 s does not complete R4: scratch u64 timed out at TIMEOUT600 with both cadical and kissat. | Disclosed, not closed. |
| Network u64 N15/16; u8 N16 | TIMEOUT120 sweeps are short screening runs; no corresponding full 600-s measurement of these solver candidates was run. | Disclosed, not closed. |
| Network u64 N17; u8 N17 | Caller runs reached TIMEOUT600 with cadical; sweeps separately reached TIMEOUT120 (kissat for u64, minisat for u8). | Disclosed, not closed. |

H1 STOP for 17..32 remains unchanged. The upper correctness gap is not inferred closed from nearby lengths, sortedness-only results, or the separate L2-0 Tagged experiments. All unaccepted experiments remain controls-only; no `should_panic` evidence is counted.

## Type matrix (C3)

Monomorphizations are representatives of dispatch branches, not a proof for every `Sized T`. The following are the actual K-16s sample sets: G = {0,1,2,7,8,15,16,17,31,32}, S = {0,1,2,15,16}, and U = {8,9,12,13,17,18,31,32}. These are boundary/transition samples, not all intermediate lengths. A separate `i32` K16s instance now checks both stable and unstable trait points at N0,1,2,15,16; it does not fill intermediate lengths or the i32 K9s cell. Full u64 length coverage comes from separate O1 families. K-16s is documented in the [network type matrix][NET], with measurement gates reported in [W2 §1][W2]. The historical matrix contains 143/143 accepted non-ZST cells plus 13 reachability harnesses; the same report records K-11s N1..15/all offsets, O3-s defaults N0..16 and insertion N1..15/all offsets, and O1-A network N18..32. The later i32 measurement establishes only the five stated lengths. ZST coverage is incomplete, and the matrix remains a set of representative instantiations.

| Type | Actual dispatch / callee distinction | Measured scope and limit |
|---|---|---|
| `()` | Freeze/Copy, size 0: unstable network, stable general; efficient swap true | Predicate accepted in [build 70902589][L1]; stable trait N1,2,7,8,16,17,31,32 accepted in [build 1e761350][L1] with the ZST-aware comparator. Stable N0, unstable/network and K9s ZST remain outside accepted coverage; see ZST below. |
| `u8` | unstable network, stable general; size≤8, size≤16, align 1 | K-16s unstable U / stable G, [NET]; correctness only in the scope table above. |
| `i32` | unstable network / stable Freeze/general from dispatch; Copy, efficient-swap | `w3_k16_i32_freeze`, stable and unstable at N0,1,2,15,16; build `8da0f05f-c30c-4f50-ba8b-27a5239b3d5a`, gate true, 99.8184 s, 0/422 failed, 11/11 covers; check-tooling against `85ceaa0ddb610d43bf24495d3aab676f6be25360` passed. Full `[i32;N]`, volatile reads of both comparator arguments, arbitrary result; safety only. This is a K16s instance, not K9s, all lengths or sortedness. `Cell<i32>` is a different branch. |
| `u64` | unstable network, stable general; size 8 boundary, align 8 | All lengths for O1; bounded correctness as above, [W1]/[W2]. |
| `u128` | unstable general, stable general; >8 and ≤16, presort8 for N≥16 | G on both routes, [NET]. This represents the 9..16-byte interval; not full C3 correctness. |
| `[u8;16]` | general on both routes; presort8 size boundary | G on both routes, [NET]; sort4 contract/arbitrary pair also [build d065eab6][L1]. |
| `[u8;17]` | general on both routes; presort4 for N≥16 | G on both routes, [NET]. |
| `[u8;85]` | last size admitted to unstable general; stable general | G on both routes, [NET]. Both separate sort4 checks TIMEOUT at 600 s in [build 9a62b6cf-b26c-41c7-a6a3-3f333f4fb402][L1]; no accepted sort4 proof for this instantiation. |
| `[u8;86]` | unstable fallback≤16; stable Freeze still general-with-scratch≤32 | Unstable S / stable G, [NET]. The fallback size test does not apply to the stable Freeze route. |
| `Cell<i32>` | !Freeze, stable default / unstable fallback≤16 | S in K-16s, [NET]. The additional mutating O3 families use `Cell<K13Tagged{key:u8,tag:u8}>`, not `Cell<i32>`; they do not establish this exact instantiation for every length. |
| Freeze !Copy with nontrivial Drop (`W2Drop(u8)`) | unstable general despite size≤8; stable general | G on both routes, [NET]. Normal-return Drop/permutation checks are separate, below. |

For the two-cell `swap_if_less` contract, K-9s checks the representative types at positions {0,1} with a pure repeatable comparator; the listed scalars/arrays/Drop/Cell use their documented strict comparisons and arbitrary full payloads. This does not establish arbitrary comparator behavior for that correctness contract. ZST K-9s is excluded after an unsupported-pointer result; see the ZST limitations below. The separate i32 result covers the stated K16s lengths only. The all-position frame proof is specifically for u8/u64; [network K-9s results][NET].

## Comparator model

O1 relies only on **variant (A)**, without `should_panic`. On each call the comparator reads both input values through `read_volatile` and returns an arbitrary bool (CD-2); the reads prevent an unread reference from making memory checks vacuous. Comparator-originated panic is excluded. The sole manually cut branch is `panic_on_ord_violation`, replaced by `kani::assume(false)`; separate covers establish reachability of that call. This proves the absence of failing Kani checks only on the retained paths, under the stated CI flags. It does not prove the behavior of the cut path or its unwind recovery. See [R6 §2 item 3][R6], [W1 CD-2][W1], [W2 O1-A][W2].

For correctness, the compared values follow the particular pure strict ordering in the harness. Arbitrary bool safety is not a sortedness claim under an inconsistent comparator. For `Cell<K13Tagged{key:u8,tag:u8}>`, O3 reads both values and writes fresh keys; only safety is claimed for the larger families. Label permutation is checked only at N2..4, across three entry points sharing two bodies. See [network night O3 results][NET], [W2 §1][W2].

ZST diagnostics deliberately use `ptr::read` instead of `read_volatile` for zero-sized values. This is an explicit exception to CD-2, isolating a tool-model limitation; it does not silently substitute the ZST result into the ordinary O1-A family. See [Z-1 classification][L1U].

## Reductions and premises

**Network permutation.** `sort9_optimal` consists of 25 compare-exchanges and `sort13_optimal` of 45, using constant distinct in-range indices and no other writes to the input array. The checked `swap_if_less` contract preserves or exchanges the two full values and frames the other cells. A composition of these operations preserves the multiset. This is a structural argument from the source and checked contracts, not a standalone full-width end-to-end permutation proof for every network instantiation. The argument is recorded in [network results][NET], as required by [R6 §2 item 4][R6]. Accepted network sortedness proofs run at full u8/u64 width on real bodies; no 0–1 or narrow-width reduction is used. Earlier reduced-width experiments with false gates are not part of the basis. See [K-10 results and handoff][NET]. For N9..15, the permutation claim composes this structural argument with separately proved insertion-tail permutation; full-route sortedness is proved separately. A full-route multiset check for N10+ is not claimed ([K-10 handoff][NET]).

**K-9s allocation sizes.** The earlier arbitrary-position proof in `[T;17]` was extended to exact `[T;N]` arrays for every N9..16, u8/u64, with the same comparator as K-10 and frame checks on all other cells. N17 was retained and rerun. [Build d065eab6-9c2e-4cf5-9022-67b2589d18f7][L1] and [build d989b725-5f5a-46b6-ae1f-c31c8152541e][L1] have gate true. Thus the former sizes 9..16 gap is closed for those exact types/allocations. Transfer to other allocation sizes, enclosing scratch buffers or types remains a locality premise: the body touches only the two addressed cells and local temporary storage, while callers must establish all alignment, liveness, initialization, distinctness and access premises. See [network transfer argument][NET] and [R8 §7][R8].

**K-8r shift invariance.** The measured region family proves the `insert_tail` contract for 120 exact regions in `[u64;17]`: start 1..15 and tail=start+1..16, including frame properties outside the region. Start 0 has earlier evidence in the same report. This removes the shift argument only for those regions. A second merge region, scratch = 48 and subregions of other allocations are not covered. Transfer there would require a separate argument that the body depends only on pointers/differences within the region and not on absolute address or enclosing allocation size; it is not a machine-checked general lemma. See [K-8r results][NET].

**Insertion offset coverage and CI contracts.** In the historical K-11s/O3-s families, all offsets are enumerated by construction through `w2_const_offset_call`; covers witness only offsets 1 and N, not each intermediate offset. Acceptance of these ordinary safety harnesses depends on the CI flag `--no-assert-contracts`: they do not assert the existing functional contract of `insertion_sort_shift_left`. The 56 grouped L1-5 harnesses for N15..20 add a separate cover for every offset; the N13/14 single-length instances retain the earlier boundary covers. See [W2 insertion results][W2] and [L1-5 final table][L1].

**B4 above 20.** The insertion safety families are bounded and unwind their loops. Even a completed all-offset family through 20 does not prove the requirement for arbitrary lengths. No universal loop invariant is claimed. Correctness of a checked `insert_tail` region also does not by itself prove full insertion correctness for every length/offset. See [requirements B4/B5][REQ], [W2 B4][W2] and [split insertion results][L1].

**Separate tagged-encoding experiment.** A source-reported merge formulation outside this candidate uses unique arbitrary tags<64, a u64 mask equal to the input region's mask, and an explicit key↔tag relationship against the input snapshot. Keys remain full-width; tags of a second region need not start at 0. `Tagged` is 16 bytes and follows general, not the u8/u64 unstable network dispatch. The actual contract/stub selection is checked at N4/8, including key-loss, tag-loss and bad-label controls, in [build 6e32e784-7096-4dfb-ba0c-743181d525b3][L2], gate true. The new formulation timed out at N24 after 1800 s, exceeding the 600-s target and triggering STOP. **Not established:** an H1 speedup, N32 or a symbolic length domain. N4/8 is not proof of those larger lengths, and Tagged evidence does not transfer to network merely because its fields are u64 ([R8 L2-0/L2-1][R8], [L2 route table][L2]).

## What is not checked

**Uninitialized reads (E1).** Ordinary organizer CI does not enable `-Z uninit-checks`. U-1 explicitly enabled it in an out-of-CI diagnostic on pin `9461e07a`, [build d044a528-b330-4754-96af-6a4ea38b5fda, source 216e1d6b][L1U]. All nine harnesses failed with an unsupported check while creating `MaybeUninit`, before the sort or control read; subsequent covers were 0. The exact messages are:

```text
Checking memory initialization of type [mem::maybe_uninit::MaybeUninit<u64>; 48] is not supported. Cannot determine layout for a type that contains union of type mem::maybe_uninit::MaybeUninit<u64> as a field.
Interaction between raw pointers and unions is not yet supported.
```

The first occurs at `uninit.rs:283/339`, the second at 317/327/378 on that source SHA. Both positive and negative controls are unsupported; no paired negative-FAILED/positive-SUCCESS control was accepted under rule U-a. Real network sorting with uninit-checks was not run: the network-layout controls are not a network proof. U-1 establishes a feasibility limitation, not absence or presence of an uninitialized read in the algorithm. Closing E1 would additionally require a supported tool configuration and committee-approved CI coverage; globally adding the flag is not proposed here. See [U-1 classification][L1U], [R8 §4][R8].

**Aliasing and UB categories.** No aliasing proof is claimed. Mutation of immutable caller bytes and invalid-value coverage must be qualified by what this pin/configuration actually checks; the draft does not claim complete coverage of all four challenge UB categories or an accepted exemption under #733. No committee acceptance of those limits is asserted. See [requirements E1/E2][REQ], [W2 exclusions][W2], [R6 §2][R6].

**Unwind and Drop.** `-Cpanic=abort` excludes unwind recovery. Neither a panicking comparator nor `CopyOnDrop` restoration during unwinding is verified. Normal-return O2 uses the pair “Drop counter equals N” and “labels are a permutation”; a counter alone cannot detect duplication plus loss. That pair is checked at fallback/insertion N2/4/8 and general/stable N2/4/8/16, with two negative controls; it is not a panic-safety result. See [W2 O2/K-14r][W2], [merge result and review][MERGE], [R6 §2][R6].

**ZST volatile reads.** `z1_volatile_unit` reproduces four dereference failures on a local `()` without sorting; replacing volatile read with `ptr::read` succeeds. The diagnostic builds are [5aee04a2-8039-4cae-8160-e76a19ab9608 and 3e8d706e-87e8-4931-8322-be51a69e10a4][L1U]. This is classified as a Kani model limitation and tracked in [model-checking/kani#5072](https://github.com/model-checking/kani/issues/5072). It was reproduced in a standalone crate on pin `9461e07a` and the latest release (2026-10-27). The accepted stable ZST measurements are N1,2,7,8,16,17,31,32 only (build `1e761350-b663-4ab9-9f8e-361b17bacd8e`, gate true). N0 is absent. Unstable/network ZST and K9s ZST are not accepted: the former had OOM/TIMEOUT diagnostic limitations, while build `b3b2a4c7-8266-4b4b-9cb2-be127adcffbe` found unsupported pointer reasoning in K9s ZST, which is excluded under controls cfg. None of these closes all-length ZST coverage. See [Z-1 final classification and handoff][L1U].

**ZST network scope and latent loop.** Network sorting of zero-sized types is not verified at any length. At N≥18, its region loop additionally cannot terminate through its normal exit: adding an element offset to a zero-sized pointer leaves the address unchanged, so `region.as_ptr() == v_base` remains true and the `region.as_ptr() != v_base` break condition never fires (`smallsort.rs:355` at `5c713131`). Source-reported Kani loop diagnostics are builds `ebedbd9b` (N17 SUCCESS) and `1dc574db` (unwinding assertion at the loop), on branch `experiment/kani-k1-zstloop-20261027`; the N17 diagnostic is not accepted verification of network ZST sorting. All std callers—stable sort, unstable sort and `partition_at_index`—return early for ZST, so this path is unreachable through them. No publicly reachable failure is claimed.

**Other exclusions.** Sortedness/permutation is established only for u8 and u64 with a pure strict order; other C3 types have safety results only. The separate Tagged N4/8 experiment validates a merge-contract encoding, not full-route C3 correctness ([L2-0 results][L2]); the K-16s safety matrix excludes the remaining ZST gaps ([W2]). Stability, correctness for arbitrary user-defined orders, generic verification for every Sized T, small-sort inputs above the route threshold and an unbounded insertion proof are not claimed. Missing correctness through the actual thresholds remains a substantive gap, not an exclusion that closes the requirement. See [requirements B/C/D/E][REQ], [R8 §1/§6][R8].

## Trust ledger

| Item | Meaning and evidence |
|---|---|
| Tool pin and flags | Kani `9461e07a`; the lane follows organizer `scripts/run-kani.sh`. Invocation: `kani verify-std -Z unstable-options ./library`, with `-Z function-contracts -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing`, `--no-assert-contracts`, request-specific arguments, then `--cbmc-args --object-bits 12`. Panic strategy is `-Cpanic=abort`. See [EXPERIMENT §1/§5–5b][LANE], [W2 pin and caveats][W2]. The final integration source is `ac0dbbf0fbf1ee8b90ca77c186c2058a96acbbad`; the three-harness measurement uses these flags. Historical partition sources select partitions over the unchanged old code snapshot `5c713131f8b92c629f0c16b68605ec2bf2547007`. See [the integration source and tooling checks][L1D]. |
| std runtime precondition checks | At this pin Kani evaluates `Operand::RuntimeChecks` (`ub_checks`, `contract_checks`, `overflow_checks`) as false. Thus std `assert_unsafe_precondition!` execution is not an extra safety guarantee; Kani's own memory/arithmetic checks are distinct. See [R6 §2 item 2, compiler source location 60–64][R6], [W2 C-5 results][W2]. |
| `--no-assert-contracts` and verified stubs | This flag does not justify treating unchecked callees as safe. R11 deliberately violates preconditions under `stub_verified`: the network control fails `a_pos != b_pos`; a merge control fails `k1_merge_halves_sorted` for the K-10 formulation, alongside an earlier K-1 sorted-halves control. The u8 insertion R11 fails `k1_tail_pre` in [build 6e32e784][L2]. These are specific controls, not a blanket theorem about every contract. See the R11 control results in [network][NET] and [merge][MERGE]. |
| R4 | The callee contract must have been proved for the exact length used by its caller, together with the relevant type, comparator and region premises. A successful proof at N16 does not authorize a stub at N13/14/15, N20 or a new Tagged instantiation. See [W2 correctness section][W2], [L2 route table][L2]. Contract/caller domains are limited to the type, length and region pairs in the linked result records; no generic contract-to-proof correspondence is claimed for unlisted instantiations. |
| Manual stub | `panic_on_ord_violation → assume(false)` is the explicit path cut used by variant A. Covers witness reachability of its call, not behavior after it. No handwritten algorithm summary is claimed. See [R6 §2/§5][R6], [W2 O1-A][W2]. |
| Assumptions / covers | Length, offset, sorted-prefix, label-domain and valid-allocation premises must be explicit. Accepted positive rows require the relevant covers. U-1's 0 covers are failure to reach the intended experiment. Negative controls may fail before their final cover; their failed check must be localized and match the intended condition. See [EXPERIMENT][LANE], [L1 grouping ledger][L1], [L2 controls][L2], [U-a][L1U]. |
| Architecture / resources | Historical proofs are Linux lane measurements, not macOS results. There is no generic claim over architecture or type layout. See [EXPERIMENT §5–5b][LANE] and [R8 §2.1/L1-8][R8]. |
| Runtime correspondence | The assembly changes add verification harnesses and isolate controls; runtime std code is unchanged. The controls `check-cfg` declaration in `library/core/Cargo.toml` is a tooling declaration to disclose, not a runtime change. The four historical Linux request sources have identical `smallsort.rs`, `kani_k1.rs` and `kani_k1/` code to the old candidate `5c713131`. Between the second and third requests, a helper-script and documentation update was merged; it does not change verification flags or algorithm bodies. The final candidate adds only `mod correct;` and the unchanged `correct.rs` from `daf8d13e`; contract dependencies were compared with that source and retain the original formulation. See [the integration audit][L1D], [R8 §2.1][R8], [EXPERIMENT §5b controls][LANE]. |

`should_panic` is not used as the basis for the submission's safety claim. CD-1 found that it masks assertion-class failures, including ordinary assertions, index/overflow assertions and contract assertions. C-5 made all four tested non-assertion controls fail: `assume`, `unchecked_add`, overlapping `copy_nonoverlapping`, and `ptr.add` outside the allocation. Neither observation licenses removing a check. See [R6 §2][R6] and [W2 C-5 results][W2].

## Controls and mutants

Expected failures, diagnostic harnesses and displaced experiments are isolated under `cfg kani_smallsort_controls`; ordinary CI does not enable that cfg. C5 controls were restored in this configuration without `should_panic`. The selected positive suite passed build `1e761350-b663-4ab9-9f8e-361b17bacd8e`, gate true (13/13). After replacing contract-function stubs with direct original/copy callbacks, the five positive K15 checks passed again in build `5864ad2e-bebf-46e7-91ec-687ecf238215`, gate true, covers 6/6.

Build `ee1f96a2-babb-4c89-82de-f6a0a2d71e26` ended `COMPILE_ERROR`; every harness was `NOT_RUN`. The exact error was `Failed to find contract closure __kani_recursion_check_insert_tail in function core::slice::sort::shared::smallsort::insert_tail`. This is a Kani `kani::stub` limitation for a contract-bearing function, not a failed property or a killed mutant. The final controls use direct calls to the original implementation and its copy instead.

Build `b9c1952b-8e00-4488-b5f8-6904cd700fdc` ran with controls enabled and gate true. It produced 11/11 expected negative results, each with exactly one localized failed check and no unrelated failure, plus `smoke::ok` SUCCESS with 2/2 covers. The K15 evidence has a narrow scope: five selected original/copy pairs use shared `FnOnce` check helpers; each copy changes one operation while keeping the same witness input and property. This shows sensitivity of those selected witnesses. It does not show that the entire earlier safety suite detects all five mutations. A separate presorted-length mutant also fails on the previously accepted K10 N10 harness.

| Control | Expected check and location | Result |
|---|---|---|
| `assembly::k15_mutant_swap` | `v[0] <= v[1]` (`assembly.rs:28`) | FAILED, 1/80; cover 1/1 |
| `assembly::k15_mutant_insert` | `v[0] <= v[1]` (`assembly.rs:38`) | FAILED, 1/102; cover 1/1 |
| `assembly::k15_mutant_merge_up` | `advancement_ok` (`assembly.rs:61`) | FAILED, 1/61; cover 0/2 after the assertion |
| `assembly::k15_mutant_merge_consumption` | `count(&src, probe) == count(&result, probe)` (`assembly.rs:93`) | FAILED, 1/144; cover 1/1 |
| `assembly::k15_mutant_presorted_len` | `v[0] == 0 && v[9] == 1` (`assembly.rs:102`) | FAILED, 1/191; cover 0/1 after the assertion |
| `network::k15_mutant_existing_k10_presorted_len` | `sorted_by(&v, &mut cmp)` (`network.rs:1549`) | FAILED, 1/377; covers 3/3 |
| `merge::w2_c5_intrinsic_assume` | `Rust intrinsic assumption failed` (`merge.rs:1472`) | FAILED, 1/139; cover 1/1 |
| `merge::w2_c5_unchecked_add` | `attempt to compute unchecked_add which would overflow` (`num/uint_macros.rs:1039`) | FAILED, 1/153; cover 1/1 |
| `merge::w2_c5_copy_nonoverlapping` | `memcpy src/dst overlap` (`ptr/mod.rs:582`) | FAILED, 1/126; cover 1/1 |
| `merge::w2_c5_ptr_add` | `Offset result and original pointer must point to the same allocation` (`lib.rs:357`) | FAILED, 1/137; cover 1/1 |
| `smoke::control_must_fail` | `has_efficient_in_place_swap::<[u8; 9]>()` (`smoke.rs:50`) | FAILED, 1/1 |
| `smoke::ok` | positive control | SUCCESS, 0/2 failed; covers 2/2 |

All table names have the common prefix `slice::sort::shared::smallsort::kani_k1::`; check locations refer to source `9ab85b24`. Controls are enabled only with cfg `kani_smallsort_controls`. Select the full harness name with the pinned Kani and verification flags in the trust ledger; the expected localized check is listed in the table.

The C5 failures check the four listed non-assertion conditions; they do not establish every UB category. The unsupported uninitialized-read diagnostic and its limits remain separate from these controls. No `should_panic` harness is used as proof credit.

## Extended layer: evidence outside CI

The original u64 merge contract (formulation 1) succeeded at N20 in 3460.9 s on [build a06eb982-3175-4375-8bd3-b16c75c4e54e][EXT], and at N24 in 14011.6 s on [build f745482f-1c58-4966-b901-b3077d25b151][EXT]. These were Cloud Build **32 GB resource** runs. They provide additional evidence for those exact lengths but exceed 600 s and do not count toward ordinary CI. N28/32 were not run; extrapolations are not proofs. See [RESULT-ext][EXT], [W2 extended-layer table][W2], [EXPERIMENT §5a][LANE].

E-2 separately checks B4 insertion safety for u64 N16..20 with **every offset 1..N**: `ext_b4_u64_n16`…`ext_b4_u64_n20`, [build 177675c6-c058-4a77-9c27-f3ed937288cf][EXT]. This is also the **32 GB resource lane, outside CI credit**. SUCCESS within 600 s on that lane does not establish the primary-lane acceptance criterion. B4/u64 N16..20, together with O3/`Cell<K13Tagged>`, is now also established in the 16 GB primary layer with all offsets: **L1-5 complete**. E-2 remains additional resource-lane evidence, separate from that primary-layer result ([E-2 results and review][EXT], [L1 final table][L1]).

The earlier K-1 experiments expose an instrumentation limit as well as solver cost. On CircleCI 13 GiB, one experiment with the permutation counter and a trivial loop invariant OOMed in `goto-instrument`, while removing the counter in a separate experiment allowed instrumentation to complete. On the separate 32 GB resource lane, full-invariant instrumentation also hit SIGKILL near 30.5 GiB, including [build 929ef63e-58d2-4838-8a42-c5465d96797a][MERGE]. Ordinary proofs of the loop-invariant formulation also timed out at 60 minutes on the 32 GB lane, with and without that invariant ([K-1 phase 7 B/C][K1]). These are distinct instrumentation experiments, not an N32 proof. See [REPORT-K1 §3][K1], [R4 §4 item 2][R4]. The instrumentation and solver limits are recorded here as measured constraints; no extrapolated runtime or memory claim is made.

The early revision-4 plan estimate of roughly 3.2× growth per extra 4 elements and the later N20/N24 timings are observations on different experiments, not a complexity theorem or a precise N32 runtime prediction. For the original formulation the later measurements show a time bottleneck even when measured process RSS is modest. The new Tagged formulation reached STOP after the N24 run exceeded the 600-s target; no speedup is asserted ([REPORT-K1][K1], [W2 §1][W2], [L2 comparison protocol][L2]).

## SAFETY comments

The known `merge_down` SAFETY-comment deficiency is recorded by the plan as rust-lang/rust#135984. This draft records that source-reported issue; it does not claim to have changed upstream or audited the issue's current resolution. The source-reported reference is retained as context, without a claim about its current upstream status. See [R4 §4 item 7][R4] and [requirements E5][REQ].

## CI resources

The final integrated candidate is `ac0dbbf0fbf1ee8b90ca77c186c2058a96acbbad`. Build `d19d306d-43ef-44dc-a79a-fd0c0a8049cf` completed with gate true, 3/3 SUCCESS and covers 12/12; its tooling matched the declared base. It checks compilation of the included suite plus two accepted L2 fallback callers and the existing C3 predicate. This is not a full-suite platform run. The [integration record][L1D] reports the exact source, checks and resource limits.

| Integration harness | Status | Verification time | Failed / total checks | Unreachable checks | Covers |
|---|---|---:|---:|---:|---:|
| `correct::l2_fallback_u64_n8` | SUCCESS | 46.489067 s | 0/485 | 60 | 1/1 |
| `correct::l2_fallback_u8_n9` | SUCCESS | 51.96637 s | 0/478 | 61 | 1/1 |
| `smoke::w3_efficient_swap_c3` | SUCCESS | 0.0975772 s | 0/10 | 0 | 10/10 |

The measurement used the 16 GB Linux machine with jobs1, controls and uninit checks off, swap off. Whole-run wall was 164.44 s; max single-process RSS was 1740144 KiB, and aggregate RSS sampled every 2 s peaked at 2.01 GiB. These are build-wide measurements, not individual harness peaks or concurrent whole-suite memory. The other imported L2 instances retain their [source-reported evidence][L2]. Final ubuntu/macOS results remain `TODO (coordinator, final CI run)`.

The earlier build `d111012e-ed67-4b74-95db-5aa2d843a5df` ended TOOL_ERROR, gate false: the controls-only `smoke::ok` name did not match while controls were off. All three selected harnesses were NOT_RUN. That selection error is not a property counterexample and adds no proof credit.

The separate old candidate for Cloud Build calibration and the macOS run is `5c713131f8b92c629f0c16b68605ec2bf2547007`. The selected C3 i32 measurement passed; complete-suite evidence is recorded per partition below. Cloud Build Linux runs use the organizer's four count-based partitions with `KANI_JOBS=2`; the separate [macOS candidate measurement][MACOS] uses the default `-j` with no `KANI_JOBS`. Historical 32 GB resource results do not substitute for either platform.

| Required measurement | Current status |
|---|---|
| Cloud Build Linux 1/4 (calibration) | Source `1ba746138fb7b17b355166dc091f7b0bdd70ae7b`; build `b796ca7b-fa1c-4dd2-ba06-8b3fb22e18e7`: gate true, 521/521 SUCCESS, no list inconsistency; SmallSort 0. Wall 80:28; pre-verification compile/setup estimate ≈55.5 min; sampled aggregate RSS 5.11 GiB, swap off, no OOM. Slowest: `num::imp::dec2flt::decimal_seq::decimal_seq_verify::check_left_shift`, 180.39307 s. |
| Cloud Build Linux 2/4 (calibration) | Source `9d204ebfc497dd05d18290857151b4a537b3e724`; build `dbfe8043-e99e-49e0-a794-5e103e73f025`: PARTIAL, gate false, timeout (exit 124). Assigned 521; reported 503: 501 SUCCESS, 2 UNKNOWN; 18 missing. SmallSort reported 248, not a complete domain. Sampled elapsed 318 min; wall/time-v RSS unparsed. Compile/setup estimate ≈45.6 min; sampled aggregate RSS 13.16 GiB, swap off. Slowest completed: `network::w2p2_k10_u64_n14`, 1511.9186 s. |
| Cloud Build Linux 3/4 (calibration) | Source `3796a1ac751be151931971d25a1281d85058f642`; build `ef4345ad-8ebd-45cc-93ef-a33dbdc6b505`: gate true, 521/521 SUCCESS, no list inconsistency; SmallSort 0. Wall 65:19; pre-verification compile/setup estimate ≈43.7 min; sampled aggregate RSS 4.16 GiB, swap off, no OOM. Slowest: baseline `num::nonzero::verify::nonzero_check_isqrt_u32`, 628.47455 s. |
| Cloud Build Linux 4/4 (calibration) | Source `7281d216696e94182aeb9dedef91f407f30136f9`; build `aea9fcc6-b301-4f9c-a49a-a6858b34b0dc`: gate true, 519/519 SUCCESS, no list inconsistency; SmallSort 73. Wall 285:15; compile/setup estimate ≈50.1 min; sampled aggregate RSS 7.46 GiB, swap off, no OOM. Slowest: `merge::w2p2_bm_u64_len16`, 1270.3354 s. |
| macOS, candidate `5c713131f8b92c629f0c16b68605ec2bf2547007` | [Run `40603213401`, report at `41659f9f`][MACOS]: all four partitions COMPLETE, 520/520 SUCCESS each, gate true, no worker-list inconsistency; longest job 123 min of the 360-min limit. Default `-j`; p1/2/4 used 3 CPU / 7 GB, p3 used 5 CPU / 14 GB. Only p2 swapped: 756 MB peak. |
| Final Linux (ubuntu-latest), integrated candidate `ac0dbbf0fbf1ee8b90ca77c186c2058a96acbbad` | TODO (coordinator, final CI run). |
| Final macOS, integrated candidate `ac0dbbf0fbf1ee8b90ca77c186c2058a96acbbad` | TODO (coordinator, final CI run); the completed old candidate run above remains separate evidence. |

The Cloud Build results are calibration measurements, not measurements of organizer CI. Cloud Build `e2-standard-4` with jobs 2 took longer on partition 2 than the macOS candidate run: p2 verify wall 104.4 min (job 108 min). Cloud Build worker 2 timed out with an incomplete inventory, while worker 4 completed in 285:15; both exceeded an internal 240-min target (not an organizer limit). No repeat or repartition is included here. The integrated GitHub Actions run on `ubuntu-latest` and macOS remains TODO for the coordinator. The old candidate measurements do not cover `correct.rs`. The completed macOS run has the qualifications below. All four Cloud Build runs are terminal; three workers completed, and worker 2 remains an incomplete verification result. See [R8 §2.1][R8].



The Cloud Build Linux 2/4 timeout reports no failed assertion for its two UNKNOWN harnesses, `network::w2p2_k10_u64_n8` and `network::w2_network_o1_a_18_21`. The first missing harness is `network::w1_network_o1_nomerge_u64`; the final completion line is absent. This is incomplete verification, not an established counterexample and not acceptance of the entire worker list. A 501-SUCCESS subset does not close the partition.

The six longest completed SmallSort harnesses in Cloud Build worker 2 exceeded 600 s: `network::w2p2_k10_u64_n14` 1511.9186 s, `network::w2p2_k10_perm_u64_n12` 1129.8988 s, `network::w2p2_k10_u8_n17` 1081.5977 s, `network::w2p2_k10_u64_n13` 892.31537 s, `merge::w2p2_gs_u64_len12` 816.43677 s and `merge::w2p2_gs_u64_len16` 618.8711 s. Cloud Build worker 4 also has seven SmallSort results above 600 s, led by `merge::w2p2_bm_u64_len16` at 1270.3354 s and `network::w2night_k8r_start1_u64` at 1076.4733 s. Earlier individual measurements do not establish the same bound under concurrent whole-suite execution. The baseline Linux 3/4 harness `num::nonzero::verify::nonzero_check_isqrt_u32` also took 628.47455 s; it is outside SmallSort.

Compilation succeeded sufficiently to begin verification in each reported Linux worker. The first `Checking harness` log line has no timestamp: pre-verification times above are estimates from the first sampled `goto-instrument`/`cbmc` process, not exact compilation durations. Partition 2's time-v wall and max RSS did not parse; 318 min is sampler elapsed, a lower bound on whole-run time, and is not substituted as an exact wall measurement. Aggregate RSS is sampled every 2 s and can miss transient peaks. The summaries report 1085.811 s, 30935.522 s, 1631.208 s and 21879.552 s of total verification time for workers 1–4 respectively; these sums overlap in concurrent runs and are not wall times. The interface does not expose separate SmallSort-only time sums for workers 2 and 4; those sums are omitted. Workers 1 and 3 contain no SmallSort harnesses, so their SmallSort-only sums are zero. Exact whole-run wall and the full missing-harness inventory remain unavailable through this report.

### macOS result and resource limits

The [macOS report][MACOS] records GitHub Actions run `40603213401` on the candidate plus its workflow only, with Kani `9461e07a` built before the timed step. Every partition completed and its worker list matched its reported harnesses. The following figures are reproduced from that report.

| Partition | Result | SmallSort kani_k1 | Verify wall | Job total | Max process RSS | Peak swap | Actual runner |
|---|---|---:|---:|---:|---:|---:|---|
| 1/4 | COMPLETE, 520/520 SUCCESS, gate true | 0 | 32.7 min | 39 min | 3.27 GiB | 0 MB | 3 CPU / 7 GB |
| 2/4 | COMPLETE, 520/520 SUCCESS, gate true | 261 | 104.4 min | 108 min | 3.98 GiB | 756 MB | 3 CPU / 7 GB |
| 3/4 | COMPLETE, 520/520 SUCCESS, gate true | 0 | 20.1 min | 23 min | 4.83 GiB | 0 MB | 5 CPU / 14 GB |
| 4/4 | COMPLETE, 520/520 SUCCESS, gate true | 73 | 117.0 min | 123 min | 2.84 GiB | 0 MB | 3 CPU / 7 GB |

The longest job was 123 min of the 360-min job limit. Partition 3's actual runner had more resources despite requesting `macos-latest`, so this run does not establish that partition on 7 GB. Only partition 2 swapped, at a 756 MB peak, and completed. Summed process RSS over-counts shared pages on macOS and is not used as a physical-memory measurement. Architecture details beyond the report's recorded runner information are not inferred here.

The report records SmallSort times above 600 s: p2 `network::w2p2_k10_perm_u64_n12` 750 s and p4 `merge::w2p2_bm_u64_len16` 803 s. Partition completion therefore does not establish a 600-s per-harness bound on macOS. The macOS report records a target-specific list of 2080 harnesses, 520 per partition. The completed Linux calibration records assign 521/521/521/519 harnesses; the target-specific difference has not been investigated. These results exclude the later `correct.rs` integration, which needs a new final macOS measurement. All counts, times and resource figures in this subsection come from [the macOS run report][MACOS] and were not recalculated or rerun here.

## Evidence snapshots

The historical partition code snapshot is `5c713131f8b92c629f0c16b68605ec2bf2547007`. Linux request sources are `1ba746138fb7b17b355166dc091f7b0bdd70ae7b`, `9d204ebfc497dd05d18290857151b4a537b3e724`, `3796a1ac751be151931971d25a1281d85058f642` and `7281d216696e94182aeb9dedef91f407f30136f9`. The [current result index][L1] records their build IDs, tooling checks, completeness and resource limits, alongside the earlier control and single-harness results. Historical reports and the separate Tagged experiment remain pinned in the references below; their outcomes are not silently extended to new types, lengths or platforms. The [macOS report][MACOS] applies to the same code candidate plus its workflow only. That snapshot predates the `correct.rs` integration. The final candidate is `ac0dbbf0fbf1ee8b90ca77c186c2058a96acbbad`, with the three-harness integration result in [L1D]; the integrated suite still needs the final organizer CI run.

[REQ]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/73ed3906fa25fba9efed3e0669b0b6aeae377d91/research/challenge-8/REQUIREMENTS-INTERPRETATION-2026-10-24.md
[R8]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/73ed3906fa25fba9efed3e0669b0b6aeae377d91/research/challenge-8/CH8-PLAN-R8-2026-10-27.md
[R6]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/73ed3906fa25fba9efed3e0669b0b6aeae377d91/research/challenge-8/CH8-MINIMAL-PLAN-R6-2026-10-26.md
[R4]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/73ed3906fa25fba9efed3e0669b0b6aeae377d91/research/challenge-8/CH8-MINIMAL-PLAN-R4-2026-10-26.md
[W1]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/1052dee57addafe3bf2389894eb99c381f4aa4f0/research/challenge-8/kani-k1/REPORT-W1-2026-10-26.md
[W2]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/1052dee57addafe3bf2389894eb99c381f4aa4f0/research/challenge-8/kani-k1/REPORT-W2-2026-10-27.md
[K1]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/1052dee57addafe3bf2389894eb99c381f4aa4f0/research/challenge-8/kani-k1/REPORT-K1-2026-10-26.md
[LANE]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/d5dc2c5fbf0da8210022112de12d25dce923934f/research/challenge-8/kani-k1/EXPERIMENT.md
[NET]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/b0f457cc51f5ad39c4e6d5c2bcdc21b3dc658ece/research/challenge-8/kani-k1/RESULT-network.md
[MERGE]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/b0f457cc51f5ad39c4e6d5c2bcdc21b3dc658ece/research/challenge-8/kani-k1/RESULT-merge.md
[EXT]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/b0f457cc51f5ad39c4e6d5c2bcdc21b3dc658ece/research/challenge-8/kani-k1/RESULT-ext.md
[L1U]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/b0f457cc51f5ad39c4e6d5c2bcdc21b3dc658ece/research/challenge-8/kani-k1/RESULT-w3-l1u.md
[L1]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/537e8931f52a00c7260f7adb42636ff7a5b76e3f/research/challenge-8/kani-k1/RESULT-w3-l1.md
[L2]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/daf8d13ef1ec9ba67549727ce1fd08fda50d7dd1/research/challenge-8/kani-k1/RESULT-w3-l2.md

[MACOS]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/41659f9ff4f71bf4902da5d8c06ff90c1b8fa9c6/research/challenge-8/kani-k1/MACOS-L1-8-2026-10-28.md

[L1D]: https://github.com/Tiramisu-Cake/verify-rust-std/blob/bf264ac2e90138a4cd48a962e3b62db752750274/research/challenge-8/kani-k1/RESULT-w3-l1.md
