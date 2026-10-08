# OVERNIGHT sort4 route — stock 26.10 and actual dependencies

Static route review only. No source, spec, verifier, or runner was changed for this note; no executable check was run. Target worktree entry was `80d9c0c318f71f49c3531883f7953883cb04c2f4`; reviewed tool source pin is VeriFast `f76012fb518703b1d98e243ac4f487f16877cfcb`; std/upstream is `cd371e035c7e573760c43bf934d53e8118ee3e7d`.

## Route and dependency order

Actual [`sort4_stable`](../../library/core/src/slice/sort/shared/smallsort.rs) has five `FnMut(&T,&T)->bool` calls, eight `select_unpredictable` calls, pointer adds/reference formation, and four `copy_nonoverlapping` calls. Its output is four initialized representations in raw caller storage; actual caller paths normally provide `MaybeUninit` scratch. Nothing in the pure index/SWO proofs verifies this Rust body.

The dependency order is:

1. Accept the stock + narrow `ManuallyDrop::new` CFG profile and independently revalidate the constructor/as-mut-pointer/typed-intrinsic/pointer-drop components on 26.10. The nearby candidate under `overnight-s6` is explicitly experimental. It only treats pointer values and exact pointer-payload glue; it does not establish the actual generic `select_unpredictable` body. The prior actual helper trace still stops at nominal `DropOnPanic<*const Element>::own` on `mem::forget`; `assume_init`/`transmute_neo`, full normal/unwind/leak gates, and actual call linkage remain prerequisites. Do not redirect the helper on component-only evidence.
2. Separately isolate the first actual callback call. This can proceed independently of selection and copying, and is the most useful first sort4 diagnostic after profile setup. A successful one-call probe would qualify neither all five calls nor sort4.
3. Capture actual sort4's full typed NORMAL and readonly MIR/CFG on the exact 26.10 compiler, including all callback normal/unwind edges, selection types, pointer operations, local drops, and the four copies. Then prove the exact body in layers: reference/callback resources; selected complete pointer values; copy into uninitialized scratch; composition and complete function posts.
4. Bind actual selected pointers/copy destinations to logical indices, then connect the separately checked finite index/SWO theorem. Safety and functionality remain separate claims.

## Smallest honest safety/resource contract

Use the adopted full four-slot source/destination byte-range separation as the sufficient caller domain. It covers both each individual source/destination copy and preservation of not-yet-copied source cells after earlier writes. Require four in-bounds, aligned, live, provenance-carrying logical slots at each base, initialized valid source `T`, and four writable destination slots with no discarded live ownership obligation (actual MaybeUninit scratch is the intended application). For non-ZST, the full byte ranges are disjoint. Do not infer permission or provenance from numeric address equality. A caller must establish the full domain; it is not an axiom supplied by the helper.

Before c5, the function has made no sort4 writes. Each callback can have legal `FnMut` and `UnsafeCell` effects. Therefore normal and unwind posts must return the callback's **current** state/resources and the current valid source state, not blindly restore the pre-call `F` or values. The callback may not invalidate the source, output storage, allocation/provenance, or outstanding permissions. Its accessible frame and output storage need a precise separation/resource relation. On every direct callback panic, recover or explicitly return the full current source/callback/frame resources and all reference/lifetime bookkeeping; no sort4 output write has occurred. The adopted contract lists all five panic sites separately. No `Freeze`, `Copy`, comparator-purity, or ordering restriction belongs in this safety contract.

On normal return, the actual index network writes each source occurrence once to a distinct destination index. The memory post must express the source's one logical ownership sequence plus four destination **shadow/raw representations**, not two independent `T.own` sequences. It must preserve padding as bytes without requiring padding to be initialized. Destination writes must account for prior contents; silently returning an overwritten owner is unsound, and silently discarding it is an unaccounted resource loss. The existing stock `copy_nonoverlapping<T>` specification requires initialized typed `dst[..count]`, so it does not model actual uninitialized MaybeUninit scratch. A new operation model or a separately checked primitive bridge must consume source access and writable raw destination access, preserve source ownership, produce an optional/shadow destination representation, and state alignment, nonoverlap, validity, padding, provenance, and overwrite behavior. It must never manufacture an initialized `T` or a second droppable owner from copied bits.

This contract is deliberately caller-oriented and sufficient for actual separated scratch use. If the target claim is the entire unsafe function under only its current prose requirement “valid for four writes,” destination storage that already contains live owned `T` values needs an explicit overwrite/leak disposition. Do not call uninitialized-only scratch a theorem for every initialized destination state.

## First independent callback fixture

A useful first diagnostic is one source-exact generic call with the actual shape `F: FnMut(&T, &T) -> bool`, two initialized logical source cells, a mutable callback resource, and no selection, `MaybeUninit`, copies, or body-local guard. Require the actual `FnMut::call_mut` in MIR. Its full normal post returns the Boolean, current `F`, source cells/current valid values, thread and frame. Its direct unwind post returns current `F`, both current source resources, thread/frame, and every borrow/lifetime token needed by the caller; it does not assert callback rollback. Add a false Boolean/post control and a callback that changes permitted interior state before normal return and before panic, so the contract cannot accidentally require purity.

