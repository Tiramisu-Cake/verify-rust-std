# Challenge 8 closure map — internal, PLAN ONLY

Snapshot: 2026-11-19, input g0 `8896f60ae9`. No criterion is newly admitted by
this map. Existing decisions retain their exact source/tool/request/invocation
and domain boundaries. File hashes and decision identities are in SOURCES.json.

## Official contract and evidence levels

The [official challenge at upstream base 25b2b24c82](https://github.com/model-checking/verify-rust-std/blob/25b2b24c82a960734a2bab082784747b9b785177/doc/src/challenges/0008-smallsort.md)
requires absence of UB for seven named functions and sorting contracts for the
three trait entries, **for all possible slices with arbitrary valid length**.
All source SAFETY obligations and all four listed UB classes apply.
The [general rules](https://github.com/model-checking/verify-rust-std/blob/25b2b24c82a960734a2bab082784747b9b785177/doc/src/general-rules.md#solution-requirements)
also require an automated solution passing PR checks with integrated accepted
tools and unchanged std runtime logic.

Our working threshold-domain interpretation is len≤16 for fallback and len≤32
for general/network, subject to the selected implementation's actual threshold
and scratch preconditions. Caller entailment and completeness of that reduction
must be established; the wording above is not replaced by our finite harness
limits. `insertion_sort_shift_left` has its own arbitrary-valid-length/offset
obligation. Primitive/default-order and representative-type strategies are
working scope choices, not proof of generic T/F or a new committee ruling.
Prior plans' discussion of possible exceptions is not an accepted UB waiver.

Evidence vocabulary used below:

- **Published proposal (P):** #752 metadata describes bounded evidence on
  `872d5a43380752786415bc00d2a12ce0e930cb37`, Kani
  `cd355b0bccd32300713bc2ce4f765dafa1510607`. These are source-reported PR
  claims; this task performs no evidence re-admission or broad PR audit.
- **Admitted bounded source-reported (A):** coordinator decisions following
  independent review under S1/Profiles-v4. Exact finite instances only;
  independent compiler/AST/MIR/B1/B2/general theorem credit remains NONE.
- **Observation/diagnostic (D):** native SUCCESS, cost probe, partial-init row,
  assumed-summary consumer, source analysis or review alone grants no admission.
- **OPEN:** the required closure evidence is absent at the stated scope. A
  complete inventory or archive integrity does not establish missing semantics.

## Accepted evidence register

All relative links below refer to committed reports, not raw logs or archives.
Different source revisions are deliberately kept separate.

| ID | Existing decision and source | Exact accepted contribution | Boundary |
| --- | --- | --- | --- |
| A1 | [S1 composite admission](../../../CH8-DISPATCH-LEDGER.md#s1-admission--2026-11-17); candidate `3c40a15d37890c8b5ef7ba49308e81279a494b05`, review `c4e619d9668eeea860bda1de1790665357a6e399`; std `99e8456d200fff1299ee5756279cddb23921dc65`, stock Kani `0aac16ef62da9e9d5645782d458593e5d78143ba` | 35/35 composite rows from runs 44095954742/44128268928; six selected implementation bodies, S1 smoke N0..3, 22 source-reported PFC chains, 127 required roles/bindings, 8 negatives | Mechanism/activation gate; finite T/F/fixtures. Not full threshold proof, single successful workflow, uniform600 or reusable provider graph. The linked candidate's historical PENDING text is superseded only by the coordinator admission. |
| A2 | [S3-1-r2 admission](../../ch8-s3/admission-r2-qualified/ACCEPTANCE.md); std `513341f41ce53833a279571401c924bdddddb6c8`, run 44416629057/1 | Four actual-body u8/KeyLess PFC cases: swap V34/base0..20/indices0..12; sort4 separate6/active1..5; sort4 same backing48/disjoint four-element ranges0..44; merge8 separate10/active1..9/sorted4+4. Three qualified intended negatives | Exact geometries; sort13 negative is a fixed weak-seam caller copy, not actual sort13 positive. Incomplete insert_tail and same-allocation merge rows remain unqualified. |
| A3 | [S3-2-r1 admission](../../ch8-s3/admission-s3-2-r1-exact-location/ADMISSION.md); run 44439462279/1, std `1b4a904f81` (exact pinned report identities) | One actual merge8 case `m8_s32_d00_allinit`: MU48 backing, source[32,40), destination[0,8), known initialized values[8,48), sorted4+4, full u8 | Functional/known-value-frame case; destination is in the initially uninitialized complement. No checked byte-state/dstinit theorem. Two partial rows stay diagnostic; metadata admission of three records is not three qualified leaves. |
| A4 | [Bridge-1-r1 admission](../../ch8-s3-s4/admission-bridge-1-r1/ADMISSION.md); run 44460583125/1, std `f1bdf11902252ad1178f42403c253ae710fecbaf` | `i_p01_b01_fullu8`: actual insert_tail PFC, initialized V34/base1/relative-tail1/span2. `sort9_v34_b01_len09_real`: actual 25-swap sort9, same V34/base1/u8/KeyLess, full frame | One of16 I-D1 geometries and one of256 old begin/tail pairs. Sort9 is one caller/body case. Capped fallback/network families remain UNKNOWN; no caller/provider lifting. |
| A5 | [S4P1-r1 admission](../admission-s4p1-r1-fallback/ADMISSION.md); run 44481580554/1, std `985062ebad` (exact pinned report identities) | Two Original Cell fallback full-logical-u8 cases, initialized V34/base1, N0..2 and N3..4; finite union N0..4 | Exact Cell/F/context only. No Cell provider, trait/general/caller/ownership/init theorem. Missing-location exception is original-run/record-only. |
| A6 | [S4P2-r2 admission](../admission-s4p2-r2-network/ADMISSION.md), commit `8896f60ae9`; run 44548842328/1, std `8faf8e62af8f82b5c46af020086f8df591b6757e`, stock `0aac16ef62da9e9d5645782d458593e5d78143ba` | Four Original/null `small_sort_network<u8,KeyLess<u8>>` cases N2/N3/N4/N0..1, initialized V34/base1, all34 independent full-u8 values, sortedness/full-count/outside-frame/canary; finite union N0..4 | No positive summary/stub edges. All coordinates positive. Model/builtin records individually retained; builtin lowering identity UNKNOWN. N≤4 takes insertion/early-return paths, not sort9/sort13/merge. |
| U1 | [Accepted SEL1-C2 replay](../../sel1-c2/replay/run-43751703000/RESULT.md), run43751703000; Kani `14bc57fdb99960240c4944845a3d985c8af4dcf7`, std `70ba5befc6` plus exact test-only package; [Gate A](../../sel1-c2/gatea/run-43744142824/ACCEPTANCE.md) | Uninit-ON six-row bounded helper replay: merge raw/profile closures, sort4, swap and raw-legal SUCCESS; raw-negative has the intended uninitialized-u64-read failure | Separate source/tool/profile, object-bits12, valid-value OFF. No whole-module, all-T/N, fn-pointer, validity or immutable-write credit. Three-platform tool regression Gate A is not itself a new proof. |

The ledger link above is read-only provenance. Existing accounting and historical
decisions are not changed or recomputed here. A1–A6 are not one combined theorem;
row totals include controls in some decisions and must not be summed into a
count of universal proof obligations. U1 is a separate accepted uninit-track
result; it is not combined with A1–A6 into an instrumented sorting theorem.

## Three entry criteria and the general route

The six implementation bodies below refine the three official entry names;
they are our completeness decomposition, not six additional official criteria.
Every row remains **OPEN for official full closure**, both safety and contracts.

| Official entry / selected implementation | Accepted evidence | Remaining closure evidence |
| --- | --- | --- |
| StableSmallSortTypeImpl: default | A1 selected Cell smoke; A5 strengthens the direct fallback helper at N0..4 only | Actual-entry sorting PFC and safety across fallback0..16; helper→entry and quicksort caller preconditions; allowed callback effects and initialization. A5 is not an entry proof. |
| StableSmallSortTypeImpl: Freeze override | A1 u8 smoke; P describes older general/stable u8/u64 N0..9 body oracles and N2 wrapper contract | Direct actual-impl contract over general0..32, sufficient/disjoint scratch, initialized prefixes and CopyOnDrop/copy-back. Scratch variants need their own binding. |
| UnstableSmallSortTypeImpl: default | A1 Cell smoke; direct fallback A5 | Same fallback gap, with actual selected implementation and comparator/model activation. |
| UnstableSmallSortTypeImpl: Freeze forwarding | A1 u8 smoke | Proved forwarding relation to the selected UnstableSmallSortFreezeTypeImpl instance with identical T/F/domain/post/frame and actual caller entailment, across threshold. |
| UnstableSmallSortFreezeTypeImpl: default Freeze !Copy | A1 non-Copy byte-wrapper smoke | General route through32 where stack geometry permits; large-T fallback branch through16; type/size/Freeze partition completeness. U8 Copy network proofs cannot supply this row. |
| UnstableSmallSortFreezeTypeImpl: Copy override | A1 u8 smoke; A6 direct network N0..4; A4 actual sort9 fixture | Actual-entry contract through network32, alternate general/fallback branches selected by type/size; sort13, tails, merge/copy-back, type/geometry lifting and caller links. |

For `small_sort_general` / `small_sort_general_with_scratch`, the source chain is
sort8/sort4 or one-element seed → copy/insert_tail extensions → initialized
scratch halves → bidirectional_merge → copy-back/CopyOnDrop. A2/A3/A4 support
particular nodes; no admitted full general N16/N32 composition exists here.
The general32 S2 pair was NOT_SELECTED; assumed consumers and timed-out probes
do not supply that missing theorem. All34 sort8 initialization/caller contexts
remain OPEN under A3.

Preserve the planned length classes: general0..1/2..7/8..15/16..32;
network0..1/2..8/9..12/13..17/18..24/25/26..32; fallback0..16.
Each class must cover every claimed length and actual source branch, not merely
one boundary witness. Geometry, types, ZST, scratch lengths and odd merge tails
are additional axes. The isolated accepted sort9 N9 case does not fill N5..8 or
N10..32 of the network caller.

## Four named helpers, supporting callees and caller contracts

| Target / dependency | Evidence now | Closure condition |
| --- | --- | --- |
| Official `swap_if_less` | A2 bounded actual PFC; P has older safety contracts/consumers on its own pin | Prove safety for legal positions/equality/allocation/T/F; functional swap and full frame for the exact semantic provider needed by sort9/13. Requalify callee and consumer together; safety-only modifies is not a sorting summary. |
| Official `insertion_sort_shift_left` | P direct bounded bodies/offsets; A5/A6 execute short instances in real callers; A4 insert_tail is one supporting case | Every valid length/offset, initialized prefix/hole/repair invariant, base/step/exit and actual loop binding. Functional prefix/order/count for consumers, not only pointer geometry. Unwind caps do not prove arbitrary length. |
| Official `sort4_stable` | A2 actual separate/same-allocation cases, full-value/frame roles | All claimed source/destination ranges and initialization, non-overlap, callback effects and promised order/count/frame; connect actual sort8 call geometries. |
| Official `has_efficient_in_place_swap` | P describes predicate checks on12 types; static source dispatch is available | Check predicate/size classes and the selected entry route at the integrated pin; no new A-level requalification supplied here. Predicate success is not swap safety. |
| `insert_tail` | A4 single actual PFC geometry | Fill required geometry/offset/length domains, mutable-hole ownership, initializedness and restoration; lift only after entailment checks. |
| `bidirectional_merge` | A2 separate merge8; A3 one original MU48 geometry | Sorted halves, full count, odd lengths, all required source/destination geometries, init/frame, ord-violation reasoning. Merge32 and generic merge are not supplied by merge8. |
| sort8 / sort9 / sort13 and wrappers | A4 actual sort9; A1 wrapper/trait activation; fixed sort13 weak negative | Actual positive sort13 and all required helper call contexts; correct comparator/model and full values. Faithful negative caller copies detect faults but are not positive callee proofs. |
| Quicksort→entry and helper→caller composition | A1 narrow source-reported PFC/relations; P has four old bounded stub_verified consumers | Derive each callee requires from the caller invariant at the same source/T/F/geometry; carry modifies/normal/abort/unwind semantics and substantive ensures. No new caller or provider credit follows from A2–A6 admission. |

A reusable summary additionally needs actual callee proof on a domain covering
every use, exact Check/Original/Replace registration, contract/producer binding,
compatible flags and source identities, nonvacuous model activation, complete
properties/roles/covers/controls, and independent review plus admission of the
specific composition. A bounded PFC requires is assumed at entry; that does not
show a different caller satisfies it. Repeated assumed summaries cannot form a
self-justifying proof cycle.

## UB classes and other safety obligations

| Required class | Current evidence boundary | Evidence needed before claiming closure |
| --- | --- | --- |
| Dangling/misaligned loads or stores; source bounds/overlap/provenance | P default pointer checks; A rows retain complete exported safety records only at their exact domains | Actual paths and legal allocation/offset classes, source SAFETY entailment, callback/copy/alias constraints and all permitted lengths. No unexported/lowered safety is inferred. |
| Reads from uninitialized memory | S sorting lane is stock OFF; A3 partial-MU rows explicitly diagnostic. U1 supplies accepted bounded uninit-ON helper evidence on another tool/source, valid-value OFF | Checked byte initialization/store/move/copy state, scratch and destination initialization, negative holes/moved-from/repair controls, actual routes on a compatible qualified pin. `is_initialized` when instrumentation is OFF and manual ShadowMem updates are not this proof. |
| Producing invalid values | No validity qualification imported by A1–A6; #752 explicitly retains the gap | Actual typed-read/production/copy/layout validity evidence and restrictive-value controls (e.g. bool/char/enum/reference cases as applicable), with exact supported/refused domains. Full-u8 covers only u8 values; initialized bytes alone do not establish generic Rust validity. |
| Mutating immutable bytes | No permission/temporal alias theorem imported; outside-value-frame checks are bounded observations | Automatically checked immutability/write permission and callback/borrow effects on actual routes, with meaningful immutable-write negatives, or an explicit applicable committee scope decision. Initialization seeding, modifies sets, disjoint ranges and unchanged canary values do not establish absence of all forbidden writes. |
| All source SAFETY, ownership, panic/Drop, abort and layout obligations | A admissions explicitly leave ownership/panic/Drop/general lifting OPEN; P discloses panic stubs and no unwind recovery proof | Preserve normal/abort/unwind distinctions and prove applicable guards/restoration/Drop behavior, or disclose a specifically accepted scope restriction. Lawful-order sorting premises cannot silently narrow arbitrary-answer safety. |

Future reports must keep invalid-value and immutable-write gaps as separate
rows even after an uninit lane succeeds. Neither source-definedness U arguments
nor SUCCESS unsupported guards establish a general compiler/emitter/MIR theorem.
Original U/guards/failures remain visible, with exact run-local metadata exceptions.

## Closure decision

There is useful admitted bounded progress, but no basis here to mark Challenge 8
complete, a general route complete, all four UB classes complete, or #752 updated.
Threshold scope/type sufficiency and any UB exceptions need an applicable accepted
ruling or the missing proof. The next plan is [UPDATE-752-PLAN.md](UPDATE-752-PLAN.md);
none of its future execution gates is authorized by this documentation stage.
