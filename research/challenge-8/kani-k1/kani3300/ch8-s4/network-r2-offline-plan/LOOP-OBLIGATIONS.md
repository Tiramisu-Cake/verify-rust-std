# Source work and unwind obligations

All source references below are at c12867b1e651a3927cbd9f169fe2c3d3728a44c3 unless prefixed TOOL (0aac16ef62da9e9d5645782d458593e5d78143ba). PROVENANCE.json supplies full paths, blob hashes and line ranges. Bounds are feasible **source body iterations**, not CBMC --unwind values, dynamic timings, or completed native verdicts. Early rejection can reduce oracle work. Array construction, copies, contracts and compiler-generated helpers require a separate lowering inventory; no compiler/expansion was run.

| Work / citation | N0 | N1 | N2 | N3 | N4 | Obligation |
|---|---:|---:|---:|---:|---:|---|
| Harness full frame, harness:32-34,57-59,82-84,107-109 | 34 | 34 | 34 | 34 | 34 | Checks all outside indices; independent of active N. Keep loop and bound 36. |
| Pre-snapshot copy, model:78-89 | 0 | 1 | 2 | 3 | 4 | Owned initialized values; CAP=32 initialization is separate fixed work. |
| Post adjacent ordering, model:95-101 | 0 | 0 | 1 | 2 | 3 | Full u8 comparison; no masking. |
| Post query loop, model:104-119 | 0 | 1 | 2 | 3 | 4 | Each input value, including duplicate queries. |
| Post inner count loop per query, model:109-114 | 0 | 1 | 2 | 3 | 4 | Total inner bodies <=N squared: 0/1/4/9/16. Not a single N-squared-depth loop. Two count predicates per body. |
| Descending cover helper, harness:12-19 | unused | unused | 1 | 2 | 3 | Short-circuits; N01 has no such cover. |
| small_sort_network outer region loop, kernel:339-382 | 0 | 0 | 1 | 1 | 1 | For 2..4 no_merge=true, region=len, prefix=1, return after insertion. |
| insertion_sort_shift_left tail loop, kernel:714-735 | unreachable | unreachable | 1 | 2 | 3 | Offset=1; tail increments to end; requires initialized span and 1<=offset<=len. |
| insert_tail sift loop per tail at offset j, kernel:670-700 | unreachable | unreachable | <=1 | <=2 | <=3 | At most j bodies; sift moves left and breaks at begin. Total over calls <=1/3/6. Comparator calls also <=1/3/6; not an observed native count. |
| Potential span-contract ordered loop, span:32-39 | 0 | 0 | 1 | 2 | 3 | Only if actually emitted/executed; precondition of a tail may use smaller prefix. |
| Potential span capture/post, span:21-30 | model above | model above | model above | model above | model above | Repeats snapshot/order/count work if instrumented; never assume free or a proved provider. |

Additional construction and implicit work, deliberately not assigned an invented loop ID/bound:

- Harness creates 34 arbitrary u8 values and copies all 34 to bytes. TOOL arbitrary:31-44,65,125-131 specializes the u8 array to any_raw_array; TOOL lib:530-546 forwards to any_raw<[T;N]> in verification mode. The generic trait default [();N].map is **not** this u8-array source route. Exact hook lowering, array copy, slice/range/iterator checks and internal memory-predicate loops remain uninspected/UNKNOWN.
- Model:9,66-88 creates a 32-cell zero-filled Snapshot for the pre-state; initialization and value copies are fixed source work independent of N, not an explicit 32-body Rust loop in that source. Invalid-snapshot path also constructs 32 cells, but the chosen valid u8 N<=4 facade does not need that branch. Source specialization (model:137-157) is active, established by the retained guard; actual instrumented binding still needs evidence.
- Kernel:348 declares MaybeUninit<[T;32]> only after len>=2. This is uninitialized scratch storage, **not** 32 initialized symbolic values. For feasible 2..4 it is not read: no_merge returns before merge. CopyOnDrop (kernel:316-329,681-688) copies one initialized temporary/element; memory-intrinsic lowering, safety predicates and drop paths have no source loop count that can be transferred to CBMC automatically. Stateless full-u8 KeyLess cannot panic at its source comparisons; no panic/safety check may be disabled on that basis.
- sort9/sort13 fixed swap sequences, bidirectional_merge and the second-region path are unreachable in feasible source executions for N<=4 (kernel:360-390). sort4_stable is not called by this small_sort_network branch. They are not presumed pruned from actual GOTO/MIR: N01 progress shows why that distinction matters. Library/model/generated loops on symbolically explored paths must be included in any future lowered inventory.
- Active guards and pair predicates have no explicit data-dependent source loops in the selected exact u8 route. Ordinary contract emission, safety::requires, Kani modifies/spec plumbing and same_allocation implementation/lowering are not a proved-zero-cost path. Actual stock configuration has assert_contracts=false and no verified stubs, but that is not an expansion/assumption trace. No claim that every source contract body executes, or that none do.

## Evaluation of unwind(N+1)

For N01/N2/N3/N4 this proposes global 2/3/4/5, respectively. The harness frame loop alone has 34 feasible bodies in every root. Thus the source iteration argument does not justify a global N+1 bound; no lowered evidence establishes that independent work was completely unrolled or eliminated. With unwinding checks ON, any remaining cut frame loop must cause a failure/incomplete result rather than proof acceptance. Disabling checks or dropping the full frame in favor of one canary would weaken the process/theorem and is excluded.

Even the bounded explicit algorithm/oracle iterations do not establish the correct CBMC off-by-one, transformed-loop identities, implicit helper bounds, or native exhaustion. Retain source unwind36 as the baseline, **not** as an independently proved universal lowering bound. No positive native unwind inventory completed in the intake. A smaller global bound would first require an equivalent full-frame/oracle representation, exact lowered loop inventory and successful complete unwinding verdicts under separately authorized execution.

TOOL call_cbmc:763-769 resolves CLI --unwind > harness attribute > --default-unwind. Its 270-273 emits the selected global bound. The actual committed positive argv has --default-unwind36 and no CLI --unwind override (intake ROOTS.json /rows/4..7/argv), agreeing with harness36; the three first controls use default34 and the Cell control default36. PROVENANCE.json records the exact per-row pointers. TOOL args:626-628 keeps unwinding ON unless checks are explicitly disabled; call_cbmc:346-350 avoids converting self-loops to assumptions and only emits --no-unwinding-assertions when disabled.

Per-loop --unwindset would require exact GOTO loop IDs and all reachable-loop bounds, which are absent. It is also incompatible with the baseline default-unwind argument under TOOL args:826-838: any extra CBMC argument starting --unwind conflicts with --default-unwind/--unwind. Do not smuggle it through the current profile or propose an unreviewed flag workaround. A separate future flag/profile proposal and native loop evidence would be required; neither is recommended in this plan.