This is a capability diagnostic with likely early barriers, not a promised PASS. On pinned 26.10 the stock `FnMut::call_mut` contract requires `Args.own`; the parser generates opaque `std_tuple_2_` ownership and the prelude has no field-to-own close/open route. Historical 26.09 attempts to append another tuple predicate collided or found no predicate instance; a real exact tuple model needs its own reviewed parser support and regressions. The compiler also exports `for<'a,'b> FnOnce<(&'a T,&'b T)>::Output = bool`; 26.10's projection registration still filters nonempty `bound_regions`. The old experimental HRTB patch addresses only a narrowly checked, two-region same-`F`/same-`T` Boolean projection and needs a fresh 26.10 adaptation, source-built pin, and nonmatching controls. It is not a callback proof.

Finally, VeriFast's direct `UnwindAction::Continue` becomes an unwinding return. Normal-path trailing ghost recovery does not execute on that edge. Prior insertion evidence also found that closing two reference accesses recovers only half the lifetime token; ending the lifetime and regaining full `T.own` needs the other reserved half and borrow-end resources. The probe must either prove an existing sound recovery route on both exits or stop at this exact boundary. It cannot return only abstract borrow debt while advertising the full current cells, nor use an assumed bridge. This is why callback is a useful independent early probe: it can expose tuple/type/unwind blockers before the larger actual helper/copy body is loaded.

## Connecting the pure components to Rust

The finite index theorem accepts arbitrary five Boolean answers and proves a permutation of occurrence IDs `0..3`; it assumes no comparator consistency. The exact selected-index expressions are source-bound in the historical pure component. The fixed strict-weak-order/rank bridge and pure network composition separately prove sorted stable order under a fixed SWO, faithful answers, and preserved keys/values. These are mathematical components only. To apply them, the Rust proof must establish that each actual selected pointer still denotes the corresponding logical source occurrence, each intrinsic returns the selected complete modeled pointer, callback answers equal the same relation on the relevant keys, and those keys are preserved. Do not convert that functional premise into a safety restriction.

A stateful or interior-mutating callback can return inconsistent Boolean results and still be safe; then the index permutation theorem remains relevant, but sortedness/stability does not follow. Stable equality handling is an occurrence-order property from the pure theorem, not pointer-address ordering. Rebind source-expression/call-site guards to the cd371e03 body before using old pure evidence as an actual-source link; a matching body text alone does not prove MIR, callee, resource, or callback correspondence.

## Generic and ZST boundary

Do not infer the unrestricted generic theorem from i32/Copy, nonpanicking callbacks, positive stride, fieldless layout, or nonzero-size experiments. Keep `T` symbolic with arbitrary valid layout, no `Copy`/`Freeze` bound, generic Drop behavior, and all valid callback effects in the safety target. Padding may be uninitialized.

For a ZST, four logical occurrences remain distinct although `.add(i)` can retain the same numerical address and all four byte regions are empty. Alignment, nonnull/reference validity, provenance, legal add operations, and one ownership occurrence per logical element still matter. Empty byte-range separation does not create four independently droppable owners or prove that the VeriFast heap model can distinguish cells at a zero stride. The pure index and SWO proofs operate on logical IDs and therefore cover this mathematical case, but the actual pointer/reference/copy resource bridge does not. The accepted merge geometry at `b0af5613` is constrained to its recorded scalar/index/provenance premises and its public callers may take ZST shortcuts; it does not prove standalone generic sort4 or its direct ZST branch. Keep generic/ZST as an explicit open gate or report a narrowly partial profile without calling the full target closed.

## Review conclusion

The callback-first fixture is the smallest independent next experiment once the common 26.10 profile is available; it should be preceded by tuple/HRTB source review and must retain both panic and normal full-resource posts. The actual helper remains a hard integration dependency, while `copy_nonoverlapping` into MaybeUninit is a separate missing memory-operation model. The pure permutation/SWO result is ready only as the final mathematical layer after actual pointer and callback correspondence. None of the static or historical components alone establishes actual `sort4_stable` safety, generic/ZST validity, or a combined accepted profile.

## O9 correction: stock scratch destination already supported

The earlier static reading of `dst[..count] |-> _` as an initialized
requirement was incorrect. O9 run37707055478/proof0781cdbd M1 confirms
uninitialized optional destination is accepted with full rawrepresentation
post. Stock `verifast1.ml:6925` deliberately lowers DummyPat to `array_`;
no new memory primitive is required for this isolated copy boundary. This
supersedes the missing-uninitialized-destination assertion above, while
keeping actual wrapper linkage, complete fourcopy geometry, padding,
provenance, ownership/SWO composition and generic/ZST gates open.
