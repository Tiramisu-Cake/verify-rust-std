# S5 — harness integration and time budget (PLAN ONLY)

Status: **READY_FOR_COORDINATOR_REVIEW; S5 PASS NOT_ESTABLISHED**.
Authority: coordinator's w15 assignment, 2026-11-19, one planning stage.
Worktree `/root/verify-rust-std-kani3300-g0`, branch
`experiment/kani-k1-kani3300g0-20261111`; entry `8896f60ae9`.
No execution request, cap increase, deletion, provider promotion or publication is authorized here.

## Frozen inputs and present coverage

All source references below are to std **`8faf8e62af8f82b5c46af020086f8df591b6757e`**,
tree `91f097cdb4085d30c4b94afbb843aeb34f1d3287`, read using `git show` from
`/root/verify-rust-std-ch8-s4p-2-w13`. File names abbreviate
`library/core/src/slice/sort/shared/smallsort/verify/` unless stated otherwise.
[SOURCE-INVENTORY.json](SOURCE-INVENTORY.json) records file hashes and every
lexically identified direct proof declaration / harness-generating macro invocation:
248 legacy candidates including opt-in controls, and 76 `sorting_*` candidates.
These counts are **source inventory**, not native discovery or the historical 235-root CI count.
[INPUTS.json](INPUTS.json) binds curated inputs and parent/control source hashes;
[BUDGET-MATRIX.json](BUDGET-MATRIX.json) makes the proposed lengths and unchanged caps explicit.

Admission [8896f60ae9](../../ch8-s4/admission-s4p2-r2-network/ADMISSION.md) accepts exactly
four `QUALIFIED_BOUNDED_SOURCE_REPORTED` cases from run **44548842328/1**:
`sorting_s4_network_r2::s4p2r2_network_b01_n{02,03,04,00_01}_fullbyte`.
They cover the actual `small_sort_network<u8, KeyLess<u8>>` at N0..4, Original/Proof,
target null, initialized V34/base1, all 34 independent full bytes, full sortedness and
multiplicity, complete outside frame and arbitrary outside canary. No stubs are enabled.
Four SUCCESS assertion roles and SAT covers 6/6/6/3 were retained. Actual byte order is
`a < b`, not the older profile order `(a >> 1) < (b >> 1)`.

Earlier [fallback admission](../../ch8-s4/admission-s4p1-r1-fallback/ADMISSION.md)
accepts two exact Cell/KeyLess fallback blocks N0..2 and N3..4 from **44481580554/1**,
with their own exact metadata exception. This does not extend that exception to another
run. S1 smoke, S3 leaves and other historical admissions retain their original identities
and limits. This plan grants **zero** new leaves, proof obligations or B1/B2 credit.

## Replacement table

`O` = actual Original body, ordinary `Proof`; `C` = actual-body `proof_for_contract`;
`V` = consumer with `stub_verified`; `S` = ordinary/panic/weak-seam stub (explicitly
retained scope). A C root can still use Original bodies for its nested calls.
Mode equality includes the exact target instance, target null/contract target, selected
Check/Replace behavior and every enabled stub; an attribute alone is insufficient.

Cfg: `L` = ordinary legacy inventory under enclosing `cfg(kani)`; `X` adds
`kani_smallsort_controls`; `S1` adds `kani_smallsort_sorting`; `P4` adds to S1
`kani_smallsort_s2_assumed`, `kani_smallsort_s3_leaf`, `kani_smallsort_s4_partition`.
P4 is the current experimental profile; its name does not mean selected positives use summaries.
Every abbreviated root below has its module and source line in SOURCE-INVENTORY.json.
The table groups roots with the same replacement decision, without dropping any legacy module.

