# HANDOFF — S4P2-r2 concrete-calls postrun intake

Run **44548842328 / attempt 1** independently reconciles as **completed FAILURE; SELECTED_PARTIAL; all 8 selected roots started, completed and sealed; no global stop**. The four positive native harnesses report SUCCESS and the four fixed negatives report their own intended FAILURE labels. Strict expected matches remain **0/8**. This packet supplies **four bounded SOURCE_REPORTED S1 candidates for independent review**, not an admission decision. Newly qualified leaves, proof obligations credited and independent B1/B2 credit: **0 / 0 / NONE**.

All 1,143 exported properties are retained: **1,051 SUCCESS + 4 FAILURE + 67 UNREACHABLE + 21 SATISFIED covers**. The 67 U instances have individual source-local candidate arguments. No labelled post/frame/relation role is UNREACHABLE. All coordinates have a positive file/line and the frozen rich reader accepts all eight inventories; 13 records use stock Kani model or backend builtin coordinates and receive separate per-instance metadata arguments. Candidate BLOCKER count is **0** under the approved S1 source-reported method. Actual backend builtin source and independent AST/MIR/emitter origin remain UNKNOWN.

## Identities and acquisition

- Trigger head `d88fac48cf50a742f9f00026ba66e5e4353e1019`, tree `628a9aa91c86a2e5f72efee626b58f1715ec3dbf`, sole parent `4059c900e50ba179d824a1e6f6bd7798cf343e36`. Connected commit metadata agrees with the local object. Same-tree sibling of reviewed control `3d3fb715271e3b195c6e0eee3557d5b0a6aad00d`; not its child.
- std `8faf8e62af8f82b5c46af020086f8df591b6757e`, tree `91f097cdb4085d30c4b94afbb843aeb34f1d3287`, parent `c12867b1e651a3927cbd9f169fe2c3d3728a44c3`. Stock tool `0aac16ef62da9e9d5645782d458593e5d78143ba`, tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`.
- GO `fef8170d868c64bfa61e6de5eee3450943354ec7` (`ch8-s4/network-r2-go/`); request SHA256 `fd2b608a5538779f5f0345a49e5c147646d82dc6d066fdd1e3b50d0e6bc69e39`; workflow SHA256 `d5dd5942297df013e625b85890fcc3884ec6b60d1f08c8e1dc51c019ce15fdfc`. Exact 155 control payload hashes and all declared source dependency hashes checked. Workflow `ch8-s2.yml`, branch `uninit-ci/ch8-s4p-2-r2-20261119`, event push; job `s3_leaf` / `135646722748` on ubuntu-24.04.
- Connected artifact `ch8-s3-2-44548842328-1` / `14542371938`: 448143 transport bytes; SHA256 `5faedd4231f8aae73aa47f6020665de24e153944d0f2436893e631c70bca913b` checked **before** opening the bounded transport in memory. No transport ZIP was retained. Only member `group-evidence.json.gz` was extracted: 462944 bytes, SHA256 `f94969b3cf6c641a94dd8766f09de609777a1eaa97c282fd1cd03f7219032285`. Decompressed structured payload: 6223182 bytes, SHA256 `65f5b72308391a71a19fad281ee5617ba1365c37ffc189accc19a819276fa81e`. All 119 structured members matched their own byte counts and SHA256s. These three digest scopes are distinct.
- Connected plugin metadata was read first. The connector only offers a whole-artifact download, so the r1 bounded gh in-memory adapter was used for the sole member; no full/raw logs, saved transport archive or GCS access. One acquisition, no old evidence reacquired. `acquire.py` is retained for audit and must not be invoked on replay. `CONNECTED-METADATA.json`, `RUN-METADATA.json`, `JOBS-METADATA.json`, `HEAD-METADATA.json` and `artifact-integrity.json` preserve the inputs.

## Exact per-root native inventories

Aliases below map to exact roots/selectors in `QUALIFICATION.json` and `ROOTS.json`. `NATIVE-PROPERTIES.json` preserves every exact property dictionary, including all IDs, classes, descriptions, status and native display coordinates; no status is rewritten. Checks exclude covers.

| Alias | Exact root ID | Native | Properties | Checks | SUCCESS | FAILURE | UNREACHABLE | SAT covers | SUCCESS unsupported guards |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| NEG-order | `checker_order_corrupt` | FAILURE | 24 | 24 | 15 | 1 | 8 | 0 | 0 |
| NEG-count | `checker_count_corrupt` | FAILURE | 26 | 26 | 24 | 1 | 1 | 0 | 0 |
| NEG-sort13 | `sort13_weak` | FAILURE | 25 | 25 | 16 | 1 | 8 | 0 | 0 |
| NEG-Cell | `s4p_cell_count_corrupt` | FAILURE | 64 | 64 | 62 | 1 | 1 | 0 | 1 |
| N2 | `s4p2r2_network_b01_n02_fullbyte` | SUCCESS | 258 | 252 | 241 | 0 | 11 | 6 | 3 |
| N3 | `s4p2r2_network_b01_n03_fullbyte` | SUCCESS | 258 | 252 | 241 | 0 | 11 | 6 | 3 |
| N4 | `s4p2r2_network_b01_n04_fullbyte` | SUCCESS | 258 | 252 | 241 | 0 | 11 | 6 | 3 |
| N01 | `s4p2r2_network_b01_n00_01_fullbyte` | SUCCESS | 230 | 227 | 211 | 0 | 16 | 3 | 3 |

Each complete export has unique IDs, exact check/cover partitions, no ERROR/UNKNOWN/UNDETERMINED/other statuses and no UNSAT or unreachable cover. All selected native exports are COMPLETE and all canonical row receipts remain OBSERVED/RECORDED with `s3_expected_match=false`; they are not rewritten to qualified receipts. `SELECTED_PARTIAL` retains the failed strict qualification of selected observations despite complete native inventories; `full_inventory_complete=false` separately preserves broader deferred obligations.

| Alias | Invocation ID | Native original group exit | Resolved unwind |
|---|---|---:|---:|
| NEG-order | `48447dd51b7f486f9d32ed300a7f196d` | 1 | 34 |
| NEG-count | `b20e3cc9816c446db56a9c31d397a7a7` | 1 | 34 |
| NEG-sort13 | `edf7e69ef5fc478091365f8ecb1c2bc7` | 1 | 34 |
| NEG-Cell | `135b20a994dc4c8988cfdcb06d671d6e` | 1 | 36 |
| N2 | `f4551429b6d5452fb500872840a34c8c` | 0 | 36 |
| N3 | `34ce7f6cd3004e1abddb5e861885fc00` | 0 | 36 |
| N4 | `667365b8fc9e4f7dbf84f0d17119673d` | 0 | 36 |
| N01 | `a44909f40bf7474e9b929518edfb8ca6` | 0 | 36 |

All eight are actual Original/Proof registrations in crate core with target null, unique fresh cargo namespaces and exact singleton selectors/argv/cfg. There are no positive stubs, verified stubs or enabled summary edges. NEG-sort13 alone retains the reviewed `s2_swap_seam -> weak_swap` negative stub. NEG-sort13 is the fixed descending 13-element weak-seam fixture, not an arbitrary-byte sort13 theorem. NEG-Cell is the initialized logical checker-only `[0,1] -> [0,0]` fixture, not a Cell network/provider theorem.

The exact intended native failure labels are:

- NEG-order: `slice::sort::shared::smallsort::verify::sorting_s2_batch::checker_order_corrupt.assertion.1` — `S2_NEG_CHECKER_ORDER`, `library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs:140`, FAILURE. No extra failure is present.
- NEG-count: `slice::sort::shared::smallsort::verify::sorting_s2_batch::checker_count_corrupt.assertion.2` — `S2_NEG_CHECKER_COUNT`, `library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs:134`, FAILURE. No extra failure is present.
- NEG-sort13: `slice::sort::shared::smallsort::verify::sorting_s2_batch::sort13_weak.assertion.1` — `S2_NEG_SORT13_WEAK`, `library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs:149`, FAILURE. No extra failure is present.
- NEG-Cell: `slice::sort::shared::smallsort::verify::sorting_s4_partition::s4p_cell_count_corrupt.assertion.4` — `S4_NEG_CELL_COUNT`, `library/core/src/slice/sort/shared/smallsort/verify/sorting_s4_partition.rs:30`, FAILURE. No extra failure is present.

### Positive roles, lengths and covers

All four positive roots use initialized `[u8;34]`, base1 and `KeyLess<u8>`; all 34 bytes are independent in 0..255. N2/N3/N4 call the original network using literal slices `[1..3]`, `[1..4]`, `[1..5]`. N01 uses an independent symbolic bool and both literal original calls `[1..2]` and `[1..1]`, with one shared oracle/role block. The domain is this exact finite geometry and normal-return context.

Each root has all four exact labelled native assertion roles SUCCESS at its frozen source sites: ACTIVE_CONCRETE_MODEL, SORTED_FULL_VALUE_COUNT, FULL_OUTSIDE_FRAME and ARBITRARY_OUTSIDE_CANARY. The corresponding full `S4P2R2_N_*` messages, native IDs and coordinates are in `QUALIFICATION.json`; every match is checked against exact pinned source bytes.

| Alias | Exact SAT cover labels |
|---|---|
| N2 | `S4P2R2_N_02_N02`, `S4P2R2_N_02_UNSORTED`, `S4P2R2_N_02_DUPLICATE`, `S4P2R2_N_02_NONCONSTANT`, `S4P2R2_N_02_MAX_DESCENDING`, `S4P2R2_N_02_USEFUL_RETURN` |
| N3 | `S4P2R2_N_03_N03`, `S4P2R2_N_03_UNSORTED`, `S4P2R2_N_03_DUPLICATE`, `S4P2R2_N_03_NONCONSTANT`, `S4P2R2_N_03_MAX_DESCENDING`, `S4P2R2_N_03_USEFUL_RETURN` |
| N4 | `S4P2R2_N_04_N04`, `S4P2R2_N_04_UNSORTED`, `S4P2R2_N_04_DUPLICATE`, `S4P2R2_N_04_NONCONSTANT`, `S4P2R2_N_04_MAX_DESCENDING`, `S4P2R2_N_04_USEFUL_RETURN` |
| N01 | `S4P2R2_N_00_01_N00`, `S4P2R2_N_00_01_N01`, `S4P2R2_N_00_01_USEFUL_RETURN` |

Thus positive SAT counts are exactly **6/6/6/3** in execution order. Both N01 length witnesses (`..._N00` at source line114 and `..._N01` at115) and USEFUL_RETURN at116 are SAT in the same invocation. Impossible pair/descending witnesses are omitted only as source sites in N01; no exported UNSAT/U cover is waived. Source site counts are not native property counts.

Unwind values are 34/34/34/36/36/36/36/36. The only exported `class=unwind` record is N01 `sorting_model::active_post::<u8>.unwind.0` at sorting_model.rs:96, SUCCESS. N2/N3/N4 export zero such records, not an invented nonempty unwind inventory. Complete native SUCCESS results and unchanged safety/unwind flags are retained; no larger-domain unwind theorem follows.

## Why the strict producer rejected each row

The frozen `s4p2r2_policy.expected_observation` result was replayed unchanged for each exact row/export/rich inventory. It first requires `unsupported_constructs == []`, then every check status in SUCCESS/FAILURE, and later empty `checks.unreachable` plus strict success-count equality. The request retains `REJECT_ALL`, proposal disabled, unknown reject and role-U reject. Intended negative FAILURE labels themselves are the expected behavior.

| Alias | First failing strict predicate | Additional preserved rejection |
|---|---|---|
| NEG-order | 8 UNREACHABLE statuses; required SUCCESS/FAILURE only | 8 U records also violate empty `checks.unreachable` and all-success-or-intended-failure count rule |
| NEG-count | 1 UNREACHABLE statuses; required SUCCESS/FAILURE only | 1 U records also violate empty `checks.unreachable` and all-success-or-intended-failure count rule |
| NEG-sort13 | 8 UNREACHABLE statuses; required SUCCESS/FAILURE only | 8 U records also violate empty `checks.unreachable` and all-success-or-intended-failure count rule |
| NEG-Cell | unsupported_constructs has 1 SUCCESS guards; required [] | 1 U records also violate empty `checks.unreachable` and all-success-or-intended-failure count rule |
| N2 | unsupported_constructs has 3 SUCCESS guards; required [] | 11 U records also violate empty `checks.unreachable` and all-success-or-intended-failure count rule |
| N3 | unsupported_constructs has 3 SUCCESS guards; required [] | 11 U records also violate empty `checks.unreachable` and all-success-or-intended-failure count rule |
| N4 | unsupported_constructs has 3 SUCCESS guards; required [] | 11 U records also violate empty `checks.unreachable` and all-success-or-intended-failure count rule |
| N01 | unsupported_constructs has 3 SUCCESS guards; required [] | 16 U records also violate empty `checks.unreachable` and all-success-or-intended-failure count rule |

No rejection here is caused by a missing location, timeout, additional native failure or failed cover. An S1 candidate argument does not change the producer predicates or historical results.

## Per-site S1 U candidate arguments

Method: `S1-ACCEPTANCE-DECISION-2026-11-17.md`, the source-local S3-1-r2 proposal/admission and S4P1 exact-case practice. For each of the **67 invocation-specific instances**, `U-ARGUMENTS.json` preserves the full exact property dictionary, root/selector, invocation/namespace, native member hash, pinned source SHA/file hash/context, cfg, domain, registration, explicit premises and argument. The following is a lossless grouping by exact property/site; every root occurrence is named. These are candidate definedness arguments for generated arithmetic/bounds checks, never admission of an unreachable mandatory post/frame/relation role. Covers do not replace the argument.

- **`slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.4`** — `library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:100`; roots NEG-order, NEG-sort13, N01 (3 instance(s)). In the order loop i starts1 and increments only under i<L<=32, so i+1<=32. In N00_01 the loop body has no source-feasible entry.
- **`slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.5`** — `library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:106`; roots NEG-order, NEG-sort13 (2 instance(s)). Entry validates before.len=L<=CAP32. The outer count loop has i<L, so before.values[i] is within the 32-element snapshot array.
- **`slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.6`** — `library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:111`; roots NEG-order, NEG-sort13 (2 instance(s)). Entry validates L<=CAP32 and the inner loop has j<L. Thus before.values[j] is in bounds. old_count starts0, increments at most once per j iteration, and is <=j before the increment; its successor is <=L<=32.
- **`slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.7`** — `library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:111`; roots NEG-order, NEG-sort13 (2 instance(s)). Entry validates L<=CAP32 and the inner loop has j<L. Thus before.values[j] is in bounds. old_count starts0, increments at most once per j iteration, and is <=j before the increment; its successor is <=L<=32.
- **`slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.8`** — `library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:112`; roots NEG-order, NEG-sort13 (2 instance(s)). Entry validates values.len=before.len=L<=32; inner j<L bounds values[j]. new_count starts0, increments at most once per j iteration, and is <=j before the increment; its successor is <=L<=32.
- **`slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.9`** — `library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:112`; roots NEG-order, NEG-sort13 (2 instance(s)). Entry validates values.len=before.len=L<=32; inner j<L bounds values[j]. new_count starts0, increments at most once per j iteration, and is <=j before the increment; its successor is <=L<=32.
- **`slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.10`** — `library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:113`; roots NEG-order, NEG-sort13 (2 instance(s)). Inner j starts0 and increments only while j<L<=32, hence j+1<=32.
- **`slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.11`** — `library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:118`; roots NEG-order, NEG-count, NEG-sort13 (3 instance(s)). Outer i starts0 in the count loop and increments only while i<L<=CAP32; therefore i+1<=32 even if a prior mismatch makes this site unreachable.
- **`slice::sort::shared::smallsort::verify::sorting_model::active_post::<cell::Cell<u8>>.assertion.11`** — `library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:118`; roots NEG-Cell (1 instance(s)). Outer i starts0 in the count loop and increments only while i<L<=CAP32; therefore i+1<=32 even if a prior mismatch makes this site unreachable.
- **`num::<impl usize>::abs_diff.assertion.1`** — `library/core/src/num/uint_macros.rs:3222`; roots N2, N3, N4, N01 (4 instance(s)). The self<other arm computes other-self; unsigned ordering implies other>=self, so subtraction cannot underflow.
- **`num::<impl usize>::abs_diff.assertion.2`** — `library/core/src/num/uint_macros.rs:3224`; roots N2, N3, N4, N01 (4 instance(s)). The else arm has self>=other, including equality, so self-other cannot underflow.
- **`slice::sort::shared::smallsort::bidirectional_merge::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>.assertion.1`** — `library/core/src/slice/sort/shared/smallsort.rs:974`; roots N2, N3, N4, N01 (4 instance(s)). len/2 divides by literal2, which is nonzero.
- **`slice::sort::shared::smallsort::bidirectional_merge::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>.assertion.2`** — `library/core/src/slice/sort/shared/smallsort.rs:990`; roots N2, N3, N4, N01 (4 instance(s)). The only call in this frozen small_sort_network body follows the no_merge return, hence requires len>=18. It supplies the slice of that same len, so len_div_2=floor(len/2)>=9 and len>=18; len_div_2-1 cannot underflow. In these exact roots len<=4, so that call has no source-feasible path. This uses the caller branch, not the callee intrinsics::assume as an added premise.
- **`slice::sort::shared::smallsort::bidirectional_merge::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>.assertion.3`** — `library/core/src/slice/sort/shared/smallsort.rs:991`; roots N2, N3, N4, N01 (4 instance(s)). The only call in this frozen small_sort_network body follows the no_merge return, hence requires len>=18. It supplies the slice of that same len, so len_div_2=floor(len/2)>=9 and len>=18; len-1 cannot underflow. In these exact roots len<=4, so that call has no source-feasible path. This uses the caller branch, not the callee intrinsics::assume as an added premise.
- **`slice::sort::shared::smallsort::bidirectional_merge::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>.assertion.4`** — `library/core/src/slice/sort/shared/smallsort.rs:992`; roots N2, N3, N4, N01 (4 instance(s)). The only call in this frozen small_sort_network body follows the no_merge return, hence requires len>=18. It supplies the slice of that same len, so len_div_2=floor(len/2)>=9 and len>=18; len-1 cannot underflow. In these exact roots len<=4, so that call has no source-feasible path. This uses the caller branch, not the callee intrinsics::assume as an added premise.
- **`num::<impl usize>::is_multiple_of.assertion.1`** — `library/core/src/num/uint_macros.rs:3916`; roots N2, N3, N4, N01 (4 instance(s)). The match handles rhs==0 in its separate arm; the remainder in the wildcard arm has rhs!=0. The only visible smallsort caller here uses literal2.
- **`ub_checks::is_valid_allocation_size.assertion.1`** — `library/core/src/ub_checks.rs:148`; roots N2, N3, N4, N01 (4 instance(s)). size==0 takes the usize::MAX arm; division occurs only in the else arm where size!=0. Concrete element size u8 is1 as well.
- **`ptr::const_ptr::<impl *const ()>::is_aligned_to.assertion.1`** — `library/core/src/ptr/const_ptr.rs:1479`; roots N2, N3, N4, N01 (4 instance(s)). Normal continuation follows the power-of-two test; zero is not a power of two, so align>=1 and align-1 cannot underflow.
- **`fmt::Arguments::<'_>::from_str.assertion.1`** — `library/core/src/fmt/mod.rs:820`; roots N2, N3, N4, N01 (4 instance(s)). The shift count is literal1, less than x86_64 usize width64. This generated shift-count property is defined for every s.len(); it is not a no-lost-bits or transmute-validity claim.
- **`slice::sort::shared::smallsort::small_sort_network::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>.assertion.3`** — `library/core/src/slice/sort/shared/smallsort.rs:381`; roots N2, N3, N4, N01 (4 instance(s)). len_div_2=floor(len/2)<=len for every usize len; len-len_div_2 cannot underflow. Additionally all four roots have len<=4<18, so no_merge returns before this site (and N0/N1 return at entry).
- **`slice::sort::shared::smallsort::small_sort_network::<u8, slice::sort::shared::smallsort::verify::sorting_model::KeyLess<u8>>.assertion.2`** — `library/core/src/slice/sort/shared/smallsort.rs:350`; roots N01 (1 instance(s)). len/2 has the literal nonzero divisor2. This remains defined for every usize len; the N00_01 early return also prevents reaching it at source level.
- **`slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.1`** — `library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:97`; roots N01 (1 instance(s)). The order loop starts i=1 and executes only with i<L=before.len=values.len<=32. Thus i and i-1 are valid values indices, and i-1 cannot underflow. For the N00_01 root L<=1, the loop body has no source-feasible entry.
- **`slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.2`** — `library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:97`; roots N01 (1 instance(s)). The order loop starts i=1 and executes only with i<L=before.len=values.len<=32. Thus i and i-1 are valid values indices, and i-1 cannot underflow. For the N00_01 root L<=1, the loop body has no source-feasible entry.
- **`slice::sort::shared::smallsort::verify::sorting_model::active_post::<u8>.assertion.3`** — `library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:97`; roots N01 (1 instance(s)). The order loop starts i=1 and executes only with i<L=before.len=values.len<=32. Thus i and i-1 are valid values indices, and i-1 cannot underflow. For the N00_01 root L<=1, the loop body has no source-feasible entry.

