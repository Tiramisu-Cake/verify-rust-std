# Exact stock source trace — W13

**Result:** actual R3 cause UNKNOWN. A concrete, source-supported wrong-body path exists for ordinary stubs of contracted functions. It has higher diagnostic priority than an unobserved `old()`/MIR-loss hypothesis. Nothing here is observed macro expansion, MIR, native verification, or a repair.

## Citation convention and identities

`T:path:Lx-Ly` means exact Git object at stock tool **0aac16ef62da9e9d5645782d458593e5d78143ba**, repository `/root/kani-ch8-s2-r3-final-w13`. `S:` means source **478dbf10d3fccd1119f4de7ac596c96d6dbe8ade**, repository `/root/verify-rust-std-ch8-s2-r3-w13`; `A:` means accepted S1 **99e8456d200fff1299ee5756279cddb23921dc65** there. Full paths below are repository relative; line ranges are inclusive. PROVENANCE.json binds whole-file SHA256/Git blobs. Changed control HEAD is not used as stock tool source.

For readability, `M` = `library/kani_macros/src/sysroot/contracts/`; `C` = `kani-compiler/src/kani_middle/`; `F` = `library/core/src/slice/sort/shared/smallsort.rs`; `V` = `library/core/src/slice/sort/shared/smallsort/verify/`. These abbreviations are only citations, not token-path theories.

## 1. Attribute entry, state, naming, and placement

- `T:library/kani_macros/src/lib.rs:19-23,363-385,434-436,460-466`: sysroot selects `sysroot as attr_impl`; the exported requires/ensures/modifies delegate there. This trace concerns that intended sysroot implementation, not the regular no-op branch. No assertion about actual expanded tokens is made.
- `T:M/mod.rs:535-545,675-699`: all three attributes use `contract_main`, parse `ImplItemFn`, inspect remaining attributes, construct a handler, dispatch on state. `T:M/initialize.rs:16-47`: any name-value `kanitool::checked_with` marker sets Expanded; otherwise Untouched. Matching checks the internal marker, not the user spelling of `crate::kani::requires`.
- `T:M/initialize.rs:72-89`: `generate_name = |purpose| format!("__kani_{purpose}_{fn_name}")`. For `swap_if_less`, names are exactly `__kani_recursion_check_swap_if_less`, `__kani_check_swap_if_less`, `__kani_replace_swap_if_less`, `__kani_assert_swap_if_less`, `__kani_modifies_swap_if_less`. Neither `old` nor generic arguments nor unsafe status enter name construction. `remember_kani_internal_<hash>` is a different family and cannot satisfy recursion lookup.
- `T:M/bootstrap.rs:18-49`: first attribute creates check, replace, recursion and assert streams unconditionally, and appends all five metadata markers *inside* remaining attribute stack so later expansions see them. It preserves the function signature. `:54-85` emits force-FnOnce, registration and mode helper functions. `:86-104` inserts the four outer named local closures in separate match arms inside the original function body, then original body in `_` arm. The recursion declaration is not conditional on `#[kani::recursion]`.
- `T:M/bootstrap.rs:132-164`: recursion closure wraps a `static mut REENTRY`; its then branch contains a nested **replace** closure, its else branch a nested **check** closure and reentry reset. These nested closures use the same spelling as the standalone match-arm closures but belong to the recursion closure body, not the outer function MIR. They cannot substitute for missing *outer recursion* debug information.
- `T:M/bootstrap.rs:113-128,167-184`: subsequent attributes locate the four generated locals by `is_contract_generated` tags in the match and modify their bodies, including nested recursion check/replace. `T:M/helpers.rs:77-145`: AST lookup scans direct statements and direct match arms; it is distinct from compiler `find_closure`. A structurally missing marker/closure at this point triggers its own panic, not contracts.rs:728. No source branch here selectively skips recursion for an ensures with old.

## 2. Clause/body construction and old-state effects