| Old harness / family | T, comparator, lengths and geometry | Old mode; cfg/discovery | New coverage or proposed equivalent | Remaining gap / deletion decision |
|---|---|---|---|---|
| `network::network_correctness_u8_n0_to2`, `...n3_to4` | u8, exact fn-item `strict_less::<u8>`, N0..4, exact `[u8;N]`/base0; real Unstable entry; order + independent full-value probe count | O; L | Admitted r2 N01/N2/N3/N4 has full-byte order/count for the direct helper at V34/base1 | Same value-order formula, but different F, allocation geometry and trait entry/forwarding. Bind actual trait path, callback equivalence, and base0/exact-size versus interior backing before deletion. **KEEP** |
| `network::network_correctness_u8_n5/6/7/9/10/11/12/13` | u8/strict_less, enumerated N; N<9 count+order, N>=9 order only; no N8 root in this family | O; L | Proposed N partitions in final matrix would strengthen value properties on their own domain | All lengths >4 open; trait/F/geometry correspondence still required. N8 is a coverage hole to add, not an existing root to remove. **KEEP** |
| `network::network_correctness_u64_*` | u64/strict_less, N0..7 and9; count only below9 | O; L | No equivalent admitted new coverage | Width/layout/comparator and full-value count differ. u8 is not a u64 theorem. **KEEP** |
| `merge::general_stable_sorted_permutation_{u8,u64}_n0/n1`, `general_stable_direct_u8_n2..n8`, `general_stable_direct_u64_n2..n5`, split `general_direct_u64_n6..n9`, `stable_direct_u64_n6..n9`, `general_direct_u8_n9`, `stable_direct_nonconst_u8_n9` | Exact lt_u8/lt_u64 fn-items, upper-seven-bit key, full-value probe; direct general and Stable entry; scratch48 (const/nonconst construction) versus stack scratch | O; L | Proposed general KeyLess/u8 N0..32 partitions are a new stronger full-byte domain, not these canonical profiles | Different ordering/equal-key classes, F, u64 width, entry and scratch allocation/construction. Need matched proofs or a checked equivalence argument preserving full values and both routes. **KEEP** |
| `merge::fallback_sorted_permutation_u8_u64_n0..n6` | Each root branches across u8/u64 with lt_* upper-bit order, exact arrays/base0 | O; L | Admitted Cell/KeyLess N0..4 is only adjacent coverage | Cell versus scalars, both widths, F/order and N5/6 missing. Preserve both branches. **KEEP** |
| `types::sorted_permutation_traits_fallback_cell_u8_n0_to2/n7`, stable/unstable Cell N8 roots | Cell<u8>/logical_less, full-byte order + probe; exact arrays, both trait entries and scratch48 where applicable | O; L | Cell direct fallback N0..4 admission; S1 Cell entry smoke is separate historical evidence | Direct helper does not prove both trait bodies; N7/8, F and fixture geometry remain. **KEEP** |
| `types::sorted_permutation_traits_general_drop_u8_n0_to2/n8` | DropKey/logical_less, non-Copy **with Drop**, Stable/Unstable entries | O; L | NonCopyByte/KeyLess general is a proposed different pair | No-Drop NonCopyByte does not cover DropKey destruction or entry/F equivalence. **KEEP** |
| `forwarding_contracts::{stable_cell_n2,unstable_byte_n2,freeze_noncopy_n2}` | Cell/u8/NonCopyU8, exact canonical fn pointers, key x>>1 + full-value probe, backing4/base1; stable scratch lengths0..2 including unread uninit tail | C adapters, actual entries; L; wrong-F/checker controls X | Proposed six S1 entry PFCs retain distinct implementation targets | KeyLess full-byte order, NonCopyByte identity, scratch and adapter contract differ. New direct-helper leaves cannot replace forwarding contracts. **KEEP** |
| `network::swap_contract_four_positions_*`, `swap_contract_*`, `contract_insert_tail_u8_prefix`, `insert_tail_contract_u64_start1_*`; `merge::{sort4_contract_*,merge_contract_*,merge_scratch48_contract_u8_n9}` | u8/i32/u64/Drop/Cell<i32>/arrays16/17 as exact profiles; canonical fn pointer guards, often key x>>1; swap backing2/4/9/13/17; tail spans through17 (u64 start1 tail16 means relative position15); sort4 separate allocations; merge lengths2..9 incl scratch48 | C profile adapters; L; wrong-F controls X | S3 full-byte actual leaves may be useful prerequisites only on matched domains | Preserve canonical guards, tied-key/full-payload classes, probe quantification, type/F and all src/dst contexts. Safety or one-probe summary is not automatically a full multiset provider. **KEEP** |
| `helper_contracts::*`, `helper_contracts_wide::*`, `insert_tail_contracts::*` positive PFCs | Reading arbitrary-bool F; swap u8/u64/bytes17 backing4, u8 backing9/13, wide backing32/interior base; insertion u64 N2/3/offsets, tail1..4 in5 and1..15 in17; sort4 separate u64; merge u64 N2/4 and8 at scratch48/src32/dst0 | C actual helper safety/frame; L | New sorted leaves with pure KeyLess have a smaller callback domain | Need same callback footprint, arbitrary answers, initialization/frames and exact geometry; scalar order proof does not subsume these contracts. **KEEP** |
| `helper_contracts::unstable_network_safety_u8_n9_stubbed/n13_stubbed`, `helper_contracts_wide::{unstable_network_safety_u8_n32_stubbed,sort8_safety_u64_scratch48_src32_dst0_merge_stubbed}` | Exact old T/F/provider targets and bounded caller geometries | O+V, auxiliary S and panic S as in source; L | No admitted new summary edge | Require same-version actual callee contract proof AND matched caller, precondition, frame, initialized destination and full relation. Admitted bounded leaves remain leaves. **KEEP** |
| `network::{network_safety_*,dispatch_safety_*,dispatch_reachability_*}`, `merge::route_safety_all_routes_*` | u8/u64, bytes16/17/85/86, DropValue/WrappedU64; arbitrary reading answers; lengths listed exactly in source inventory, boundary17/18/31/32; six dispatch/size classes | O, some order-violation panic S; L; solver-specific attributes retained | Six KeyLess entry PFCs only cover the selected three tiny types | Lawful KeyLess does not cover arbitrary answers, large/size>16 paths, payload reads, panic-cut semantics or all specializations. **KEEP** |
| `network::{insertion_safety_*,insertion_permutation_*}` | u64 arbitrary-reading answers incl all selected offsets throughN20; u8/u64 arbitrary answer permutation N10/11/14 as named | O, source-specific panic S; L | Insert-tail KeyLess p1..16 is a potential functional prerequisite | One tail operation does not cover whole shift loop, offsets, N17..20, widths or arbitrary-F domain. **KEEP** |
| `network::{mutating_route_safety_*,mutating_insertion_safety_*,mutating_route_permutation_*}` | Cell<TaggedKey>; comparator mutates keys; route safety N0..16, insertion through20/offsets, tag permutation N2/3/4 | O with source-specific panic boundary; L | No equivalent pure KeyLess coverage | Mutable keys/identity preservation and arbitrary comparison history are distinct. **KEEP** |
| `merge::sort4_arbitrary_comparator_*`; `network::swap_same_position_u8`, `unstable_freeze_noncopy_bytes86_fallback_n2` | sort4 u64/bytes16 arbitrary answers; coincident swap including true on equality; NonCopyBytes86/read-bool fallback N2 with full86-byte values | O; L | None | Distinct callback/alias/size/layout axes. **KEEP** |
| `merge::drop_{fallback,general}_{drop_count,tag_permutation}_*` | DropTaggedValue, mutating/arbitrary comparator, N2/4/8 and general Drop-count16; alternate insertion/fallback and general/stable | O+panic S; L | None | Drop count, identity multiplicity, alternate routes and panic scope are not full-byte sorting. **KEEP** |
| `tag_permutation::{tag_types_preserve_source_routes,network_u8_n9,network_u8_n13}` | Fixed distinct identity tags, fresh arbitrary answers, real trait path, tag mask/range | O+panic S on network roots; L | None | Sortedness of full arbitrary bytes for one lawful F does not cover every returning answer sequence or source-type route predicates. **KEEP** |
| `scratch_geometry::stable_u64_min_scratch_n2` | u64 arbitrary reading answers, separate exact minimal scratch18, frame | O+panic S; L | None | Fixed scratch48 or u8 V34 is not minimum scratch/locality proof. **KEEP** |
| `fixed_inputs::*` positives | Fixed swap/tail/merge_up/merge/network-prefix witnesses; unit ZST stable N1/2/7/8/16/17/31/32 with zst-aware comparator | O, explicit panic S as source; L | None | Witness/helper advancement and ZST dispatch domains remain. **KEEP** |
| `smoke::predicate_efficient_swap_type_matrix` | u8/u16/u64/u128, arrays9/16/17/85/86, Drop, Cell<i32>, unit | O; L | None | A network result is not the type/layout predicate matrix. **KEEP** |
| All opt-in old negative roots across `merge::profiles`/helper/forwarding/fixed/tag modules, plus `mutations` dependencies | Exact bad F, corruption, overlap, out-of-bounds or callback-write fixtures, intended label/site | O/C/V/S as pinned; X | Keep and requalify each affected control against its changed target | Four campaign negatives do not replace these different rejection obligations. **KEEP** |
| `sorting_s4_network_partition::s4p2_network_b01_n{02,03,04,00_01}_fullbyte` | Same u8/KeyLess/V34/base1, old singleton usize / symbolic N01 slices; N0..4 | O; P4; old positive runs censored at child600 | r2 has explicit domain correspondence in `network-r2-impl/DOMAIN-EQUIVALENCE.md`, admitted complete results at unchanged caps | Closest replacement candidate: review exact source transformation, both N01 branches and all roles/covers; future compiler discovery and source-preserving integration gates still required. Historical timeout evidence immutable. **No deletion in this stage** |
| `sorting_s4_partition::s4p_network_b01_n00_02_fullbyte`, `...n03_04_fullbyte` | Same finite network domain, grouped symbolic lengths | O; P4 | r2 disjoint union N01+N2 and N3+N4 | Preserve grouped-domain cover obligations, independence, full frame and non-vacuity; no automatic transfer of admission between invocations. **KEEP pending reviewed replacement** |
| Six `sorting_entry_smoke` symbolic roots and their16 exact-N splits; other S2/S3/bridge candidates and controls | Three exact KeyLess pairs, N0..3 S1 with backing5/base1, scratch19 prefix n+16; leaves have their own domains/modes | C entry targets; S1; S2/S3/P4 cfg hierarchy separate | Proposed final six entry PFC targets; each needs its own full accepted domain | No direct-helper union substitutes PFC/forwarding/threshold assertions. Exact-N and symbolic union equivalence must be accepted separately; do not merge composite600/1200 historical runs into fit600. Unselected/partial/init-open diagnostics stay explicit. **KEEP** |

