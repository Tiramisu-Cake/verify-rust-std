# HANDOFF — independent review of S4P2-r2 run 44548842328

**APPROVE each of N01, N2, N3 and N4 as an exact bounded SOURCE_REPORTED S1 candidate. Zero blocking findings; zero required changes.** This is a review recommendation for a separate coordinator decision. No admission, qualification receipt, ledger entry or proof credit is created by this review.

Reviewed intake through **7c66fb85b99f77801ff10e99ccc5d37761ba5442**, including original intake **5c52edd71ad20f3f5b89257ed54836b2f43e14c0** and its planner addendum. All 41 manifest entries and the manifest itself match that pinned commit. The independently written `review.py` reads compact evidence and Git objects directly, imports no intake modules, and records exact per-instance reviewer arguments in `REVIEW.json`.

## Exact cases and findings

All four cases use initialized V34/base1, all 34 independent full-domain u8 values, `KeyLess<u8>`, Original/Proof registration, target null, no positive stubs, verified stubs, providers or summary edges. Domain and source bindings are the exact frozen ones. The finite union is N0..4 only in this context; this review does not extend the historical S1 smoke domain or establish a general network theorem.

| Case / exact root | Invocation | Checks: SUCCESS / U | Required SUCCESS roles | SAT covers | Exported unwind records | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| N01 `s4p2r2_network_b01_n00_01_fullbyte` | `a44909f40bf7474e9b929518edfb8ca6` | 211 / 16 | 4 / 4 | 3 / 3 | 1 SUCCESS | **APPROVE** |
| N2 `s4p2r2_network_b01_n02_fullbyte` | `f4551429b6d5452fb500872840a34c8c` | 241 / 11 | 4 / 4 | 6 / 6 | 0 | **APPROVE** |
| N3 `s4p2r2_network_b01_n03_fullbyte` | `34ce7f6cd3004e1abddb5e861885fc00` | 241 / 11 | 4 / 4 | 6 / 6 | 0 | **APPROVE** |
| N4 `s4p2r2_network_b01_n04_fullbyte` | `667365b8fc9e4f7dbf84f0d17119673d` | 241 / 11 | 4 / 4 | 6 / 6 | 0 | **APPROVE** |

**N01 finding:** both literal calls `[1..1]` and `[1..2]` return at helper340–341. Its extra U sites at network350 and model97/100 have excluded source paths. Distinct `S4P2R2_N_00_01_N00` and `..._N01` SAT covers at harness114/115 follow all four roles; both lengths have continuing witnesses. `active_post::<u8>.unwind.0` at model96 is SUCCESS. No mandatory role is U.

**N2 finding:** literal `[1..3]` gives len2, no_merge=true, initial region len2 and presorted_len1. The first insertion-sort call is followed by return372–373. All four merge U properties and network381 are excluded before any merge invocation. All six declared covers, including unsorted, duplicate, nonconstant, descending and useful-return witnesses, are SAT after the four roles.

**N3 finding:** the same source reasoning is instantiated at the actual literal `[1..4]`, len3, initial region len3, presorted_len1 and immutable no_merge=true. Its own invocation/export supplies all four SUCCESS roles and six SAT covers; the N2 outcome is not substituted for its evidence.

**N4 finding:** the actual literal `[1..5]`, len4, still takes presorted_len1 and no_merge return before381/389. Its own four roles and six covers pass. This examines the small-length path of `small_sort_network`, which uses insertion sort here; it establishes no sort9/sort13, merge, threshold16/32 or larger-length claim.

## U arguments checked against actual source

I checked all **67** exact U dictionaries against the authenticated compact member, invocation/namespace and pinned source commit/file SHA256/line. `REVIEW.json` contains every exact property ID and full dictionary plus an independently stated domain argument. There are **43 source-path exclusions** and **24 generated arithmetic failure-edge exclusions**. All 49 positive U instances and 18 fixed-negative U instances are accounted for, without duplicates or additional records.

The 16 `bidirectional_merge::<u8, ...KeyLess<u8>>.assertion.1` through `.4` instances at smallsort974/990/991/992 are bound to the actual helper branch, not to their status: helper340–341 excludes N0/N1; for N2/N3/N4, helper351 sets no_merge,354 selects the whole slice,360–368 select presorted_len1,370 calls insertion sort and372–373 returns on the first iteration. If that call does not return normally, it also cannot continue to381 or389. Thus the second-region operation381 and merge call389 cannot execute. The callee's `intrinsics::assume` is not a proof premise.

The remaining positive source-path exclusions are network350 for N01 and model97/100 for N01's order loop, which starts at i1 with L<=1. Negative-path arguments are also concrete: order-corrupt `[2,1]` and unchanged descending weak-seam len13 return at model98; count-corrupt32 has first-query counts32/31; logical Cell `[0,1] -> [0,0]` has first-query counts1/2, returning at116 before118. The weak negative is a fixed fixture with an empty comparator seam, not an actual arbitrary-byte sort13 failure.

Each positive separately retains six exact arithmetic U arguments: usize abs_diff3222/3224 follows its unsigned ordering branch; is_multiple_of3916 excludes the zero-divisor arm; allocation-size148 divides only for size!=0; alignment1479 follows the nonzero power-of-two check; fmt820 shifts by literal1 below usize width64. These establish the specified generated **error edge** is impossible. They do not explain why the native check instruction itself was classified UNREACHABLE. That compiler/emitter cause remains UNKNOWN. This distinction is explicit in the intake and is consistent with the approved S1 source-local definedness method and prior reviews. No U is relabelled SUCCESS; no blanket helper/std exception is used.

## Non-vacuity, safety and location records

