# M2-B/R2 size and use map

PREPARED/AWAITING_CI. Source identities, exact lines and SHA256 are in INPUTS.json. No actual GOTO/symtab/SSA projection was supplied. New proof credit 0. This stage does not reopen R01–R04 or historical results.

## Available observations and their limits

| Assurance | Object / stage | Available fact | Missing discriminator |
| --- | --- | --- | --- |
| Coordinator-reported, TASK-M2BR2 | E/A2R b207847932, run43249040713 | GOTO 239KB, properties160, eloc239; symex0.32s, steps11348, VCC699→186; RSS>6.48GiB at9.6s, killed | Exact artifact/stage/hash, KB convention, per-case attribution, PID/tree/raw units, last milestone, conversion/CNF/SAT entry |
| Coordinator-reported background only | A3R a0a2386001, run43249047207 | GOTO338KB, properties276, eloc331; symex0.36s, steps14420, VCC948→192; RSS>6.43GiB at7.6s, killed | Same missing fields; no new inventory/execution requested for this pin |
| Coordinator-reported | U run43244395728 | 46s/1.4GB, store_argument frame and unreachable load_argument, Unsupported | Comparable retained paths, exact frame object/range and phase attribution |
| Connected metadata, ARTIFACT-ACCESS.json | U and E existing run artifact list | First-page `artifacts: []` | No curated file ID/hash/projection was returned; this does not prove artifacts or instrumentation absent |

P2≈P1 is coordinator-reported only; no exact P1/P2 split is inferred. Both heavy pins are reported past symex/postprocess. A3 is not necessary to reproduce the reported cutoff; an additional A3 effect remains possible. Conversion/bit-blasting is a working localization from the coordinator receipt, not an independently established phase entry. CNF counts and SAT start are UNKNOWN. Low VCC/property/GOTO counts do not bound expression width or intermediate operation cost. Upstream early failure is not speed evidence for equivalent verification.

## Source-only inventory, separate from emitted layout

| Pin / object | Source fields or shape | Derived expression, excluding padding | Actual ABI/backend bytes, bits, offsets, alignment |
| --- | --- | --- | --- |
| U MEM_INIT_STATE, mem_init.rs:19,37 | 2 usize + 1 bool | 2W+B field bits | UNKNOWN |
| U ARGUMENT_BUFFER, :22,365 | Option<ArgumentBuffer>; payload selected_argument:usize, saved_address:*const (), layout_size:usize | Payload 2W+P field bits; Option total UNKNOWN | UNKNOWN, including discriminant/niche/payload placement |
| R1/A1/E MEM_INIT_STATE, :19,34 | 6 usize + 2 bool; field names in INPUTS.json | 6W+2B field bits | UNKNOWN |
| A3 background, task source count | 11 usize + 4 bool | 11W+4B field bits | UNKNOWN; no additional inventory pin |
| Layout<N>, U:34; R1/A1/E:31 | [bool;N], separate from private static | N×B storage bits only after actual N and storage-bool representation binding | Actual N/T/instance/callsite UNKNOWN |

W=actual usize width, P=actual pointer width, B=actual storage-bool width; none is supplied as a measured value here. These formulas are field sums, not sizeof or Boolean encoding widths. Rust field order, padding and Option layout cannot be inferred as C layout. `usize::MAX` is an argument-selection sentinel, not an array extent. Source scalar shapes refute the claim that the declared private state directly contains a huge array; they do not reject an actual backend backing view or costly generated operation without measurement.

`check_uninit/mod.rs::resolve_mem_init_fn` supplies a const from layout_size and an associated T; per-pin exact lines/hashes are recorded. `Layout<N>` needs the emitted generic N plus the originating PointeeInfo layout computation, associated T and callsite, not an assumption that every wrapper uses the input's `MaybeUninit<u8>`. Captures, return temporaries, masks and generated helpers may use other types. Dynamic extents require the actual expression, dependencies/range and overflow semantics.

## Exact missing projections

For U/R1/A1/E only, request Q0–Q4 in QUERY-RECIPE.md through the existing curated interface. Q0 binds file/stage/schema/source/input/tool identities; Q1 resolves the marker-selected static and U's separate buffer; Q2 returns top20 declared fixed types/objects and reachable layouts/captures/views before and after DFCC; Q3 returns actual private write uses; Q4 requests top20 widest retained expressions at Boolean conversion only if existing reporting supports it. Pre-DFCC, post-DFCC and post-symex are separate artifacts, never interchangeable. Every current actual-size/top20 row is UNKNOWN; no ranking is fabricated from source field counts.

## Ranked suspects and discriminators

1. Newly retained MU transfer/PFC paths across U→R1: compare reached store/load/ensures and frame handling alongside early-Part1 inventory. U may stop before the path retained by Part1; this explains non-comparability, not hunk causality.
2. Layout/capture/mask specialization or symbolic index/array update/equality expansion: actual N/T/owner plus retained operator operand/result widths and multiplicities distinguish a wide aggregate from many small operations. Large declared types without retained use do not establish cause.
3. Whole-private-object DFCC assigns/havoc/snapshot or generated write-set/memory views: bind symbol→target extent→helper→retained operation. If measured static and related types are small, reject the huge-static-size hypothesis in that measured scope and inspect object-whole views, pointer operations and intermediate expansion.
4. Arithmetic/conversion cost with modest types: compare operation kinds/counts, bit widths, slicing retention and exact conversion milestones. A1 typed masks/ZST guard versus E's later relevance/raw_eq changes are onset intervals only until actual outcomes exist.

No causal repair, source ablation, release readiness, semantic PASS or new proof credit is established. Seed/Part1 release and resource/frame gates remain OPEN; M3 HELD.