## Discovery and equivalence gate before any deletion

1. Freeze the old and proposed std/tool/control/request hashes; preserve originals and
   their prior receipts. This source pin differs from the historical #752 tool pin;
   compatibility and organizer-pin acceptance remain separate gates.
2. Obtain compiler-discovered inventories later under L, L+X, S1 and P4 (and the
   intermediate S2/S3 gates when affected). A static macro scan does not prove registration.
   Match full crate/module/root, actual registration kind, contract target, T, **exact F**,
   enabled model, selected stubs, solver/unwind/check flags and target. Ordinary discovery
   must neither lose retained roots nor acquire experimental/negative roots accidentally.
3. For each old root to remove, record old domain D, new domains Di and the reviewed
   mapping showing D is covered by their union. This includes all values, lengths,
   comparator state/answers, backing/base/src/dst/scratch/init ranges and outside frame.
   Equal Rust signatures or equal length sets alone are insufficient. Full-byte order
   cannot replace upper-bit order with distinct tied payloads without a correspondence proof.
4. Map every old postcondition, contract/forwarding obligation, useful cover and safety
   check to retained complete native evidence. Require all feasible covers SAT; retain
   exact expected failures and source/property identities. U, guards and system metadata
   require current exact-case review/admission, not a blanket historical exception.
