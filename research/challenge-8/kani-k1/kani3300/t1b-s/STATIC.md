# KANI3300 T1b-S — static cache / emission analysis
Source citations below are at Kani baseline 989f72351c (f046b70644 + unchanged production CMP2 b1f0105); diagnostic candidate does not repair this behavior.
- Each unit creates one shared_unit_transformer; harnesses in that unit reuse it. Unit reset already exists (kani-compiler/src/codegen_cprover_gotoc/compiler_interface.rs:485–494).
- order_harnesses can warm the same cache by reachability before sorting; clear_codegen_cache() per root clears another cache, not BodyTransformation (compiler_interface.rs:495–517; kani_middle/codegen_order.rs:57–89).
- BodyTransformation.cache keys only Instance. A miss starts from instance.body(), applies unit-configured local stub/instrumentation passes once, then caches; hits return that body (kani_middle/transform/mod.rs:86–102,104–148,152–226).
- These local transforms are reusable within the unit's configuration. Their cache is not a pristine local-only layer after a global writer changes it (transform/mod.rs:243–249).
- Per root, codegen_items first computes reachable items and a call graph from transformer.body_ref; these inputs may already contain a prior root's mutation (compiler_interface.rs:105–127; kani_middle/reachability.rs:171–178).
- DelayedUbPass scans raw instance.body() for initial targets, and runs points-to from raw root instance.body() with the pre-global call graph (transform/check_uninit/delayed_ub/mod.rs:70–144).
- It derives successors of the current root's target set, then instruments each reachable instance starting from transformer.body(), i.e. the currently cached, possibly globally modified body (delayed_ub/mod.rs:147–190).
- When instrumentation_added, DelayedUbPass replaces that instance's cache entry with TransformationResult(body,true); this is the root-dependent writer into the shared unit cache (delayed_ub/mod.rs:198–210).
- Each codegen_items receives cloned template GlobalPasses, but the same shared transformer. New pass objects therefore do not isolate their output bodies (compiler_interface.rs:522–532; transform/mod.rs:358–378).
- Reachability runs again only when a global pass reports modification. Otherwise the first item set remains (compiler_interface.rs:158–174).
- Baseline function_presence occurs before globals and the optional second reachability; it proves neither final presence nor GOTO consumption (compiler_interface.rs:130–156).
- GOTO codegen clones transformer.body(tcx,instance), then uses this same body for prelude, variables and blocks; body() does not rerun globals (codegen/function.rs:94–140; transform/mod.rs:243–249).
- Thus each emitted root consumes its instances' latest cache bodies, including any earlier root's global writes unless overwritten. Static code establishes the mechanism, not which concrete failing-root emission occurred in A3.
- A3 observed writer cmp3_into_iter_next → len hash9bae019701b64b9b → later lookup; its failing-root consumption, concrete object/offset/R and runtime causality remain UNKNOWN (../t1b-a3/RESULT-KANI3300-T1B-A3.md).
Design only: construct a fresh transformer per root, including reachability, local-pass auxiliary maps and globals, and retain it through complete GOTO emission. Heuristic warmup must use a separate transformer or discard its globally mutable state.
Alternative: share a pristine local-body cache and matching auxiliary metadata, with a fresh root-scoped overlay for global writes. Every reachability/codegen body reader must use that overlay until emission finishes; no global write may mutate pristine entries.
Resetting only per unit is insufficient. Do not disable CheckRef, blanket-seed shadow state, weaken checks, or change production CMP2 in this diagnostic stage.
T1b-S adds source-reported hash/last-writer observations at actual block emission plus final reachability presence; it does not establish runtime execution, cryptographic body identity, independent B1/B2, or causal proof. Credit NONE.
