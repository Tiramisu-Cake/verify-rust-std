# W13: r1 static compile diagnosis

Task `task90b7e5bd7f7dcecc00e7009196a466a7422f179d`. **No concrete compile defect established in the requested source/stock-tool slice. Historical rustc cause UNKNOWN.** Registration presence is established statically; successful macro expansion, Rust type/borrow checking and compilation are not established. Proposed repair **NOT_APPLIED**; source/control unchanged; proof credit NONE.

Pinned identities: S = `9fd558c9dab5ec26abdb1226eb5f2b9cd9ffbff6`, O = `97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a`, K = `0aac16ef62da9e9d5645782d458593e5d78143ba`, C = `2ecf5e839f898f6bb1cd96edd6cc6bf677acb4c8`. Paths and line numbers below are relative to the named commit. `SOURCE-CFG-MAP.json` binds each cited source/tool file to its full commit, Git blob, SHA256 and exact line excerpts. `PROVENANCE.json` binds the task and reused package inputs.

The task/coordinator reports run44284869572/attempt1: compile FAILED after 27.6s, cfg gate passed, zero roots, `Found 1 compilation errors`, stdout preview omitted 16235 bytes. These are reported inputs, not independently recovered diagnostics. No rustc code, primary span, expansion backtrace or error text is available here. Neither an expected error below nor a source-local observation reconstructs that historical error. Review e40ac8e8dd approved static registration lookup, not compilation.

## Established source facts

All 11 requested roots share `kani + kani_smallsort_sorting + kani_smallsort_controls + kani_smallsort_s2_assumed`. C:`ch8-s1-control/runner.py:337–344` fixes the three explicit RUSTFLAGS; `kani` is the Kani compilation cfg. These are the declared effective cfgs, not a recovered compiler invocation. C:`runner.py:322–334` supplies all exact selectors in one command. Removing `controls` does not remove the S2 modules, roots or registration: their module gates use `kani && sorting && s2_assumed`. The six negative roots themselves have no additional controls gate. All are active under the issued configuration.

S:`library/core/src/slice/sort/shared/smallsort.rs:998–1000` gates `verify` by `kani`; `verify.rs:83–98` enables the sorting model and all three S2 modules. `sorting_s2_span` and the S2 attributes on sort8/insert_tail/merge have matching gates. There is no active consumer/inactive span-provider mismatch in this configuration. Ancestors through core → slice → sort → shared → smallsort are present; `fn_traits` is enabled by `kani && sorting` in `library/core/src/lib.rs:164`.

O→S changes only `library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs`: **13 appended lines**, original prefix byte-identical. New PFC attribute line168 and harness lines170–176 register sort8 for both general32 consumers (attributes lines54/155). Sort8's contract/body, span, imports and disjoint helper are byte-identical to O. The old missing sort8 registration in the reused provider slice is a source-local deficiency addressed by r1, not an established cause of the r1 failure. Registering the extra harness can still expose errors while Rust compiles crate items even though the harness is not among the 11 executed selectors.

## sort8 contract and types

S:`library/core/src/slice/sort/shared/smallsort.rs:770–778` declares:

| Component | Effective expression/type and static assessment |
|---|---|
| Signature | `T: FreezeMarker`, `F: FnMut(&T,&T)->bool`; three `*mut T` arguments and `&mut F`; return `()` |
| requires | Readable source `*const [T]` via mutable-to-const pointer coercion; writable destination/scratch `*mut [T]`; all three pairwise disjointness checks for length8. Each operand returns bool. |
| modifies | Exactly destination8 and scratch8, each `*mut [T]`. No source or comparator-state write permission is added. |
| ensures | `|_| !active::<T,F>() || post::<T,F>(old(capture::<T,F>(v_base,8)),dst,8)`: closure consumes `&()` as inferred result argument and returns bool. `old` is bare, one argument, not nested. |
| pre-state | `capture` returns owned `Snapshot`, not a pointer/reference. Snapshot has `Clone, Copy` (`sorting_model.rs:64–70`). No extra Clone/Copy bound on T or F follows. |
| captures | Source/destination raw pointers are Copy. Predicate instantiations mention T/F as types, not a captured comparator value. Original body uses `&mut F`; generated wrappers may borrow/move that reference, whose compiler validation remains unrun. |

