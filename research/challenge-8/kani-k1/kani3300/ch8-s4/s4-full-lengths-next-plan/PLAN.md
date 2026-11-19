# Exact next S4 package

Prepare **S4P3: network N8, N9, N13, N17** in a later authorized implementation
stage. Use four distinct literal calls to the actual `small_sort_network`, with
the same full-value oracle and V34/base1 fixture as admitted network-r2. All
roots here are **PROPOSED_NOT_IMPLEMENTED_NOT_REGISTERED_NOT_RUN**. This packet
does not authorize implementation or launch.

Source is `8faf8e62af8f82b5c46af020086f8df591b6757e`; admission checkpoint is
`8896f60ae9e0ea1c706c6b8693d00e2500190676`. Read
[COVERAGE.md](COVERAGE.md) for every length and [BRIDGES.md](BRIDGES.md) for
the remaining caller/type/allocation obligations. [NEXT-PACKAGE.json](NEXT-PACKAGE.json)
defines selectors, literal calls, assertions, covers and serial order.

| Order | Root | Expected result | Purpose |
| --- | --- | --- | --- |
| 1 | `checker_order_corrupt` | exact `S2_NEG_CHECKER_ORDER` FAILURE | Detect an unsorted result |
| 2 | `checker_count_corrupt` | exact `S2_NEG_CHECKER_COUNT` FAILURE | Detect a sorted non-permutation |
| 3 | `sort13_weak` | exact `S2_NEG_SORT13_WEAK` FAILURE | Retain the weak-network negative |
| 4 | `s4p_cell_count_corrupt` | `S4_NEG_CELL_ACTIVE` SUCCESS; `S4_NEG_CELL_COUNT` FAILURE | Retain Cell model/count sensitivity |
| 5 | `s4p3_network_b01_n08_fullbyte` | candidate SUCCESS | Last insertion-only network length |
| 6 | `s4p3_network_b01_n09_fullbyte` | candidate SUCCESS | Actual sort9 entry; shift offset9 has zero bodies |
| 7 | `s4p3_network_b01_n13_fullbyte` | candidate SUCCESS | Actual sort13 entry; shift offset13 has zero bodies |
| 8 | `s4p3_network_b01_n17_fullbyte` | candidate SUCCESS | Last no-merge length; sort13 plus tails13..16, span through17 |

Proposed module: `verify/sorting_s4_full_lengths_next.rs`; proposed fully
qualified prefix:
`slice::sort::shared::smallsort::verify::sorting_s4_full_lengths_next::`.
These names are reserved only in this plan, not registered selectors. Existing
negative selectors and their source bodies remain exactly as in network-r2.
In a later implementation, expose the proposed module under the same existing
`all(kani, kani_smallsort_sorting, kani_smallsort_s2_assumed,
kani_smallsort_s3_leaf, kani_smallsort_s4_partition)` gate as network-r2;
the current request already supplies those flags. Ordinary inventory stays
isolated. No new cfg flag or compiler setting is needed or authorized here.

For each positive, independently create arbitrary `[u8;34]`, save all34 bytes,
and snapshot the active range with the existing concrete model. The actual
calls are respectively `small_sort_network(&mut v[1..9], ...)`, `[1..10]`,
`[1..14]`, `[1..18]`, with stateless `KeyLess::<u8>::new()`. Use literal bounds
at the call site, not a nondeterministic length interval or a symbolic shared
runtime helper. All34 values stay independently arbitrary in0..255; initialized
storage, base1, Original/null, no summary edges, no verified/assumed stubs.
The fixed logical `n` is used only to express the oracle/frame/covers.

Each positive retains four separately named SUCCESS assertion roles:
`ACTIVE_CONCRETE_MODEL`, `SORTED_FULL_VALUE_COUNT`, `FULL_OUTSIDE_FRAME`,
`ARBITRARY_OUTSIDE_CANARY`, prefixed `S4P3_N_08_`, `_09_`, `_13_`, `_17_`.
Active guard checks all three existing u8 model/span/pair predicates. The post
is the existing owned snapshot plus sortedness/full logical multiplicity. The
frame examines every index0..33; a separately nondeterministic outside index
must also preserve its byte. No input-order or distinctness assumption is added.

Six individually named SAT covers per positive,24 total:

- `N08`/`N09`/`N13`/`N17`: exact selected length.
- `UNSORTED`: `bytes[1] > bytes[n]`.
- `DUPLICATE`: `bytes[1] == bytes[n]`.
- `NONCONSTANT`: `v[1] < v[n]` after the call.
- `MAX_DESCENDING`: the existing strict-descending predicate on the complete
  active input slice. This is satisfiable for each N<=17 and exercises worst
  source insertion movement for N8/N17; it is not a lowered branch trace.
- `USEFUL_RETURN`: reachable after the original call and assertions.

Covers are separate existential witnesses, not simultaneous input restrictions.
N9 and N13 test actual sorting sequences, not a copied circuit. N17 also tests
preservation of the suffix until insertion. New U/property/model/builtin records
must be individually bound to the new invocation; neither old case-specific
admissions nor the old merge-unreachable exclusions apply automatically. No
missing-location exception or new general admission rule is requested.

Keep negative root unwind34/34/34/36 and positive unwind36, all current flags,
caps and strict checks; [LOOP-COST.md](LOOP-COST.md) records the exact snapshot.
The eight roots fit the previous static resource envelope:6180s with720s reserve
inside campaign6900s. Actual new native fit remains UNKNOWN. No N32 or merge
root belongs to this first package.

After a separately reviewed implementation, a later execution request must bind
the exact source/tool/control/request identities, all role/cover source locations,
actual resolved argv/unwind, native property inventory and per-row costs. Review,
execution authorization and coordinator admission remain distinct stages.
Do not weaken ZERO_U/REJECT_ALL or turn strict0 into success: any exact
source-reported admission requires its own reviewed decision. Compiler/MIR
origin, unexported safety, initmask/dstinit, ownership/Drop/unwind and independent
B1/B2 credit remain separate.

Next **separate** package: the same four negative controls, then one concrete
`small_sort_fallback<Cell<u8>, KeyLess<Cell<u8>>>` N16 root on initialized V34/base1,
all34 independent full bytes, literal slice `[1..17]`, four roles and six covers
with prefix `S4P4_F_16_`. Construct/set all34 Cells as in S4P1, use `.get()` for
the full frame/canary, and assert only the exact Cell sorting model is enabled:
u8-only span/pair guards are inactive for Cell and must not be asserted as active.
No Copy/Freeze premise or summary transfer is added. Retain unwind36. The
five-root campaign envelope is4020s =5*720s slots +180s controller +240s
cleanup. Separate workflow setup is not charged a second time inside this
campaign formula; see LOOP-COST.md.

Conditional filling order after those boundary packages (each list is literal
roots, with the same four controls preceding each batch):

| Package | Exact positive lengths | Why |
| --- | --- | --- |
| F-gap1 | Cell fallback5,6,7,8 | Connect admitted0..4 to the lower interior |
| F-gap2 | Cell fallback9,10,11,12 | Middle insertion spans |
| F-gap3 | Cell fallback13,14,15 | Complete0..16 only if all previous exact admissions exist |
| N-gap1 | network5,6,7 | Complete insertion-only0..8 |
| N-gap2 | network10,11,12 | sort9 plus each suffix length |
| N-gap3 | network14,15,16 | sort13 plus each suffix below17 |
| N-bridge1 | network18,19,25 | First two-region even/odd merges; mixed9/13 boundary25 |
| N-bridge2 | network24,26 | Last two-sort9 length; first two-sort13 length |
| N-gap4 | network20,21,22,23 | Fill remaining sort9 two-region contexts |
| N-gap5 | network27,28,29,30 | Fill sort13 two-region contexts |
| N-close | network31,32 | Close upper end only after earlier geometry/merge work |

General is a separate route: first literal u8 general helper calls at
0,1,2,3 (return and first even/odd merge), then8,9,16,17 (sort4/sort8 boundaries),
then4,5,6,7;10,11,12,13;14,15;18,19,20,21;22,23,24,25;
26,27,28,29;30,31,32. Each semicolon group is a later package with the four
controls. Repeat the exact33-length map for NonCopyByte with its own active
model and typed fixtures, and separately address the size>16 branch. General
timing is unmeasured here; these are coverage priorities, not reserved attempts.
If an unchanged cap prevents completion, retain UNKNOWN/incomplete and plan a
source-preserving concrete-call refinement or a separately proved bridge in a
later task. No rerun or cap increase follows from this plan.