For every positive, the four exact labelled assertions ACTIVE_CONCRETE_MODEL, SORTED_FULL_VALUE_COUNT, FULL_OUTSIDE_FRAME and ARBITRARY_OUTSIDE_CANARY are SUCCESS at their frozen source sites. The harness source has a nonempty34-iteration frame loop. All declared covers occur after the helper and all four roles in the same harness. Their SAT paths supply non-vacuity, including both N01 lengths. They are not used to justify U sites. Inventories are complete at258/258/258/230 properties in execution order, with252/252/252/227 non-cover checks. N2/N3/N4 export zero residual unwind assertions; this is recorded as zero rather than an invented check. Unwind36 and the unchanged argv/check configuration are retained; no unexported safety or larger-domain unwind claim is inferred.

All **13 non-std location records** were checked as exact per-invocation tuples with complete property dictionaries, members, namespaces and identities. Five are `ToISize::to_isize.unreachable.1`, class unreachable/status SUCCESS, stock-tool models203: NEG-Cell and each positive. Pinned stock source has the separate failed-conversion safety check before unreachable; each invocation retains its SUCCESS `to_isize.safety_check.1` with description `Offset value overflows isize`. The model coordinate is not misrepresented as a physical std implementation. Eight are `memcpy.pointer.1/.2`, class pointer/status SUCCESS, builtin pseudo-lines33/34 in the four positives. Actual backend builtin source/lowering identity remains UNKNOWN. Protected CBMC identity binds the producer observation, not an independently established source trace.

All1,143 records have positive coordinates, and the frozen rich reader accepts all eight inventories. There is no present-null/missing-location case in this run. No earlier location exception is transferred, no coordinate is replaced, and no general parser/std/builtin waiver is proposed. The13 SUCCESS unsupported guards are separately retained: one in NEG-Cell and three per positive. Frozen stock producer semantics emit a failing assertion plus assume for an unsupported operation; these SUCCESS guards report no reachable violation in the bounded invocation. They grant no general support or panic/unwind theorem, and the producer's strict empty-array rejection is preserved.

## Policy and precedent

Applied `S1-ACCEPTANCE-DECISION-2026-11-17.md`: exact per-site arithmetic/bounds arguments with pinned premises, located/non-U required roles, full inventories and source-reported registration/context. Independent compiler/AST/MIR proof is neither claimed nor silently added as an S1 gate.

Compared S3-1-r2 `admission-r2-qualified/ACCEPTANCE.md`, its `admission-r2-location/ADMISSION.md`, the corrected independent reporting review, and S4P1 `admission-s4p1-r1-fallback/ADMISSION.md`/JSON plus its independent review. They accept individually justified U, retained successful guards, positive roles and SAT covers at exact finite source-reported boundaries. Their successful-system missing-location exceptions are tied to specific old runs and tuples. They supply the review discipline, not an exemption for this run. The new stock-model/builtin tuples are reviewed here individually; no rule for future runs or unknown records follows.

## Identities, validation and preserved limits

Run44548842328/attempt1; trigger `d88fac48cf50a742f9f00026ba66e5e4353e1019`; std `8faf8e62af8f82b5c46af020086f8df591b6757e`; stock tool `0aac16ef62da9e9d5645782d458593e5d78143ba`. Request SHA256 `fd2b608a5538779f5f0345a49e5c147646d82dc6d066fdd1e3b50d0e6bc69e39`; workflow SHA256 `d5dd5942297df013e625b85890fcc3884ec6b60d1f08c8e1dc51c019ce15fdfc`. Compact gzip SHA256 `f94969b3cf6c641a94dd8766f09de609777a1eaa97c282fd1cd03f7219032285`; decompressed structured payload SHA256 `65f5b72308391a71a19fad281ee5617ba1365c37ffc189accc19a819276fa81e`. All119 structured member hashes/byte counts match. No artifact reacquisition was performed.

Independent review: **1,019 checks PASS**. Frozen reference replay: **976 checks PASS**; supplemental audit: **2,612 checks PASS plus10 adverse checks**; addendum: **192 checks PASS**; original seal: **41 files PASS**. Reference generators used a compare-only replacement for their JSON writer; regenerated projections matched committed bytes. Audit/addendum ran in separate Python interpreters. `VALIDATION.json` records the initial shared-interpreter driver failure and its clean-process resolution. Original intake files remain unchanged. These are offline reader/source/reporting checks, not fresh native verification.

The full original partition remains **1,051 SUCCESS +4 intended FAILURE +67 UNREACHABLE +21 SAT =1,143 properties**. Workflow FAILURE, SELECTED_PARTIAL, strict0/8, ZERO_U/REJECT_ALL, disabled proposal and every `s3_expected_match=False` remain historical facts. No output receipt or original rejection is rewritten.

Cost claims are honest: campaign359.3813398520001s is distinct from native verification and whole-child elapsed; N2/N3/N4/N01 native verification is3.061223584/3.846284711/4.692468986/33.427759135s. Old600s results are censored whole-child timeouts with incomplete exports; their verification costs remain UNKNOWN_CENSORED and no exact speedup factor is justified. Sampled RSS and initial-export compile markers preserve their stated limits; no solver-phase or causal compiler/MIR attribution follows.

**HANDOFF; requested one-stage review complete.** Coordinator may separately assess these four exact candidates. Admission, newly qualified leaves, newly credited proof obligations and independent B1/B2 credit from this review are **false /0 /0 /NONE**. Generic/provider/summary/caller/initmask/ownership/panic/Drop/fullN16/N32 and independent compiler/emitter/MIR obligations remain open. Only this review directory is changed; no `acquire.py`, compiler/Kani/CBMC/full runner, CI, push, ledger/accounting, admission or external messaging action. Local commit uses `[skip ci]` and Tiramisu-Cake <igkharin@gmail.com>; its SHA is returned separately.