`merge_contract_regions_disjoint<T>` is a local free function at S:`smallsort.rs:858–866`, cfg `kani`, signature `(*const T,*mut T,usize)->bool`. Sort8's first arguments `v_base` and `dst` can coerce from `*mut T` to `*const T`. It requires no import in the same module, and does not depend on controls/sorting/s2. It checks multiplication overflow, zero size, distinct allocations or sufficient address distance. Its presence proves neither memory validity nor a verified provenance theorem. `ub_checks.rs:245–250` reexports the Kani predicates; K:`library/kani_core/src/mem.rs:35,73,117` accepts the corresponding mutable slice/const slice/const element pointers.

S:`.../verify/sorting_s2_span.rs:5–53` supplies `active()->bool`, `capture(*const T,usize)->Snapshot`, `post(Snapshot,*const T,usize)->bool`, `ordered(*const T,usize)->bool`. The public-in-smallsort facade has no per-function cfg and no extra T/F bounds. Both the generic default and `u8/KeyLess<u8>` specialization are compiled. At the registration instantiation the latter is selected; at other instantiations the default returns inactive, a non-reading invalid snapshot, and true post/order. An inactive specialization is a value/model choice, not a declaration removed by cfg. The actual u8 post reads destination; the capture reads source. Destination/scratch remain MaybeUninit storage until the runtime body initializes them; the registration does not read their values.

At S:`.../verify/sorting_s2_batch.rs:170–176`, `src: [u8;8]` fixes T=u8; `dst` and `scratch` are `[MaybeUninit<u8>;8]` with casts inferred as `*mut u8`; `&mut KeyLess::<u8>::new()` fixes F=KeyLess<u8>. The call has four arguments in the declared order and returns `()`. `KeyLess<u8>` supplies `FnOnce/FnMut` with bool output (`sorting_model.rs:45–60`), and u8 satisfies the existing FreezeMarker blanket implementation (`shared/mod.rs:11–13`). No concrete arity, return, generic-bound or pointer-type mismatch was located by this inspection. This is not a Rust compiler result or proof of the unsafe preconditions.

## What stock0aac actually generates

K:`library/kani_macros/src/sysroot/contracts/initialize.rs:60–69,93–110` parses requires as an expression, ensures as ExprClosure, modifies as expressions separated at top-level commas. The commas inside `slice_from_raw_parts_mut(dst,8)` are inside token groups. The inspected syntax fits these shapes.

K:`.../shared.rs:138–158,195–254` recognizes bare `old(...)`, recursively traverses the closure, replaces it with a remember variable and emits `(capture::<T,F>(v_base,8)).clone()` in a clause bracket. **The outer postcondition's `!active || ...` does not guard this lifted evaluation.** Safety therefore depends on requires plus the non-reading inactive implementation; both are present in this slice. `split_for_remembers` recognizes bracketed preconditions (`shared.rs:46–89`). Check, replacement and assert modes insert remembers after their assumed/asserted requires (`check.rs:33–54`, `replace.rs:114–129`, `assert.rs:74–93`). The post is passed through `apply_closure` with `&result`; K:`library/kani_core/src/lib.rs:693` expects `Fn(&T)->bool`, here `Fn(&())->bool`. Snapshot is Copy and the predicates do not mutate closure captures, so no concrete Fn/FnMut mismatch is established.

Check mode builds a modifies wrapper plus a unit result (`check.rs:84–102,135–153`); replacement mode creates `any_modifies::<()>` by result type inference, writes the two modifies regions and assumes the post (`replace.rs:20–35,131–151`); assert mode wraps the actual unit-returning body. `bootstrap.rs:41–103` emits all modes, using FnOnce marker helpers and match arms. The choice of a runtime mode does not exempt other generated closures from Rust checking. No actual expansion, type-check, borrow-check or MIR was generated in this task.