For model loop sites, entry rejects invalid snapshots, length>CAP32 and unequal before/after lengths; counter induction starts from source initializers. Negative fixtures have exact L=2/32/13/2 respectively. Later code made unreachable by an intentional early false return is preserved. For N01, L is0 or1. For merge subtraction, the argument uses the frozen caller’s `len>=18` path and exact small-call exclusion; it does not promote `intrinsics::assume` to a new trusted premise. No arithmetic argument establishes allocation ownership or general comparator behavior.

**U BLOCKER: none at this candidate source-reported level.** Independent actual emitted-property/caller/AST/MIR origin is UNKNOWN and is not claimed as proof or silently made an additional S1 gate.

## Every location issue and successful unsupported guard

All 1,143 native records have nonempty file and positive line; all eight frozen `RegularEvidence.validate` calls ACCEPT and every rich `missing_sites` array is empty. `METADATA-GAP.json` preserves those facts. There is **no** null/zero-location `.unreachable.1` case analogous to the admitted S3-1-r2 or S4P1 records. Their exact-run admissions do not transfer and no new syntactic location waiver is required.

`LOCATION-SITES.json` checks all ordinary coordinates against the exact std source and separately identifies these three non-std coordinate sites. `LOCATION-ARGUMENTS.json` retains all **13 full per-invocation dictionaries and identities** with separate candidate arguments:

| Exact ID/site | Root occurrences | Candidate argument and limit |
|---|---|---|
| `<usize as kani::rustc_intrinsics::ToISize>::to_isize.unreachable.1`, `library/kani_core/src/models.rs:203` | NEG-Cell, N2, N3, N4, N01 (5) | Exact stock tool model source at tool0aac, not a physical std file. Failed conversion has a retained SUCCESS `to_isize.safety_check.1` (Offset value overflows isize) before unreachable!. This system record is SUCCESS. Keep canonical export-prefixed path and native display, pinned tool source/hash and all same-invocation checks; physical std/MIR origin is UNKNOWN. |
| `memcpy.pointer.1`, `<builtin-library-memcpy>:33` | N2, N3, N4, N01 (4) | Exact SUCCESS pointer-system check with its complete same-object-violation description; backend builtin pseudo-location, not a Rust source coordinate. Retain complete dictionary/status/native display plus protected CBMC fingerprint, all counts/roles/covers/safety checks. Actual builtin source/lowering origin is UNKNOWN. |
| `memcpy.pointer.2`, `<builtin-library-memcpy>:34` | N2, N3, N4, N01 (4) | Separate exact SUCCESS pointer-system check for the reverse comparison, with its own description and line34. Same exact-case metadata argument and provenance limits; no source coordinate substitution. |