`T:M/check.rs:84-120,135-153`: Check is a force-FnOnce closure with `let result_kani_internal: () = __kani_modifies_swap_if_less(_wrapper_arg); result_kani_internal`. Wrapper owns the original body statements, with permitted argument redefinitions. Modifies adds the two addresses to `_wrapper_arg` tuple (`:56-79`); it does not rename/move the outer recursion local. Check asserts postconditions after the wrapper result (`:33-54`), and assumes each precondition (`:26-31`). Early returns inside the original function body return from that inner wrapper, then the check postcondition still executes. This concrete function has no explicit `return`; its original body is a single nested unsafe block with implicit unit return (`S:F:463-492`; `A:F:436-465`).

`T:M/replace.rs:20-35,100-151,160-179`: Replace asserts each precondition, computes remembered values, havocs return and modifies locations, then assumes ensures. Result type is unit for swap; argument rebinding and receiver logic do not change its signature. There is no owned receiver here. `T:M/assert.rs:22-57,63-98`: Assert wraps original body in `body_wrapper`, asserts requires and ensures, and does not implement modifies havocking. Its wrapper is another inner body, not the body searched for outer closure names.

`T:M/shared.rs:143-158,195-254` visits the entire ensures closure, recognizes one-segment `old(expr)`, hashes the original expression for a remember identifier, replaces the old expression by that identifier, and emits a bracketed `(expr).clone()` before body execution. It does this syntactically even if the old call occurs on the right of `!enabled || ...`; the remember is not guarded by that boolean at runtime. Inactive `capture` must itself be safe and non-reading. `S:V/sorting_s2_swap.rs:25-32,35-49,54-71` meets that intended model property: generic inactive capture returns invalid without dereferencing; active u8/KeyLess capture reads exactly two initialized bytes. PairSnapshot derives Clone/Copy at lines8-13. No hash suffix is calculated or asserted here; the required recursion name is independent of it.

`T:M/shared.rs:46-89` inserts remembers after recognized precondition statements, including clause-guard blocks. Requires are prepended by subsequent attributes; after all five expansions all five requires precede the snapshot, though their generated evaluation order is reversed relative to declaration order. `T:M/helpers.rs:233-239` brackets clause evaluation in a block with RAII clause-depth guard; this is not an additional outer closure. `T:C/transform/contracts.rs:481-542` computes Check/RecursiveCheck/Assert mode as `mode * (1 - in_contract_clause())` so calls during clause evaluation execute Original. This adjustment happens only **after** mark_unused and cannot rescue a failed name lookup. Replace does not take that runtime clause branch.

## 3. Exact searched body and failure predicate

`T:C/transform/mod.rs:115-123` pass order, compact excerpt:

```rust
transformer.add_pass(queries, FnStubPass::new(&unit.stubs));
transformer.add_pass(queries, ExternFnStubPass::new(&unit.stubs));
transformer.add_pass(queries, FunctionWithContractPass::new(tcx, queries, unit));
```

`T:C/transform/mod.rs:152-179` loads `checked_body(tcx, instance)` once, then feeds each result's **body** to the next pass while passing the **same instance**. `T:C/mod.rs:143-150` checked_body checks tail calls and returns `instance.body()`; the source does not supply this session's actual MIR/debug content. Cache key is the instance.

`T:C/transform/contracts.rs:315-342` pass always enabled. For a FnDef with a contract it chooses mode, optionally checks recursion/Arbitrary cycles, calls `mark_unused(tcx, *def, &body, mode)`, and only then `set_mode`. For generated closure instances it clears bodies whose ClosureDefs were recorded as unused (`:353-362`). Thus this pass's own set_mode/deletion cannot have removed the outer recursion entry before its first lookup in that invocation. AnyModifiesPass follows it; its modifications cannot explain that earlier lookup failure.

`T:C/attributes.rs:319-321` has_contract means CheckedWith exists. `:270-299` reads the five marker symbols. `T:C/transform/contracts.rs:659-667` always executes these lookups in order:

```rust
let recursion_closure = find_closure(tcx, fn_def, body, contract.recursion_check.as_str());
let check_closure = find_closure(tcx, fn_def, body, contract.checked_with.as_str());
let replace_closure = find_closure(tcx, fn_def, body, contract.replaced_with.as_str());
let assert_closure = find_closure(tcx, fn_def, body, contract.asserted_with.as_str());
```

