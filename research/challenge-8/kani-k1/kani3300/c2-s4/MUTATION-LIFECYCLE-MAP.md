# S4 mutation and lifecycle map

Structural source review only; compilation/native tests/CI NOT_RUN.

| Stage | Ownership / state |
| --- | --- |
| Unit construction | One BodyTransformation per existing unit; pass order, stubs/contracts and configurations unchanged |
| order_harnesses prewarm | Runs before scoped codegen; cached regular transformations remain available |
| codegen_items entry | delayed_scope begins before first reachability; rejects any unclosed journal |
| First delayed replacement | Moves the complete previous TransformationResult (Body + modified bool) into journal keyed by exact Instance |
| Repeated replacement | Leaves first original intact; discards intermediate delayed result |
| Delayed instrumentation write | replace_delayed_body after transformer.body; snapshot already includes regular passes |
| Failed-root Unsupported write | Same API, after ordinary instrumentation; cannot replace the original snapshot |
| Second reachability and codegen | Read delayed versions throughout current model, including declarations and contract processing |
| Quantifier/immutable finalization | Still inside scope; emitted model complete before restore |
| gcx.split and enqueue | Moves SymbolTable and owned maps/paths into FileDataToWrite/WithInterner |
| codegen_items return | RAII Drop restores exactly touched entries; originals with false/true modified flags move back unchanged |
| Recoverable return/unwind | Same Drop; no production panic-catching; process abort cleanup not claimed |
| Next harness | Reuses regular warmed/new cache and existing loop metadata; no cumulative delayed bodies |

The generic journal can restore originally absent entries to absence. Current two
production callers first call body(), so both normally have a regular entry.
Untouched and newly computed regular entries are not journaled or cleared.
generated_loop_modifies and loop_modifies_bindings are not reverted.

Callsite audit: CPROVER Harnesses/AllFns use the same shared transformer loop;
PubFns uses the same codegen_items guard for its aggregate model. None returns
before creating a transformer. LLBC also calls run_global_passes: its owned
transformer now starts the same scope for both Harnesses and PubFns. This adds
no LLBC semantics/reachability refactor. These are all run_global_passes callers.

Async audit: GotocCtx::split returns MinimalGotocCtx (owned diagnostic maps/bool)
and an owned SymbolTable. FileDataToWrite holds symbol_table, vtable restrictions,
type/pretty-name maps, paths and bool; no transformer, Body reference, or deferred
MIR callback. The worker serializes only those values. No_codegen also restores.

Type/borrow review: Instance is Copy+Eq+Hash. Journal values are moved, not cloned;
Option<V> preserves absence. Scope exclusively borrows BodyTransformation and
DerefMut reborrows it for reachability/GlobalPasses/GotocCtx. split consumes gcx,
so its transformer borrow ends before the scope drops. LLBC's guard borrows the
owned transformer until its emission returns. Drop mutably borrows disjoint
cache/journal fields. Rust compile/borrow checking remains NOT_RUN.