These source-reported metadata candidates use the same narrow system-record discipline as S3-1-r2/S4P1: exact tuple, counts, invocation, member/payload and protected identities; original status retained; unknown actual origin disclosed. They do not claim the backend C library source has been supplied or independently verified. **Location candidate BLOCKER: none; backend source identity remains UNKNOWN.** No blanket std/builtin/future-run or parser allowance is applied.

The other generated/macro coordinates, including core/lib.rs:358 (`kani_core::kani_lib!(core)`), remain source-reported macro locations, not substituted function definition lines. Every std coordinate exists in the pinned file; this check alone does not establish AST/MIR causality.

**13 successful unsupported guards are retained**, separately from status UNREACHABLE: NEG-Cell has one same_allocation guard, and each positive has that guard plus caller_location and foreign Rust rust_begin_unwind guards. `GUARD-ARGUMENTS.json` preserves each exact dictionary/site/member/invocation and its candidate interpretation. Pinned producer snippets in `POLICY-REFERENCES.json` show unsupported operations emit a failing assertion plus assume; SUCCESS reports no reachable guard violation in this bounded invocation, not general support or a licensed reachable unsupported operation. The exact same_allocation implementation tests allocation before its unsupported hook. Panic/caller-location and unwind support remain outside the claimed theorem. Strict producer empty-array rejection still applies to all13.