5. A summary edge requires a proved same-version actual callee contract for that caller's
   domain, all premises established at the call, initialized output/frame/count semantics
   and a qualified consumer. No bounded Original leaf is promoted just by registration.
6. Independent review, separately authorized measured final CI on the frozen candidate,
   and coordinator acceptance precede removing roots. Diff discovery and rerun affected
   controls after integration. Keep old roots if the replacement cannot preserve coverage.
   No PR/issue update or deletion is part of this planning stage.

## Compact final matrix proposal

This is a **23-positive target core**, not 23 implemented/proved roots and not a complete
replacement for the retained legacy inventory. Prefer literal call/snapshot/post slices
when partitioning; symbolic length remains independent of values. Every length in each
partition needs a reachable return witness. Large partitions must be calibrated; no
fit assertion follows from small-N timings. Further splits require a revised explicit
matrix and accounting, not silently dropped lengths or changed caps.

| Row IDs | Count | T/F; target and lengths | Required result / current state |
|---|---:|---|---|
| F0,F1,F2 | 3 | Cell<u8>/KeyLess<Cell<u8>>, actual fallback, {0..2}, {3..4}, {5..16} | Original/Proof, full logical-byte order/count/outside frame, initialized V34/base1. First two are exact historical bounded admissions; F2 OPEN |
| G0..G3 | 4 | u8/KeyLess<u8>, general, {0,1}, {2..7}, {8..15}, {16..32} | Original/Proof; private scratch48, plus separately matched external Stable scratch contexts. All proposed full partitions OPEN |
| N0..N9 | 10 | u8/KeyLess<u8>, network, {0,1}, {2}, {3}, {4}, {5..8}, {9..12}, {13..17}, {18..24}, {25}, {26..32} | First four correspond to exact admitted r2 leaves. Remaining six OPEN. Include N8, N17 tail16, mixed25 and merge/copy-back cases |
| E0..E5 | 6 | Six **distinct** actual implementation PFC targets: Stable default Cell; Stable Freeze u8; Unstable default Cell; Unstable Freeze u8; Freeze default NonCopyByte; Freeze Copy u8 | Exact KeyLess pair, model enabled and threshold/layout/return/frame checks. Target lengths0..16 for defaults,0..32 for Freeze routes. Start from separately admitted S1 smoke domains; full domains OPEN |
| C0..C3 per campaign | 4 | Existing `checker_order_corrupt`, `checker_count_corrupt`, `sort13_weak`, `s4p_cell_count_corrupt` | Exact intended native FAILURE labels, existing modes/stubs, no extra failure. Unchanged34/36 unwind; controls grant no positive proof |
| R (retained legacy) | inventory-dependent | Every legacy row without accepted equivalence, plus its relevant controls | Mandatory preservation lane; core is not full S5 while R is unmeasured/unqualified |
| P (provider prerequisites) | unresolved | swap, sort4/8, sort9/13, insert p1..16, merge2..32 and consumer geometries | May remain actual-body expansion. If summaries are proposed, add exact provider+consumer rows before E/full composition. No current blanket provider credit |

