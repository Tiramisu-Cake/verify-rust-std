# Enabled initialization mask feasibility — PLANONLY

**Conclusion: specific layout and mask-method prerequisites are needed before a separate reviewed uninitON experiment.** Stock source provides a compiler-coupled, non-reading **u8 positive assertion oracle**, but it does not establish a runnable or qualified exact partial-MU48 mask proof. Native compilation, transformation, solver, overhead and fit are **NOT_RUN/UNKNOWN**; independent native proof **NONE**. Current S3-2-r1 partial rows remain diagnostic/INIT_OPEN.

Frozen tool `0aac16ef62da9e9d5645782d458593e5d78143ba`, source `513341f41ce53833a279571401c924bdddddb6c8`, assignment `227854d0a66b46e9d13e721932c9afa06a986ec8`. All references below resolve to exact commit/blob/range hashes in SOURCE-CITATIONS.json. Only committed planned masks were read; no uncommitted13 candidate, intake42U, raw evidence or other-party implementation was consulted. The existing OFF-path blocker is a preserved premise and is not re-audited here.

## Enabled path and actual effects

`-Z uninit-checks` is an opt-in CLI proposal, NOT_APPLIED. Driver emits `-Z ghost-state` and `--ub-check=uninit`; compiler gates the passes with `ExtraChecks::Uninit`. Existing `cfg(kani)` installs in-core instrumentation; this is not a source algorithm/profile change. Valid-value checks are separate. Local order is stubs/contracts/AnyModifies, optional ValidValue, Uninit (assert-no-assume safety), intrinsic generation, loop contracts and Rustc intrinsics. Per-entry reachability then feeds global DelayedUb, with reachability recomputed if it changed bodies. [CLI_FLAGS, FLAG_ARG, ORDER, GLOBAL_ORDER]

Harness setup chooses **one arbitrary object/byte and a false bit**. The model `get` returns the bit only for that tracked data coordinate and returns true elsewhere; it is an assertion abstraction, not an enumerable concrete map. Compiler-inserted `Set`/`SetRef`/`SetSliceChunk` update actual store footprints with type data layouts; copying nondeterministically moves the tracked source coordinate to destination, or blesses its destination branch. No manual `ShadowMem.set` is proposed. [HARNESS_INIT, HARNESS_SETUP, MODEL_GET, MODEL_SET, MODEL_COPY, MODEL_SETUP]

| Actual source operation | Enabled source route | Limit needing exact MIR/native binding |
|---|---|---|
| New raw allocation | default uninitialized state; zeroed alloc explicitly SetSliceChunk true; dealloc false | allocation identity/reuse and actual shim body |
| `MaybeUninit::uninit()` | union empty field; CreateUnion chooses empty-field mask and sets data bits false | MU48 aggregate/union pointer paths may be unsupported |
| initialized raw `ptr::write` / `*p = value` | source write_via_move lowers to raw Assign; visitor emits post-store Set true | actual lowered store and exact u8 layout |
| `MaybeUninit::write` | assigns initialized union then returns initialized reference | union assignment/deref support, not blanket array support |
| `ptr::copy_nonoverlapping` | CopyNonOverlapping -> Copy -> CopyInitState model | each actual merge copy, count and offset mapping |
| `ptr::read` / raw dereference | typed dereference -> Check before data use | no reading a hole to observe its state |
| raw AddressOf creation | post-instruction Set true blessing of the addressed place | distinguish model blessing from physical write; verify justified layout/init |
| ordinary typed local stores/reads exposed by aliasing | DelayedUb points-to target/ancestor SetRef/CheckRef | reachable cast/copy and alias analysis, not every local automatically |

[ASSIGN_PREFLIGHT, UNION_WRITES, COPY_STMT, COPY_ALLOC_INTRINSICS, READS, BUILD_OP, BUILD_COPY, DELAYED_TARGETS, DELAYED_STORES, PTR_WRITE, PTR_READ, PTR_COPY, MU_WRITE]

## Correct oracle and storage prerequisite

Inside core use assertion-only `Init_u8(p,i) := crate::kani::mem::is_initialized::<u8>(p.add(i))`. Its actual signature takes **one pointer**, not a separate len. It does not perform a typed byte load. Require live backing allocation/provenance, `i<48`, byte extent, alignment1, and separately valid permissions. Raw cast/pointer formation does not initialize Rust data. However, the stock pass emits Set true for raw AddressOf creation as a blessing of a presumed initialized place; exact lowering must show this instrumentation is justified and does not mark a hole initialized before a query. Treat it as a separate model event in the coupling proof, not an actual byte store. [ADDRESS_BLESS] Borrow only known-init source8; destination stays a disjoint raw u8 pointer. Do not form a full initialized-u8 reference over holes. [MEM_API, CORE_PATH, CORE_INSTALL, MU_RAW]

