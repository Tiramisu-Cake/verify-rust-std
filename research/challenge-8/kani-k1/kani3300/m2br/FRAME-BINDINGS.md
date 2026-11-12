# M2-B/R private frame binding

Static source gap is established; the mapping of reported upstream `Check that *var_8 is assignable` to an actual emitted lvalue/object/range is **UNKNOWN**. This package does not claim a completed runtime causal binding or implement a repair.

## Source chain (exact source pins/hashes in INPUTS.json)

| Link | upstreambf9c58e662 | Part1 1cd96e354 / pre-A3b207 | A3Ra0 / B1I-A6134 / M1+M2 |
| --- | --- | --- | --- |
| private marker/static | mem_init.rs:18–19 marks MEM_INIT_STATE; :22 separate ARGUMENT_BUFFER is unmarked | ARGUMENT_BUFFER removed; buffer fields move into marked MEM_INIT_STATE (:34–45 at Part1) | same marked static, expanded protocol/snapshot fields (:34–52) |
| actual source store | :375–385 `store_argument(from:*const T,selected_argument:usize)` conditionally assigns Some(ArgumentBuffer{selected_argument,saved_address:from_ptr,layout_size:LAYOUT_SIZE}) to ARGUMENT_BUFFER | b207:413–425 writes selected index, saved object/offset, layout_size and active fields in MEM_INIT_STATE | :449–493 store additionally takes signature:usize; return0 starts mandatory protocol, ordinary stores check signature/count/order; selected branch snapshots value including false and relative offset |
| source load | :395–409 reads ARGUMENT_BUFFER; selected load calls copy_init_state_single and writes ARGUMENT_BUFFER=None; fallback blesses | b207:436–468 takes typed `[bool;LAYOUT_SIZE]`, copies by saved object/offset then clears active | :501–548 takes index/signature/count/layout; asserts protocol pairing, retargets witness with `buffer_value && layout[relative_offset]`; remaining/active lifecycle retained |
| marker lookup → emitted assigns | contract.rs:142–170 finds KaniMemoryInitializationState in kani/core statics, obtains mangled name and looks it up in symbol table; successful lookup creates lambda for the whole static expression | byte-identical | byte-identical |
| static emission | static_var.rs:18–22 uses Instance::from(def).mangled_name(), matching lookup source convention | byte-identical | byte-identical |
| public modifies + private set | contract.rs:173–235 derives user pointer tuple, excludes ZST derefs, chains shadow_memory_assign; shadow lookup failure silently gives empty vec | same algorithm | same algorithm; larger marked object can imply different emitted work |
| generated wrapper + DFCC | check.rs:83–106,140–158 creates Check closure and modifies wrapper; contracts.rs:566–585 chooses SimpleCheck for target before Assert; driver emits --dfcc and --enforce-contract | same source | same source |
| observed emitted lambda/write/frame property | UNKNOWN | UNKNOWN | UNKNOWN |

At upstream the private source object written by store_argument is **ARGUMENT_BUFFER**, absent from the marker-selected private assigns target. Its Some discriminant and selected_argument/saved_address/layout_size payload form source write candidates; exact lowered write subdivision/byte ranges are UNKNOWN. Whole-static MEM_INIT_STATE exemption is deliberate in source, not automatically excessive or a requested fix. Migration in Part1 puts those source writes in the exempted object, but does not prove successful marker lookup, retained lambda or actual DFCC inclusion on a concrete run.

P1/P2 have no user `#[kani::modifies]` entries; generated tuple/capture ABI and actual assigns must still be observed. No public modifies extension is proposed. Static source types do not show that `var_8` denotes the unmarked buffer: it could be a lowered pointer/temporary associated with another write. Missing lookup/symbol materialization is a separate hypothesis because `.unwrap_or_default()` can remove the private lambda on any pin. No actual property ID, object ID, base/offset/width, enclosing wrapper symbol or instrumented statement is currently bound.

## Minimal existing-receipt request before any frame repair

For run43244395728 P1 (and P2 if distinct), coordinator returns curated rows for reported assignability property: complete property ID/class/location and status → instrumented DFCC statement and write lvalue → assignment operands (`var_8` definition/address) → emitted symbol/object/base/offset/width → `store_argument` instance and source assignment → enclosing SimpleCheck/modifies wrapper symbol/contract → exact assigns lambda entries. Include artifact hashes, source/input pins and coverage. Record marker-discovered StaticDef, mangled symbol-table lookup result and why a private candidate is included/excluded. If this historical receipt is unavailable, mark FRAME_BINDING_UNKNOWN; do not read raw logs or repeat upstream automatically.

For matched pre-A3/A3R, return equivalent static→symbol→lambda→instrumented-write rows from existing non-solving inventories. Compare all before/after buffer/protocol writes, return0 and constructor/reset writes actually inside that wrapper. Public referents never belong to private targets. An absence of frame failure without a reached write is not a verified fix.

Upstream reported unreachable load_argument must be classified using transformed CFG/actual call kinds and reachability evidence. Distinguish legitimate path unreachability/abort, missing instrumentation, backend-hook return materialization and early Unsupported preventing comparable checks. An early Unsupported alone proves none of these. Check wrappers/closure FnOnce shims and resolved Item calls rather than extrapolating from select's source signature. Numeric signature is model-local `Ty::to_index()`, not a fixed ID.

## Proposal for next reviewed stage, conditional on binding

If actual `*var_8` binds to unmarked ARGUMENT_BUFFER, review a narrow private-buffer representation/assigns repair against the already present Part1 migration; do not add that exemption to user memory or patch the release source here. If lookup instead fails for MEM_INIT_STATE, repair that exact marker→emitted-symbol gap. Performance changes require phase/count evidence before a hunk is chosen. Coordinator/worker14 owns any implementation after this stage; no diagnostic ablation should be cherry-picked as a release fix.

Required future gates: unchanged P1 legal roundtrip/useful ensures PASS; unchanged P2 false-return intended uninit FAIL; existing user out-of-frame write intended frame FAIL; lawful modifies PASS; ordinary/false/typed masks and source-before-Move/reset semantics unchanged. These are required oracles, not new measured outcomes. M3 remains HELD.