`T:C/transform/contracts.rs:711-733`: searches **only supplied `body.var_debug_info`**, exact string equality; for each matching entry obtains Place type with supplied `body.locals()` or Const operand type and accepts only `RigidTy::Closure`. It does not traverse source scopes, descendant MIR bodies, helper definitions, call graph, or generated attributes. It does not filter by lexical scope id or require one unique match. More than one same-name entry is allowed; the first Closure-typed one wins. If no eligible entry exists it emits at line728, aborts, and cannot continue root execution. A type lookup failure may instead unwrap-panic; that is not this reported diagnostic.

**ESTABLISHED as source logic:** absence means either no exact-name debug entry in that body or all same-name entries have a non-Closure type (subject to successful type access). A closure nested in a different function/closure MIR is not in this search. A wrong supplied body is sufficient even when source generation was correct. Optimization/debuginfo erasure, inlining of mode helpers, closure elimination/rewriting, metadata divergence and an unexpected instantiated body remain **unobserved hypotheses**, not established Rust behavior in this run.

All five modes use this same predicate before choosing unused closures (`:667-695`): Original discards all4; RecursiveCheck keeps recursion; SimpleCheck keeps check; Replace keeps replace; Assert keeps assert. A nonrecursive PFC still requires recursion debug metadata. `T:C/transform/contracts.rs:375-417,569-585` precedence is Check (recursion only if explicit attr), then verified Replace, then Assert unless no-assert-contracts, otherwise Original; no-harness default selects Original. Thus changing no-assert-contracts cannot bypass the first lookup. ROOT-MODE-MAP.json covers all11 exact roots with no-assert-contracts=true.

## 4. A concrete wrong-body route, including an S1 countercontrol

`T:C/transform/stubs.rs:46-55,145-152` resolves an ordinary replacement with original generic args, validates it, and returns replacement body. It does **not** change the instance to the replacement. Combined with the pass loop above, contract-pass sees original FnDef attributes with replacement-body locals/debug info. No guard exempts ordinarily stubbed contracted originals. This is a source-provable conditional incompatibility, not a macro token-path conjecture.

`S:V/sorting_s2_batch.rs:141-148` ordinary `stub(swap_if_less,weak_swap)` in `sort13_weak` supplies an empty generic unsafe fn as the swap body. That source has none of the four generated contract locals or contract attributes. If that original swap instance is visited and body substitution succeeds, recursion lookup uses **original** `__kani_recursion_check_swap_if_less` on **weak_swap** body. No source mechanism creates that name there. This can explain the exact reported failure without old() removal/optimization. Actual traversal, instantiation, debug representation and first failing codegen unit remain UNKNOWN from the allowed observation; no assertion that this *was* run44310254730/1's failing unit.

`S:V/sorting_s2_batch.rs:151-159` `general32_weak` supplies weak_merge for the independently contracted bidirectional_merge, with analogous risk for a different recursion name. `sort8_stable -> diagnostic_sort8` is another important mismatch: S2 adds requires/modifies/old ensures on sort8 itself (`S:F:814-817`), whereas S1 sort8 has no contract (`A:F:764-767`). Thus both general32_assumed and general32_weak can search `__kani_recursion_check_sort8_stable` in diagnostic_sort8 body under original sort8 attrs. Preserving diagnostic_sort8 relation bytes does not make its debug-name family match the newly contracted original. It is an ordinary assumed relation, not PFC qualification (`S:V/sorting_s2_batch.rs:165-188`). This potential independent compile blocker is separate from the reported swap error; do not drop either ordinary assumed relation or weak negative controls to declare a repair.

Crucial countercontrol: **A already contracts swap** via five safety::requires and kani::modifies (`A:F:406-432`). With kani_host, safety rewrites to kani_core::requires (`S:library/contracts/safety/src/lib.rs:12-18`; both A/S `library/contracts/safety/src/kani.rs:28-36`), without wrapping the fn body. S2 selects direct crate::kani requires only in its exact opt-in cfg and adds one old ensures. Therefore the wrong-body mechanism is not inherently new to S2/old(); a comparable ordinary-stub setup on S1 could hit it too. S1 acceptance does not prove that this newly added weak root was present or compiled there.

