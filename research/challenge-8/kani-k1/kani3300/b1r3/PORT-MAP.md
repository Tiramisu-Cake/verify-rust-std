# B1I/B1I-A → standalone port map

Read-only sources: production `cdb439b0a4c36e9e595019895ab803230f332941`, fixtures `dc5f5a406749a73f1c3192e0b5338441e79508bb`, final rebindings `6134e42dd1c65dc980336e7d9455aba02d423edf` in `/root/kani-fix-3300-p1b1`; research `b1i` @ `54b7b7fbc4`, `b1ia` @ `e3e1125988` in g0. No whole commit cherry-pick.

| Source / decision | Standalone application | Expected / observed |
|---|---|---|
| Common fallible resolver and actual generated-body check | Adapted into points_to resolver, local Call dispatch, points-to call admission and defensive body lookup. Foreign/intrinsic branches precede body query. | source contract / NOT_RUN |
| Fallible intrinsic seed collection | `.ok()` on FnDef resolution, existing intrinsic-kind whitelist retained; prior targets preserved. RawEq additions excluded. | source contract / NOT_RUN |
| Local diagnostic ownership | Delayed guard removed; Call operands visited once, resolver Err and shim guard break to common flush. | source contract / NOT_RUN |
| Shim caller/callee transfer policy | Reject union-containing or unknown by-value arguments/return storage on caller and entry; inspect tuple/array/ADT/closure captures without adding new shadow transfers. Non-shadow MIR shims continue. | source contract / NOT_RUN |
| Direct, FnPtr, Virtual, erased/wrapped/global, pending-read, entry initialized/partial pairs | Start from final standalone d5f072f2b inputs/goldens; custom MIR gets explicit panic=abort. Legacy top-level union argument loads/stores retained. | named goldens / NOT_RUN |
| Fn-trait pointer pair | Rename shim-* to fn-trait-pointer-* and use final 6134e42 diagnostics/comments: FnPtr Unsupported, no bodyless claim. | FnPtr failure expected / NOT_RUN |
| New function-item + drop/closure positive pair | Non-shadow Fn::call on function item and FnOnce closure consuming DropCounter; scalar/count assertions. | SUCCESS expected; actual kind/body/properties NOT_RUN |
| tuple-maybe-uninit plain/seeded (6134e42) | EXCLUDED: Part 1 observed tuple-layout Unsupported does not establish genuine shim argument guard. Standalone does not add MU conversion/compound shadow model to run it. Input retained at pinned read-only source, not in candidate tests. | historical source-reported tuple-layout Unsupported only; standalone NOT_RUN |
| item-return-uninit plain/seeded (6134e42) | EXCLUDED: source returns MaybeUninit through genuine Item then assume_init; Part 1 observed u16 read failure depends on MU/return model absent on base. Do not import negative golden or broaden ordinary Item. | historical source-reported read failure only; standalone NOT_RUN |
| item-return-initialized companions (6134e42) | EXCLUDED for the same absent return0/MU model; not a standalone positive or shim guard control. | standalone NOT_RUN |
| Part 1 transfer signature/count/size, masks, MU/flat storage, Move/reset, return0, raw_eq, library/backend hooks | EXCLUDED in full; base library and models unchanged. | no credit transferred |

## Production hunk rationale

- `points_to/mod.rs`: export resolver in place of old unsupported classifier; one policy shared with local visitor.
- `points_to_analysis.rs`: remove internal expect_resolve/duplicated classification, query actual body, retain foreign/intrinsic models and prior graph on rejection; defensive missing-body return agrees with local diagnostic.
- `initial_target_visitor.rs`: failed resolution is not a seed; successful recognized intrinsic cases unchanged.
- `instrumentation_visitor.rs`: remove duplicate unsupported emission and now-unused locals/imports; local pass owns it without delayed targets.
- `ptr_uninit/mod.rs`: supply tcx/actual instance to the entry guard.
- `uninit_visitor.rs`: instance/tcx state and conservative storage scan serve only shim admission; Call break/flush preserves pending operations; local shared resolver owns rejection. No visit_statement/index fix and no expansion of Item transfer predicate.

## Unexecuted compiler/MIR obligations

Each is a specification, not an executable fixture or branch-coverage result. Use legal pinned MIR only; no new framework and no fabricated source coverage.

1. FnDef resolution Err, distinct from FnPtr, with empty entry/top-level union formal, pending read and prior seed/edges: one target, LoadArgument → Check → one could-not-resolve Unsupported in changed passes. Earlier reachability resolver may fail first; this candidate makes no end-to-end recovery claim and acceptance requiring that recovery is BLOCKED pending separate work.
2. Bodyless generated Shim (actual body=None), LlvmIntrinsic, bodyless nonforeign Item: exact local kind diagnostic after operand checks, prior graph/targets preserved, no body unwrap. Fn::call alone closes none of these.
3. Genuine MIR-backed Shim with direct union argument only and unit destination: caller Unsupported before StoreArgument; entry Unsupported before LoadArgument/fallback blessing. Tuple-MU is not evidence of this branch.
4. Genuine MIR-backed Shim with only union destination: caller/entry Unsupported, no transfer/return handshake. Genuine Item-MU return is not evidence of this branch.
5. Tuple/array/ADT/closure-capture union storage and unknown storage at generated ABI: no bypass; supported non-shadow generated body and ordinary drop/closure controls must remain reachable. Actual kind/body/ABI and reached checks require coordinator binding.

Historical Quick `43199156872` is another model/tree (119/1/2 ignored; raw_eq legal FAIL), not standalone validation. No measured base false SUCCESS and no new independent proof credit.
