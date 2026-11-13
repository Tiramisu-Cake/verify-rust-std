# Required private state: STOP before implementation

worker15, 2026-11-13; exact source `ee2695e5a2c4c2d8ead7a511e0f3f6f2a9a95677`.
No correct total, extent-specific bounded predicate has been established in this preparation.
This is the STOP required by task §2, not a claim that such a predicate is impossible.
Production lookup and instrumentation are unchanged. UNKNOWN remains unresolved.

## Existing facts and the missing binding

Paths refer to the isolated Kani clone named in INPUTS.json. Abbreviated compiler paths
omit the `kani-compiler/src/` prefix; library paths retain their full prefix.

| Source | Established fact | Insufficient inference |
| --- | --- | --- |
| `codegen_cprover_gotoc/codegen/contract.rs:32–51, 102–124` | `find_modifies` resolves the particular wrapper through the contract's closure metadata. | The supplied `items` is not a write set or an extent-specific effect set. |
| `kani_middle/transform/mod.rs:96–114, 171–204` | Cache entries hold transformed `Body` plus changed flag; additional maps describe loop modifies. | Changed is not private-state-written. There is no existing per-contract shadow effect fact here. |
| `kani_middle/transform/check_uninit/delayed_ub/mod.rs:150–177` | Delayed instrumentation updates the same cache after local passes. | Recording only local-pass effects would miss later injected operations. |
| `kani_middle/reachability.rs:316–375, 547–562` | Collection includes direct calls, address-taken functions and vtable items; graph nodes/edges are private. | Rooted collection reachability does not establish an executed indirect call from that wrapper. |
| `kani_middle/points_to/points_to_analysis.rs:355–382` | `resolve_call(Ty)` resolves FnDef, rejects function pointers, virtual calls and some bodyless instances. | A failed resolution cannot become NOT_REQUIRED or be replaced by any matching reachable helper. |
| `kani_middle/transform/contracts.rs:477–548` | Check/Assert mode selection depends on runtime `in_contract_clause()`. | A context-free scan of all bodies/closures cannot itself establish clause versus body execution. |

The function-pointer paths already have Unsupported instrumentation (see `resolve_call` and
its callers). This is **not** evidence of a newly supported path or an unguarded shadow write.
To use that cut to establish NOT_REQUIRED, a predicate would have to bind the actual transformed
cut, control flow and call site. Merely observing an error returned by `resolve_call` is insufficient.

## Coverage that a replacement fact must establish

`kani_middle/transform/check_uninit/mod.rs` maps these operations to actual model calls:

| Operations | Emission / actual private effect |
| --- | --- |
| Set, SetRef, SetStorage, SetSliceChunk, CreateUnion | `build_set:457` chooses sized/slice/str setters, including union field layouts. A helper name alone overcounts: setters in `library/kani_core/src/mem_init.rs:267–377` return without a write for zero layout. |
| Copy | `build_copy:659` → CopyInitStateModel. Its zero-layout branch must also be accounted for. |
| AssignUnion | `build_assign_union:764` → CopyInitStateSingleModel with typed transfer mask. |
| BeginArgumentTransfer | Special emission at `mod.rs:175–197` → BeginArgumentTransferModel. Writes protocol fields even without a payload-byte write. |
| StoreArgument, LoadArgument | `build_argument_operation:691` → StoreArgumentModel / LoadArgumentModel. Store snapshots a witness; Load consumes protocol and may update tracked location/value. A global zero-size rule would be wrong for protocol fields. |
| Immutable seed | `context/immutable_allocations.rs:199–313` patches normal completions of the reset function, after `handle_check_contract` (`compiler_interface.rs:192,204`). Seed presence globally is not a wrapper write. |
| Reset and clause bookkeeping | Reset at harness entry and enter/exit-clause counter writes outside this extent do not independently require a private assigns target. They must not contaminate a fact from another context/root. |
| Indirect/transitive helpers | Need an actual call/effect chain beginning at this transformed modifies-wrapper, with call-site/context binding. The same helper merely collected for clauses or another root is not such a chain. |

The public state marker cannot be the sole source of the required-state fact: the diagnostic
must also work when that marker is missing. Scanning accesses to its emitted symbol has the
same circularity for the missing-symbol case.

## Candidate mechanisms considered and rejected for this patch

1. `uninit && !symbol`, or “any shadow helper in items”: false positives for off-extent
   reset/clauses/other roots; neither establishes condition 3 in the task.
2. Wrapper's own injected calls only: loses transitive helper writes and delayed effects.
3. DFS over final transformed direct callees: useful positive witnesses, but not a total
   NOT_REQUIRED proof when resolution/context/cuts are unknown; helper presence also needs
   zero-layout/no-write handling. No new global points-to or path analysis was introduced.
4. A pass-recorded per-body effect bit: needs separate writer/read/no-op effects, delayed-pass
   updates and composition from the wrapper through actual callees and clause context.
   A bit alone does not supply that composition.

**Concrete handoff:** establish/review a small effect provenance contract that (a) records actual
local and delayed write effects independently of marker lookup, (b) binds their composition to
the transformed wrapper's call sites, including existing cuts/no-write cases, and (c) retains
UNKNOWN when a binding is unavailable. Specify how UNKNOWN is resolved without a blanket
missing-state error. This preparation does not authorize a new intermodule analysis framework.
Only after that fact is justified should the resolver/diagnostic patch be implemented.

Static/source findings above are not a typecheck, emitted-model inventory or verifier result.