K:`.../mod.rs:572–586` adds reset/init calls and the stringified PFC target to the registration harness. K:`kani-compiler/src/kani_middle/mod.rs:83–128` collects registration targets over crate items and checks stub targets against that set; it does not establish that a registered contract proof passed. `attributes.rs:622–681` additionally checks that PFC/stub targets have contracts. The existing CFG-PFC-MAP is a registration-provider slice, not this compiler's validation of the entire crate.

## Ranked unresolved hypotheses and discriminators

Ranking is investigation priority after the static exclusions, not a probability estimate. **Established r1 compile defects: none located in scope.**

| Rank | Concrete hypothesis | Static status | Future distinguishing retained result |
|---|---|---|---|
| 1 | Rust rejects a generated sort8/insert_tail/merge contract closure, capture, result or write-set expression | Open; generated modes and lifted old are real dependencies, but no violating type/capture established | Complete primary error plus notes and macro expansion provenance naming these clauses; e.g. E0308/E0277/E050x/E0525 only if actually emitted. Record inferred/expected types and closure spans. |
| 2 | The new registration call has an inference/trait error, or its PFC expansion's reset/init call fails | Weak: source constrains u8/KeyLess and stock helpers are defined; no source mismatch found | Primary span at batch:168–175 or expansion thereof, actual error code/types. A retained E0282/E0308 at a cast would justify considering the explicit-type proposal below. |
| 3 | Error belongs to another compiled sorting/control/ordinary crate item or a compiler/tool stage outside this slice | Open; all crate items, including unselected harnesses, can participate before root execution | Complete diagnostic names another item/file or an ICE/tool stage; retain stage and original exit. This report is not a whole-core audit. |
| 4 | Missing span/disjoint provider or missing sort8 PFC under effective cfg | Contradicted for pinned source under declared cfg; runtime input/invocation binding still not recovered | An actual E0425/E0433 or stock missing-PFC message must be retained with exact source/tool/config/argv identities. Reconcile drift rather than infer this cause from zero roots. |

An unchanged exact-tuple future compile with original exit0, complete diagnostic retention and a valid initial export/11 exact selected roots would establish that future compilation succeeded; it would not retroactively identify the old failure. A failure with a retained primary error identifies that future failure only. No run is requested or authorized by this report.

## Minimal conditional proposal — NOT_APPLIED

There is no evidence-backed semantic repair to prescribe yet. If a future retained diagnostic specifically identifies inference at the new registration call, the smallest explicit-type spelling to consider is the following **diagnostic proposal**, not an established fix. It preserves the intended type instance, contracts, summaries and all existing roots. It will not repair a generated-contract error. No source candidate was created.

```diff
--- a/library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs
+++ b/library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs
@@ -174,2 +174,2 @@
-    unsafe { sort8_stable(src.as_mut_ptr(),dst.as_mut_ptr().cast(),
-        scratch.as_mut_ptr().cast(),&mut KeyLess::<u8>::new()) };
+    unsafe { sort8_stable::<u8,KeyLess<u8>>(src.as_mut_ptr(),dst.as_mut_ptr().cast::<u8>(),
+        scratch.as_mut_ptr().cast::<u8>(),&mut KeyLess::<u8>::new()) };
```

The justified immediate follow-up is W11's separately owned diagnostic retention work, not speculative source mutation. Future retained evidence must include complete compiler error records (message/code/level, primary and secondary spans, rendered text and expansion/notes), source/tool/tree/request hashes, actual argv/env cfgs, stage, original exit/signal, and independent completeness/truncation status. Diagnostic retention must work even when the display preview omits bytes. W11 owns implementation and service error-path checks; its files are untouched here.

Only pinned Git reads, source-byte comparisons and small inline Python static assertions were used. The 12 source identity hashes, 11 root bindings, shared cfg, exact control request bytes, and 13-line prefix-preserving delta matched. Compiler/Cargo/Kani/CBMC/full runner/CI/subagents/push/PR/ledger/reservation/budget actions: zero. B1/B2, summary qualification and independently established proof credit remain NONE/NOT_ESTABLISHED. Item1 28/28, item2 provisional10/14, total38/42 are unchanged reported accounting; r1 charging is owner-only. Completion reason: all authorized static/report work delivered; missing historical diagnostic is an uncertainty, not a reason to abandon the static task.
