# Harness-specific global transformations

Candidate: `cab66681c912a3e5ee01a106faaeee5237ca0232`, direct child of frozen upstream main
`faffcee3bca2770c03bd21c3bde89cc8f6f7a14e`. Static reasoning; compiler build and fixed runtime NOT_RUN.

## Defect and applicability

`DelayedUbPass::transform` derives analysis targets and a points-to graph from the current
`starting_items`. It instruments `transformer.body(tcx, instance)` and writes the result into the
Instance-keyed `BodyTransformation.cache`. `codegen_items` receives one harness as its starting
item, runs those global passes, recollects reachability when modified, and uses the same
transformer for codegen. Main passes the shared unit transformer to each harness, allowing a
later harness to retrieve an earlier harness's delayed-instrumented body.

The immutable reproduction intake `06ff67af4aa1dd8df2cdbf2eec58bf3863008748` from run
44177926794 records initialized singleton SUCCESS and paired FAILURE in both cfg variants,
with an added uninitialized read at the shared `read_value`. The delayed singleton/paired and
independent raw-padding control retain intended FAILURE. This is bounded runtime reproduction,
not an independently established general proof or measured compiler ordering.

## Chosen lifetime

1. Construct `shared_unit_transformer` per codegen unit with its original contracts/stubs.
2. Keep `order_harnesses` and its local-transformation cache warming unchanged.
3. Clone that transformer inside the harness loop, before `codegen_items`. The shared template
   receives local transformations during ordering; harness global passes mutate only the copy.
4. Use the copy for initial reachability, global passes, recollected reachability and codegen.
5. Drop the copy after that harness. Keep `clear_codegen_cache()` at the original boundary.

`BodyTransformation` now derives Clone. Its two pass vectors already support deep cloning via
`Box<dyn ClonableTransformPass>` and the clone machinery in `transform/mod.rs`. The cache holds
owned `TransformationResult(Body, bool)` values, which already derive Clone. The two loop-contract
maps hold owned vectors or copyable instance/local identities and clone together with their
matching bodies. Warmed pass state and generated loop-modifies metadata therefore stay aligned.
The passes' contract target, unused closures, stub configuration and helper discoveries retain
the codegen unit's configuration. Newly discovered local bodies are transformed by that harness's
copied passes and remain available throughout its codegen.

Global passes already clone per harness; their target discovery, original checked-body scans,
points-to analysis, delayed instrumentation and initialized-memory checks are unchanged.
`PubFns` retains its single transformer/call. Export workers receive owned symbol tables and
metadata from `gcx.split()` rather than borrowing the transformer. No other cache is cleared.

## Alternatives and practical limits

A new transformer per harness would discard cache warming and rebuild local transformations.
Saving/restoring only delayed-written entries would couple cache rollback to every global-pass
write and bodies discovered during recollected reachability. A general cache overlay would
expand this standalone fix. Cloning uses the existing pass/body Clone support and a single
harness lifetime boundary.

The copy adds transient body/pass/map allocations per harness and may repeat local work for
bodies discovered after ordering or when no export workers exist. At most one harness copy is
live on the compiler thread alongside the shared template; worker exports own their data.
Performance/RSS effects are unmeasured. Review14 should assess this tradeoff; full standard
regression/performance/compiler-benchmark CI must check it before acceptance. No performance
claim or successful compilation is inferred from the static trace.