## Resource, timing and containment facts

Campaign **359.3813398520001 s**. Connected job 2026-11-19 14:54:34Z–15:09:32Z (898s); actual-leaf step 15:03:27Z–15:09:26Z failed, setup/checkout/build/upload steps succeeded. Setup receipt total 531.1854872703552s; stock-tool build child 269.343s with sampled peak 1453668KiB. These scopes are not interchangeable.

| Alias | Initial-export compile marker upper s | Whole child s | Exported verification s | Sampled PGID peak KiB | Outer sampled peak KiB |
|---|---:|---:|---:|---:|---:|
| NEG-order | 37.631 | 37.816 | 0.058600329 | 1941716 | 1965748 |
| NEG-count | 36.448 | 36.931 | 0.336841224 | 1956764 | 1978528 |
| NEG-sort13 | 36.346 | 36.581 | 0.098671217 | 1956808 | 1973160 |
| NEG-Cell | 37.531 | 39.48 | 0.437875524 | 2164248 | 2190704 |
| N2 | 36.719 | 41.716 | 3.061223584 | 2612416 | 2690704 |
| N3 | 37.915 | 43.751 | 3.846284711 | 2545732 | 2595072 |
| N4 | 37.542 | 44.183 | 4.692468986 | 2211672 | 2537976 |
| N01 | 37.661 | 72.998 | 33.427759135 | 2267724 | 2250476 |

