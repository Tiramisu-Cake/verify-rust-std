# KANI3300 M0 — bounded implementation contract (no implementation authorized)
Base `6134e42dd1c65dc980336e7d9455aba02d423edf`; B1I-A production = `dc5f5a406749a73f1c3192e0b5338441e79508bb`.
D0 diagnostic `5eec235e3` and baseline `a0a2386001` are evidence inputs, never replacement production bases.
Existing B1I-A guards/entry loads and Item true/false controls are dependencies; Shim/Err/DST/hook qualification remains open.

1. M1 first reproduces the immutable RHS gap using the unchanged two D0 legal harnesses plus retained direct/helper None negatives.
2. Frontend descriptor API: resolve_const_referent -> origin alternatives + offsets/extent + allocation mask/mutability/freeze/relocations;
   preserve actual byte Option values before lowering, and distinguish pointer carrier from target allocation. Unknown is explicit failure.
3. `kani_middle/points_to/points_to_graph.rs`: add compiler-local Anonymous node; side table carries descriptor/range identities.
4. `points_to_analysis.rs`: both constant operand/deref successors propagate anonymous origins through assignments, offsets and helper calls.
5. `check_uninit/delayed_ub/{initial_target_visitor,mod,instrumentation_visitor}.rs`: seed both operands, qualify all origin alternatives,
   preserve mutable destination effects and entry loads; unknown/relevance holes diagnose rather than positive type-based bypass.
6. `codegen_cprover_gotoc/context/goto_ctx.rs`: per-unit canonical immutable registry and requested AllocId -> emitted symbol binding.
7. `codegen/operand.rs`: capture referent mask before unwrap_or(0), validate carrier relocations/emitted byte layout,
   register/compare full descriptors at alloc_map insertion AND reuse. No incompatible coalescing and no trust in hardcoded const shortcut.
8. `compiler_interface.rs::codegen_items`: after item/contract codegen closure, before export, finalize registry and seed reset completions.
   Proposed finalize_immutable_seeds emits inline guarded assignments in the marked reset function after all resets, before return;
   use actual symbol address and existing private state marker. Preserve nondet selection, argument-buffer resets and every reset site.
9. `library/kani_core/src/mem_init.rs` + `kani_middle/kani_functions.rs`: retain reset model identity/fields; add a marker only if
   completion placement cannot be found structurally. No runtime bitmap, new ABI, new assume, or per-reference seeding.
10. `codegen/contract.rs`: inspect private marker/DFCC behavior; change only if exact new seed code needs private-state registration.
11. Proposed diagnostic record schema: source/compiler/target identities, carrier MIR operand, AllocId+offset+extent, Some/None mask,
    mutability/freeze justification, relocation widths/ranges, emitted symbol/layout, reuse equivalence, reset site and property join.
    Store bounded source-bound records, explicit UNKNOWN/missing coverage; extend curated sidecars only in separately authorized work.
12. M1 STOP/review gate: exact mask+symbol+post-reset runtime binding, legal pass and reached hole failure on either operand.
    A disappeared raw_eq, extra failure, Unsupported hiding a required flat path, ICE or incomplete binding rejects gate.
13. M2 follows accepted M1: qualify existing normal-return setters and actual false transfers, padding, original parameter indices,
    return0, plain/seeded Item, hooks/private DFCC/abnormal edges. D0 does not authorize a new temporary setter.
14. M2 adds a setter only for a separately reproduced gap with proved callee initialization and matching normal destination;
    shadow-carrying returns transfer actual false. New ABI forms remain guarded, not silently paired.
15. M3 follows accepted M1/M2 and C1: dynamic immutable/local choices for both operands, coalescing, nonzero offsets/subranges,
    overlap/overwrite/reset/reuse, flat array/slice whole-copy, empty/nonempty/ZST, singleton/shared AB/BA and PFC legal/frame/clause.
16. C1 owner 15 activates controls only on separate assignment; shared interface changes return to model owner 14, no overlapping writes.
17. Per stage: static/preflight -> exact target and distinguishing controls -> review/coordinate targeted CI -> STOP; final full gate later.
    All future CI belongs to coordinator; current Cloud $0 and no dispatch/local compiler/verifier. Current outcomes remain NOT_RUN.
18. Release requires reached pre-effect boundaries for unsupported heap/foreign/realloc, DST, ordinary union constants and unpaired calls;
    if unavailable, record exact blocker. Do not shift such work to maintainer or claim exclusion by documentation alone.
19. No B3/G1/B4/T1b/general cache fix, fixture activation, source-clone changes, workflows, goldens or PR work in M0.
20. M0 design acceptance requires bounded independent Luna High review and resolution of concrete soundness findings.