E rows must preserve six targets, not coalesce them because u8 reaches two related
traits. NonCopyByte general and its stack/allocation semantics need matching coverage;
u8 general is not its provider. G3 additionally needs all34 internal sort8/merge8
src/dst contexts; final merge all2..32 and network18..32 differ. External scratch
minimum n+16, scratch48 and larger/same-allocation disjoint contexts are not synonyms.

Keep the core as an opt-in target until legacy equivalence and total cost are established.
One possible future packing of the23 positives is five serial campaigns containing
5/5/5/5/3 positives plus the four unchanged negatives first: **9/9/9/9/7 invocations**.
This means43 invocations including repeated controls. It requires future runner/profile
work, review and authorization; the current fixed-eight request is unchanged. This is
an envelope calculation, **not five available attempts or a reservation**. If remaining
coordinator budget cannot accommodate the needed core, retained and prerequisite lanes,
report PARTIAL/OPEN rather than declaring S5 complete.

## S5 acceptance and handoff

S5 PASS requires (a) a reviewed old-to-new coverage map with no lost obligations,
(b) complete accepted results for the declared final matrix, including retained domains
and all required controls/providers/consumers, (c) actual cfg/native discovery and source
binding at the final pins, and (d) the time/memory and aggregate/shard gates in
[TIME-BUDGET.md](TIME-BUDGET.md). Functional initialized bounded credit, combined
uninit/validity/permission/ownership proof, generic/all-length claims, panic/unwind and
stability remain separately scoped; none is inferred from S5 packaging.

Next coordinator action: review this plan, select the first missing bounded domain
and its coverage contract, then issue a separate implementation/execution stage if desired.
The current network result justifies using concrete-call slicing as a planning pattern.
It does not justify a generic compiler/MIR causal claim, an exact speedup factor, or
rerunning all heavy roots without further decomposition.