`T=u8` selects a one-data-byte layout. `[u8;8]` selects eight data bytes; a raw `[u8]` pointer uses its fat-pointer length. A zero-length or zero-sized query is vacuous. **`T=MaybeUninit<u8>` is not a valid substitute:** it is a transparent union, and stock enabled intrinsic generation emits an unsupported-union check. An array/slice element recursion into MU also has `UnionAsField`. This is an explicit unsupported route, not evidence that the predicate successfully checked initialized underlying bytes. A hypothetical permissive all-false layout would be vacuous, but that is not the established stock path. [ORACLE_U8, ORACLE_SLICE, ORACLE_UNION, LAYOUT_UNION, LAYOUT_BYTE_ARRAY, LAYOUT_NESTED_UNION, MU_REPR]

There is a **storage-level issue even when the oracle is u8**: the ordinary assignment visitor preflights the assigned type. If `[MaybeUninit<u8>;48]` aggregate assignments survive into this pass, recursive array layout hits `UnionAsField` and inserts unsupported. Union-pointer operations without an active field have a further unsupported route. These source branches require a specific supported lowering/tool fix or exact MIR proof that they are avoided, without changing the domain. Their actual native reachability is UNKNOWN; no compiler was run. [ASSIGN_PREFLIGHT, LAYOUT_BYTE_ARRAY, LAYOUT_NESTED_UNION, SET_UNION]

`!Init_u8(p,8)` is not a universal assertion that a hole is uninitialized: queries to untracked holes return true. Likewise, `old(Init_u8(p,i)) == Init_u8(p,i)` does not snapshot a complete invariant when copy may retarget the selected coordinate. Never assume/branch on these predicates to prune model choices. Positive initialization assertions quantify over the model choices; complete negative mask bits need an independently checked store-footprint/mask relation or a separately approved stronger oracle. No new trusted model is proposed or enabled. [MODEL_GET, MODEL_COPY, DEMONIC_USE]

## Exact future masks and distinguishing controls

Masks below are logical source specifications, not exported native masks. All prior initialized values remain independent full bytes; only source halves4+4 are ordered. Use the actual frozen merge body and concrete `KeyLess<u8>`.

| Case | src / dst | Initial initialized K0 | Required final K1 | Counts K0 -> K1 | Holes after |
|---|---|---|---|---|---|
| L | 32 / 0 | [32,40) | [0,8) union [32,40) | 8 -> 16 | 32 |
| R | 40 / 16 | [0,8) union [32,48) | [0,8) union [16,24) union [32,48) | 24 -> 32 | 16 |

For both, K1=K0 union dst8, new bits exactly8, src8 is in K0, dst8 is disjoint K0, and sentinel8 stays a hole. Previously initialized outside-dst values must remain unchanged; never snapshot/load the other bytes as u8. These are the committed planned domains, not a reading of13's uncommitted implementation. [ROOT_MASKS]

PLAN.json gives eight conceptual selectors under `...::init_mask_enabled_future::`, four per case:

1. **Actual merge positive:** assert Init_u8 on K0; actual `bidirectional_merge::<u8,KeyLess<u8>>`; assert destination8 initialized before any typed/spec output loads. Check order plus full-value multiplicity, source/known-init frame and exact dst-only modifies. Negative mask bits still need prerequisite P2.
2. **Hole8 negative:** after authentic merge, assert Init_u8(p,8), with no typed hole load. Expected only a counterexample at the named literal initialization assertion; an unrelated unsupported failure is inconclusive.
3. **Outsidewrite effect pair:** deliberately write p+8 in an isolated harness diagnostic, then the same positive Init_u8 assertion should succeed. It is an intentionally wrong K1, never a correct merge result. A separate diagnostic wrapper declaring only dst8 modifies but performing that outsidewrite must fail its exact real-byte frame check.
4. **Missing destination write:** isolated writer writes seven destination bytes and omits dst+7, then asserts Init_u8 there. Pair with all8 writer. Expected missing-write literal failure versus all8 success; no typed omitted-byte read and no claim the handwritten writer is the actual merge.

All expectations are conditional designs and **NOT_RUN**. Never accept unsupported errors, early abort, setup rejection or vacuity as these intended controls. The sentinel negative/explicit write pair can distinguish store tracking; it cannot establish the complete untouched-hole theorem by itself. [MERGE_CONTRACT, MERGE_STORES, MERGE_LOOP]

