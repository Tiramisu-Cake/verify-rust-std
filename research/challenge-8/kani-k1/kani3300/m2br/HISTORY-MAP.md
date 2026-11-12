# M2-B/R history and source boundaries

Static Git audit in the read-only source repository. Full commit/tree/parent IDs, changed paths and SHA256 of all inspected anchors are in INPUTS.json; every adjacent row below is a verified direct parent. Table order is Git order. No historical outcome was reclassified.

| Stage | Commit | Delta class |
| --- | --- | --- |
| Upstream | `bf9c58e662fd65c64381ef2ac97a6397ffc0693a` | BASELINE |
| Part1 | `1cd96e354ec45346b61c245554a50a8af8cb5ce7` | PRODUCTION_AND_TESTS |
| A1 production | `fc37f9021d4cdb0e7c66e96c8a9f45aa99e85652` | PRODUCTION |
| A1 tests | `5fd713a200aea3ba85edcc341f48a0a20331fce2` | TEST_ONLY |
| A1 final / ZST repair | `613c188313e34e51e6a69d2c62bbd6ded2511819` | PRODUCTION |
| A2 production | `1f91626a305161ac6b9ba6c79ae66daa22af9c54` | PRODUCTION |
| A2 tests | `1dc99da6bf3c6387d8f69d9a44ffa8a8e0419139` | TEST_ONLY |
| A2 golden | `b8c0d00ac3ab00eefaa22396274af4e9d2b15450` | TEST_ONLY |
| A2 test repair | `3dc0227cee87d85bed32678a2209353ebdb9d2fa` | TEST_ONLY |
| A2R production + tests | `85fc5cd2ca770cdc5ae1bb514c27b6da7b6d9b18` | PRODUCTION_AND_TESTS |
| A2R final / pre-A3 | `b207847932da34ac19886c1337f5b69ace0b0843` | TEST_ONLY |
| A3 production | `e3c529a0d5a501987a36c1481bb7e8a48c80dc73` | PRODUCTION |
| A3 tests | `55d704a56dbd5864ffb75e3d861a544c281f8ebd` | TEST_ONLY |
| A3 test repair | `14c0a3c95b6ece62b01f96f663b455f8c5e155dc` | TEST_ONLY |
| A3 final / coverage tests | `0b1d68ac691cac7e03dbe73f4aec139bb5389059` | TEST_ONLY |
| A2R2 production + tests | `585c93b2ff366f5723611a7ca944328ef62f40b5` | PRODUCTION_AND_TESTS |
| A3R production + fixture repair | `c57314d4cf8aed4721c3170827827c6c9b9cd429` | PRODUCTION_AND_TESTS |
| A3R final / intrinsic repair | `a0a2386001a15fecfe2facc2f6cd87f3dee13b60` | PRODUCTION |
| B1I production | `cdb439b0a4c36e9e595019895ab803230f332941` | PRODUCTION |
| B1I tests | `dc5f5a406749a73f1c3192e0b5338441e79508bb` | TEST_ONLY |
| B1I-A tests | `6134e42dd1c65dc980336e7d9455aba02d423edf` | TEST_ONLY |
| M1 production + tests | `254ae69662b3206cd4432dae0cd44c534b1b13fb` | PRODUCTION_AND_TESTS |
| M1 tests | `5abdcf982da6aff65662e198af27a9c776830a89` | TEST_ONLY |
| M2 tests | `5f7f2b7364135a0a8b7cfd86c43b4491a8911bac` | TEST_ONLY |

## Source deltas that can distinguish resource hypotheses

- **upstream → Part1 1cd96e354**: MU-storage relevance/transfer instrumentation expands beyond direct unions. The independent `ARGUMENT_BUFFER: Option<ArgumentBuffer>` becomes fields in marked `MEM_INIT_STATE`; saved pointer becomes object/offset. New typed storage paths, return transfer and constant-mask handling change executable obligations. This boundary may change both relevance and DFCC writes; it is not a pure performance patch.
- **Part1 → A1 fc37f9021 / final613c188313**: typed preserve masks distinguish data from padding; raw transfers retain full extent; zero-sized transfer guard. New mask parameters/monomorphizations are source candidates. Source size is not backend size.
- **A2 1f91626a3 → A2R 85fc5cd2c / finalb207847932**: nested Pat/enum offsets, fail-closed unsupported byte operations, then full-pointee checks for both raw_eq operands and relevance roots. P1/P2 use scalar equality, but actual generated library calls must be inventoried before treating this delta as inactive.
- **pre-A3 b207847932 → A3 e3c529a0d**: common caller/callee Item predicate, explicit Begin/signature/count/written/remaining/order assertions, source snapshot, demonic argument choice, mandatory return0 and loads, all snapshots before Call(Move) source clearing. Private state grows from 6 usize + 2 bool source fields to 11 usize + 4 bool. These are source field counts, not ABI bytes, generated operation counts or a causal resource result. Neither state struct contains an unbounded array; `Layout<N> = [bool; N]` exists separately and actual generated N/instances remain UNKNOWN.
- **A3 final0b1d68ac69 → A2R2 585c93b2ff**: raw_eq checks reference pointee via AddressOf instead of reference storage. A2R2 is AFTER A3. No protocol removal.
- **A2R2 → A3R c57314d4c / a0a2386001**: `argument_count.max(1)` removed (transitive integer_max Unsupported); argument/return branch assertions retained, custom MIR fixture unwind actions repaired for panic=abort, intrinsic/shim pairing stays fail-closed. A3/A2R2 can have known Unsupported/build defects: an early exit is not resource relief. First comparison uses final A3R rather than silently repairing old pins.
- **A3R → B1I cdb439b0a4**: shared call classification and single body walk/common flush preserve instrumentation across unresolved callees; fallible seeds and bodyless handling. This can change actually retained call paths and checks without changing `mem_init.rs`. B1I tests dc5f5a4067 and B1I-A6134 are test-only (verified changed paths); do not attribute their changes to production.
- **B1I-A → M1 254ae69662**: immutable allocation collection/origin graph and reset-completion seeds can change extents and reachability. M1 tests5abdcf982 and M2 tests5f7f2b7364 add no production delta. The reported cutoff already exists at6134, so M1 is not necessary for that observation; an additional effect remains possible.

`contract.rs`, `contracts.rs`, `check.rs`, driver DFCC orchestration and CBMC invocation files are byte-identical from upstream through M2 (per-pin hashes). An unchanged lowering function can still emit different work for changed input state/types. No workflow delta is present in this audited ancestry; CI recipe/installed binaries remain separate identities.

## First discriminating boundary

Compare unchanged P1 at **b207847932da34ac19886c1337f5b69ace0b0843** and **a0a2386001a15fecfe2facc2f6cd87f3dee13b60**, using matching inventories before solving. This spans A3 protocol/snapshot changes plus A2R2/A3R repairs; even a measured difference would locate an interval, not identify one hunk. Both have buffer-in-private-state, so this comparison cannot isolate the Part1 frame migration. Test-only paths are not installed into the matched singleton inputs. Early Unsupported, missing path or build error makes the pair non-comparable. No full bisect or source ablation is justified yet.