## 5. S1/S2 contract and cfg comparison

| Factor | A: exact S1 | S: exact S2 | Source inference |
|---|---|---|---|
| a offset | F:406-412 safety::requires | F:406-419 paired cfg branches | checked_mul(size), <=isize::MAX, checked base addition, byte_offset_does_not_wrap preserved |
| b offset | F:413-419 | F:420-433 | same predicate for b |
| allocation | F:420-423 | F:434-441 | same_allocation(base,base.wrapping_add(a)) AND corresponding b preserved |
| a validity | F:424-427 | F:442-449 | can_dereference AND can_write at a preserved |
| b validity | F:428-431 | F:450-457 | can_dereference AND can_write at b preserved |
| frame | F:432 | F:458 | exactly two wrapping_add targets, unchanged |
| ensures | none on this helper | F:459 | !enabled<T,F> OR post(old(capture<T,F>),base,a,b) |
| signature | F:433-436 | F:460-463 | identical unsafe fn<T,F>, raw base, usize indices, &mut F, F:FnMut; implicit unit |
| body | F:437-465 | F:464-492 | identical bytes from opening brace; nested unsafe, no return, same movement operations |

Direct Kani requires and ensures activate only for `all(kani,kani_smallsort_sorting,kani_smallsort_s2_assumed)`. Complementary safety branches retain the exact old predicates. Modifies remains cfg(kani). controls flag only enables control declarations, not this contract stack. NonS2 behavior must remain unchanged in any future remedy. Host selection of the safety implementation is source conditional, not observed expansion evidence. Core kani_lib binding is at `S:library/core/src/lib.rs:357-358`.

Comparable functions distinguish limitations of candidate causes: S1 six trait small_sort bodies already use requires/modifies/old(snapshot) with generic comparator (`S:F:174-190` is one example inherited from A); not proof that arbitrary unsafe raw-pointer helpers preserve debug info. S2 insert_tail has generic unsafe body, early return, modifies and old(capture) (`S:F:634-701`); bidirectional_merge additionally has Freeze bound, disjoint initialized source/destination and old(capture) (`S:F:925-940`). They share generation machinery but different frames/body nesting and ordinary stubs. Their compilation behavior is UNKNOWN; source similarity is not a passing control. insertion_sort_shift_left (S:F:706-737) has modifies but no old ensures and safe outer fn, so it is not a controlled old-only comparison.

## 6. Providers, root selection and limits

`T:C/codegen_units.rs:86-96,244-293,357-393` collects harness declarations, selects filters/exactness, then groups by both ordinary stub map and PFC/verified usages. Distinct modes do not merge merely because the runner labels them Original. `T:C/attributes.rs:622-681` validates target contract presence, not proof success, and cannot validate per-instance sorting qualification. All active provider declarations are inventoried in ROOT-MODE-MAP; helper_contracts.rs bytes are identical A/S. Existing arbitrary_less PFCs have different comparator types from KeyLess, so do not qualify S2 pair postconditions.

`T:C/reachability.rs:49-74,141-178` transforms visited instances before collecting their outgoing MIR edges. A source call can be optimized/instantiated differently; all per-instance reachability is therefore UNKNOWN here. Unselected provider registration does not imply its contract closures were transformed. PFC `init_contracts()` inserted at `T:M/mod.rs:572-580` becomes free(NULL) hook (`T:kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs:792-834`), not eager execution of every registered provider. No evidence justifies attributing this failure to an unselected provider or to the first named verifier row.

No closure-name/MIR dump was read or produced. Sole owner-reported message has no failing unit, mode or instance. Compile21.9s/0roots is compatible with collection-time failure for a weak ordinary-stub root; it does not distinguish it from missing metadata in the original swap body. Path normalization failed as reported; R1 original diagnostic stays UNKNOWN.