Conceptual argv is stored as a vector in PLAN.json: stock0aac cargo-kani, one future exact selector, `--lib`, `--default-unwind 50`, `-Z function-contracts`, `-Z export-json`, `-Z uninit-checks`, fresh export path. The future source/module does not exist in513. This is not a runnable package, environment instruction, profile edit or GO. Full effective flags and source pins must be part of a later reviewed package.

## Contract capture and assigns

PFC Check assumes requires, captures `old` expressions with clone after requires, executes original modifies wrapper, then asserts ensures. Capture only known-init source/value frame and scalar geometry, never a full unknown u8 backing. Clause-depth guards control Original/Check dispatch and are not blanket uninit suppression. Models are excluded from recursive instrumentation. [CHECK_CONTRACT, ACTUAL_BODY, MODIFIES_BODY, OLD_CAPTURE, OLD_ORDER, CLAUSE, SKIPPED]

Real modifies codegen emits `len * size_of(element)` for dst slice and, **if found in actual symbol table**, appends the marked whole `MEM_INIT_STATE` static to assigns. This permits shadow updates during the original body; it is not a proof that only dst's logical init bits change. The lookup can fall back to an empty allowance, so actual exported DFCC assigns must be inspected for the exact in-core instance. Checked real-store footprint plus a justified complete instrumentation relation would be needed to derive K1 exactly. No summary, global shadow frame premise or count waiver is granted. [ASSIGNS_SHADOW, ASSIGNS_REAL]

There is another source-visible confirmation risk: model copy retargets with usize `to_offset-from_offset`. Both L/R copy downward in one allocation; if checked subtraction is retained, the selected-source/reset branch has an arithmetic hazard. Base driver uses overflow-checks=on, but actual effective core settings/lowered check presence and execution remain UNKNOWN. Preserve any native failure; do not disable checks to force a result. [MODEL_COPY, CFG_ARITH]

## F4 singleton boundary

The source answer is conditional and precise. In **manual Harnesses** mode, `determine_targets` applies exact metadata selection **before** group_by_stubs and transformer creation. If it actually yields one metadata entry, that unit has one harness entry/global-pass call. Ordering immediately returns for fewer than two. Closures, multiple contracted callees/providers or many reachable instances within that one entry do not by themselves recreate the known cross-harness cache reuse. [MANUAL_MODE, FILTER_BEFORE_UNIT, FILTER_IMPLEMENTATION, EXACT_MATCH, ORDER_SINGLETON]

Singleton does **not** restrict transformed analysis to only the root body: local transformations and the global delayed pass still inspect its reachable cast/copy/alias targets, including contracts and closures. AllFns/autoharness adds automatic roots beyond manual selection; absent/nonexact/ambiguous filters or multiple selected harnesses invalidate the singleton inference. The stock Instance-keyed cache is shared across entries of one unit, and DelayedUb writes global instrumentation into it. `clear_codegen_cache` clears a different cache. Per-unit/new-process boundaries matter. No F4 fix or #4591 tool was imported. [CARGO_FLAGS, UNIT_GROUPS, SHARED_CACHE, CACHE_KEY, GLOBAL_ORDER, DELAYED, DELAYED_TARGETS, CLEAR_OTHER_CACHE]

A future authenticated compiler record must establish manual reachability mode, exact selector cardinality, unit membership and no additional entry/global passes. Source existence is not actual MIR binding, and CLI singleton alone is not that record. Native closure/provider lowering, alias membership and F4 relevance for the future package remain UNKNOWN.

## Remaining prerequisites and authority

P1 resolves exact MU48 aggregate/union support or its established lowering; P2 supplies the checked complete-mask/store relation; P3 binds enabled flags, every relevant hook, contracts and shadow assigns to actual MIR/native evidence; P4 establishes singleton scope or separately resolves broader F4 exposure. Then P5 requires a new exact package, independent review and explicit root/coordinator GO. The detailed prerequisite list and native unknowns are in PLAN.json.

No source/control/tool/profile/flag/runtime change, build, native run, publication, dispatch, reserve or accounting action occurred. Current admitted seven S3-r2 SOURCE_REPORTED cases and current diagnostic boundary remain unchanged. Compile/solver overhead/RSS/time/fit are NOT_RUN/UNKNOWN, with no solver-cost estimate. Future authorized root runs use ordinary item2 attempt accounting; item1 is exhausted31/31, item2 remains12/17, total43/48. #4591 stays HOLD14ab awaiting owner morning+1, not given. Approval of this PLAN does not authorize implementation or CI.
