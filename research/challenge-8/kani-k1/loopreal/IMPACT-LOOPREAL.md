# Static regression scope

Snapshot: task `01cb5fc3cd`, library commit recorded in RUN-LEDGER.json.
Source inspection only; these are conservative source call paths, not a compiler-derived graph.
The real-loop attributes apply whenever Kani reaches these functions, including ordinary CI
with `-Z loop-contracts`; the `kani_smallsort_controls` gate protects only the new module.

| Entry/call family | Route to an annotated loop | Existing ordinary roots at risk |
| --- | --- | --- |
| `insert_tail` directly | inner `loop`, `CopyOnDrop::dst` | `assembly::sorted_permutation_insert_tail_u8_n2`, `realcontracts::insert_tail_safety_u64_tail1_to4_backing5` |
| `merge::specfix::insert_tail_profile` | real `insert_tail` body | `network::insert_tail_contract_*`, profile PFC and their consumers |
| `insertion_sort_shift_left` directly | outer `while`, then real `insert_tail` unless stubbed | `network::insertion_safety_*`, `network::insertion_permutation_*`, `merge::drop_insertion_*` |
| `small_sort_fallback`, default unstable/stable dispatch | real outer and inner insertion loops | `network::unstable_freeze_noncopy_bytes86_fallback_n2`, dispatch, drop, types and wrap fallback families |
| `small_sort_network` finishing region | real outer and inner insertion loops, when suffix nonempty | `assembly::sorted_network_prefix_u8_n10`, network/permtags/type routes; path depends on length |
| `small_sort_general_with_scratch` | real `insert_tail` on initialized scratch prefixes | `scratchgeom::*`, stable/general dispatch, drop and types families; path depends on length |

External source entry points also reach these loops:

- `slice/sort/unstable/mod.rs::sort`: length 2..20 selects real insertion directly;
  larger quicksort routes can reach `UnstableSmallSortTypeImpl::small_sort`.
- `slice/sort/stable/mod.rs::sort`: default non-size-optimized short-slice route uses insertion;
  drift/quicksort reaches `StableSmallSortTypeImpl::small_sort`.
- `slice/sort/select.rs::partition_at_index` and deterministic fallback select insertion for
  small subslices. The public `select_nth_unstable*` methods delegate to this entry.
- Public `slice::sort_unstable*`, `partial_sort_unstable*` and f32/f64 `sort_floats` delegate
  to unstable sort. Alloc `slice::sort*` and `sort_by_cached_key` also reach core sorting.

Searches covered direct `insert_tail`/`insertion_sort_shift_left` calls in `library/core/src/slice/sort`,
SmallSort trait/dispatch calls there, and sorting calls in `library/core/src`/`library/alloc/src`.
No explicit existing Kani proof root for those external public sorting entries was found in
this worktree. This does not establish an exhaustive compiler call graph or autoharness inventory.
The unchanged K-1 request validator (`HARNESS_RE`) accepts only SmallSort verify roots; G1
therefore measures the following five existing ordinary roots. The first three baselines
have bounded K-1 rows; the two ZST baselines are coordinator-reported Actions timings.

| Ordinary root under `verify::` | Historical verification seconds | Source | Coverage |
| --- | ---: | --- | --- |
| `realcontracts::insert_tail_safety_u64_tail1_to4_backing5` | 38.1495 | `03d45e6a-0553-414e-83ea-6f6c9ce87778` | u64 inner-loop contract, symbolic tail and suffix frame |
| `network::unstable_freeze_noncopy_bytes86_fallback_n2` | 8.783918 | `6bc006d2-eff0-406e-92a5-06c934e5e97f` | non-Copy real dispatch, both insertion loops and whole-value assertions |
| `realcontracts::unstable_network_safety_u8_n9_stubbed` | 8.316227 | `03d45e6a-0553-414e-83ea-6f6c9ce87778` | u8 network with verified swaps, real outer loop at offset=len |
| `assembly::safety_stable_unit_n16` | ubuntu 4.687 / macOS 3.657 | Actions organizer v7 `d1283ff22a`, coordinator-reported | ZST stable no-extension boundary |
| `assembly::safety_stable_unit_n32` | ubuntu 35.126 / macOS 25.670 | Actions organizer v7 `d1283ff22a`, coordinator-reported | ZST stable scratch insertion, reachable inner loop |

The u8 network N9 reaches the annotated outer loop with offset=len (empty suffix), so it
checks invariant establishment/exit on another T/F; it does not exercise an inner step.
The first two regressions do exercise the annotated helper bodies. The first three historical
times are from before these loop attributes, on the same Kani pin and standard4/jobs1.
They are not fresh baseline executions and do not isolate hardware noise.
The ZST times were supplied by the coordinator from full organizer Actions CI v7
(`d1283ff22a`, Kani `cd355b0b`). They are not GCB standard4 timings. Comparisons across
platform and revision are approximate; no matched-run ratio is implied. No historical
K-1 rows or Actions run IDs are available for these two roots. The record in
`actions-v7-timing-source.json` is source-reported, not independently verified; Actions was
not accessed and old per-root status/checks/covers were not supplied. Body-level and broader suite regression outcomes remain unmeasured.
All five roots are members of the saved ordinary v8b inventory and their files are unchanged.
G1 is a representative regression sample, not a full ordinary/whole-stdlib regression claim.

Coordinator correction adds `assembly::safety_stable_unit_n16` and
`assembly::safety_stable_unit_n32` to the same G1. The complete static case analysis is in
`ZST-REACHABILITY.md`: N16 skips scratch-prefix extension, while N32 reaches `insert_tail`
and may enter its real loop with equal ZST pointers. Both use `zst_aware_less::<()>`.
The inner invariant now short-circuits on zero size. This preserves the non-ZST conjunction
and every runtime statement; no new PFC domain or dynamic success is inferred.
