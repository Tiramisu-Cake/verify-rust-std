# M2-B/R2 private storage bindings

Source-only links below use exact historical objects in INPUTS.json; emitted links are UNKNOWN. `*var_8` without its definition is not an object binding. No user modifies, model, checks or assumptions are changed.

| Link | Verified source coordinate / instance rule | Required emitted observation, currently UNKNOWN |
| --- | --- | --- |
| Marker→source static | All four pins mem_init.rs:18–19, KaniMemoryInitializationState→MEM_INIT_STATE | Selected crate/StaticDef, target instance, actual mangled symbol, marker lookup result and source span |
| Marker→symbol lookup | contract.rs:146–171 searches kani, fallback core; Instance::from(static_def).mangled_name(); symbol_table.lookup; unwrap_or_default | Exact symbol-table artifact/hash/JSON pointer and matching symbol; record failed lookup separately from no write |
| Static emission | static_var.rs:18–28 uses same mangling rule, codegen_alloc_in_memory | Actual declared symbol/object and allocation/backing type, size, padding, initial value |
| Symbol→assigns lambda | contract.rs:163–168 makes Lambda::as_contract_for(..., shadow_memory_symbol.to_expr()); :232 chains private target with public entries | Whole-static expression/type, lambda symbol/body, target address/base/offset/extent and membership; aliases/backing views |
| PFC→enclosing Check/modifies | contracts.rs:566–585 selects SimpleCheck for matching PFC target; library/kani_macros/src/sysroot/contracts/check.rs:83–106,140–158 generates Check/modifies wrapping | Actual metadata target/mode, mangled Check/ensures/modifies symbols, captures/ABI and enclosing wrapper for each write |
| DFCC pass | call_goto_instrument.rs:173–216 source constructs --dfcc root and --enforce-contract contracted_function | Actual expanded argv, pass input/output hashes/stages and corresponding instrumented statements |
| Private writes→DFCC operations | store/load anchors below; source writes do not specify backend subdivision | Exact instruction ID/location/instance, write lvalue/object/range; generated write-set/helper insertion, havoc/snapshot/assign/compare and operand/result types |
| DFCC→retained expression→conversion | No emitted receipt | Retained SSA/equation step and type width, operator/operands/use count, source/DFCC origin and exact phase milestone; absent reporting UNKNOWN |

The `contract.rs`, static emission, serializer and CBMC driver anchors have identical per-file SHA256 across U/R1/A1/E. This establishes unchanged source algorithms, not equal generated operations, successful lookup or equal private extents. Source lookup failure yields an empty private list, so it remains a separate discriminator.

## U→R1 storage migration and changed paths

U mem_init.rs:365–389: store_argument writes `ARGUMENT_BUFFER = Some(ArgumentBuffer{selected_argument,saved_address,layout_size})`. This is a separate, unmarked `Option<ArgumentBuffer>` static (:22), while the marker-selected MEM_INIT_STATE (:37–41) contains only tracked_object_id/tracked_offset/value. Source-selected exemption therefore names the other static. Q1/Q3 must separately observe ARGUMENT_BUFFER's Option/discriminant/payload and actual assigns membership; source does not establish that reported frame `*var_8` is this buffer.

R1 :404–422: saved_address is replaced by saved_object_id/saved_offset; store_argument writes five fields in the marked MEM_INIT_STATE. Return selected_argument==0 is now mandatory rather than demonic. R1 load_argument :426 onward copies by object/offset and resets active; A1/E store :413 and load :436 add typed preservation behavior. This moves the source writes into the source-exempt object and changes transfer/relevance paths. The actual DFCC inclusion, range, instrumented write checks and generated views remain UNKNOWN; no frame repair is accepted from source alone.

Request per write: marker→actual symbol→assigns lambda→enclosing SimpleCheck/modifies→actual DFCC write/havoc/snapshot/assign/compare→retained expression/type→conversion observation. Include constructor/reset and return paths as well as store_argument. Preserve aliases, offset/extent expressions, object IDs, captures and generated memory backing types; private object identity must not be inferred solely from a similar prettyName. For U's reported property supply complete property ID/class/location, definition of var_8, pointer derivation, byte range, callee instance and wrapper scope.

Upstream unreachable load requires actual transformed CFG/call kind and reachability/early-exit evidence. Early Unsupported alone does not distinguish legitimate unreachable path, missing instrumentation or stopped analysis. No-match/partial coverage remains UNKNOWN, not NOT_RUN. P1 has no explicit user modifies entries; actual generated tuple/captures and all frame obligations must still be inventoried.

Until Q0–Q4 arrive, neither a huge emitted private object nor costly DFCC use is established. If all measured related types are small, reject that size hypothesis for the measured model and discriminate operation expansion through Layout<N>/symbolic indices, array update/equality, dynamic-object views, pointer/object-whole operations and arithmetic/conversion. Width without retained use and low VCC count without operand widths prove neither causality nor cheapness.