All8 effective local caps are6291456KiB = min(local6GiB, outer12GiB, available−2GiB), with exact availability per row in `COST.json`. Child cap600s includes compilation; compile subcap180s, slot720s, campaign6900s, controller180s, cleanup240s, outer7500s, phase8100s and step7560s remain frozen. No timeout, signal, RSS/compile/slot/global cutoff or output truncation is reported; successful positives exit0, intended negative invocations exit1, and every supervisor exits0 after verified child shutdown/containment. All8 launch/native-start/cleanup intervals are serial and all8 completion seals authenticate.

Binary fingerprints agree at E0, controller pre, worker BEFORE, worker AFTER and controller post; protected identities and exact epoch contexts are in `PROTECTED.json`, serial order in `SERIAL-ORDER.json`. Outer and PGID RSS are sampled non-atomically; component peaks are not simultaneous and none is a kernel/cgroup/full-tree maximum. Compile markers are observed upper bounds through initial export, not exclusive compile CPU. `verification_time_s` is the native exported metric, not exclusive solver time. No internal symex/solver phase trace is available.

Each row retains64 lifecycle diagnostics with omitted counts72/93/96/110/115/112/102/117 respectively. Omitted events remain UNKNOWN; completion/shutdown/protected observations are separately checked. Relative to r1’s four whole-child600s timeouts, this run supplies completed positive inventories at unchanged caps, including N01 verification33.427759135s. This is measured cross-run behavior, not independent attribution of the speedup to a compiler/MIR cause.

## Validation and stop boundary

Frozen offline replay: **976 checks PASS**, including exact identities/dependency hashes/source-only gates, fresh local and upload-only collectors, sealed prefixes0..8, full native/role/cover partitions, protected epochs and shutdown/serial ordering. Supplemental audit: **2612 checks PASS** and **10 targeted adverse checks**, covering malformed terminal rejection, changed sealed export and changed protected driver rejection; original bytes and collector results restored. Every U/guard/location argument is tied back to authentic member dictionaries. No compiler/native/full host Validate or CI rerun was performed.

Artifacts follow the r1 method/format: INPUT identities in PROVENANCE/ROOTS; RESULT/QUALIFICATION; NATIVE-PROPERTIES; U/GUARD/LOCATION arguments; METADATA-GAP/LOCATION-SITES; PREFIX/SERIAL-ORDER/PROTECTED; COST; VALIDATION/AUDIT-VALIDATION/POLICY-REFERENCES and immutable MANIFEST. `seal.py --check` verifies this packet without mutation. For authorized offline reproduction run `replay.py`, `audit.py`, `render.py`, then `seal.py --check`; never rerun `acquire.py`.

**HANDOFF; one authorized stage complete.** Next is independent review of the exact intake/candidates followed by a separate coordinator admission decision. This author grants no admission, future exception, summary/provider/caller/generic/initmask/ownership/panic/Drop/MIR/B1/B2/general sorting/fullN16/N32 credit. The four bounded positive candidates cover only N0..4 in this initialized V34/base1 u8/KeyLess context if later separately admitted. Deferred obligations remain NOT_SELECTED/OPEN.

Only this run packet is changed. No CI submission/rerun/cancellation, source/control/policy patch, push, ledger/accounting mutation or external message. Local author and committer: Tiramisu-Cake <igkharin@gmail.com>; commit message contains `[skip ci]`. The containing commit SHA is returned separately to avoid a self-referential manifest.
