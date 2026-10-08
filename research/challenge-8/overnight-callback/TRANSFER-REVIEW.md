# Callback tuple ownership and HRTB transfer review

Review for the pinned VeriFast 26.10 source `f76012fb518703b1d98e243ac4f487f16877cfcb`. The prior tuple-own and FnMut HRTB experiments were written against 26.09 (`809de4596839b739dd999f9e462242c835e3af46`); neither patch is applied here. The authorized overnight phase permits a semantic transfer after its rationale, trust boundary, controls, and self-review are recorded; it does not require a separate owner decision. O5 now witnesses the exact tuple-ownership obligation, so the narrow tuple-2 transfer specified below is ready for implementation and hosted regression. HRTB and unwind recovery remain separate later boundaries.

The inspected old artifacts are [`verifast-tuple-own.patch`](../verifast-tuple-own.patch) (SHA-256 `ff2576f727d13d9dfcd9616a030b72ad0b0a27ce87cc96014af2d2ba42249660`) and [`verifast-fnmut-hrtb.patch`](../verifast-fnmut.patch) (SHA-256 `d90fb7a814b098a6008c4e64c567d2a3798e8f18999d12905425ef17224dbe1f`). The old tuple patch changes only parser-generated `std_tuple_2_` ownership. The new 26.10 transfer is [`verifast-tuple2-own-26.10.patch`](verifast-tuple2-own-26.10.patch) (SHA-256 `84b58b71bfb65ac2bfac1a63d181239001cf0a7ffba3f8bfb5d5b0f1d3a640da`) and additionally requires the exact two-public-field AST shape. The old HRTB patch changes function-predicate collection and pre-call projection registration, with narrow matcher regressions. They address different obligations and must remain separate semantic components.

## Exact obligation and order of diagnosis

At `FnMut::call_mut`, stock `bin/rust/std/lib.rsspec` requires `<Args>.own(t, args)` and returns current `F.own` plus result ownership normally; its unwind contract returns current `F.own` but no `Args.own` or result. For `F: FnMut(&T, &T) -> bool`, rustc's `Args` is a two-reference tuple and its higher-ranked predicate is `for<'a, 'b> <F as FnOnce<(&'a T, &'b T)>>::Output = bool`.

Keep three outcomes distinct in callback evidence:

1. Export/decode or refinement failure is a fixture/profile boundary; it says nothing about tuple ownership or output translation.
2. If full VeriFast stops at the `Args.own` call precondition, the tuple representation/borrow setup is first. Do not claim the Boolean output check was tested.
3. Only when the actual call reaches the associated output comparison and fails to equate `<F as FnOnce<Args>>::Output` to `bool` is HRTB translation the observed next blocker. Later source-cell recovery on unwind is a third, independent obligation.

The callback fixture prepares separate `ref_initialized` resources and a real borrow debt. Its current diagnostic order should be taken from the hosted full log, not inferred from historical insertion runs.

O5 (`37702922138`) supplies that order: NORMAL and readonly exports/decode and refinement are all zero; the named `callback_positive` body executes; the first proof error is the stock `FnMut::call_mut` precondition at `lib.rsspec:47`, `No matching heap chunks: own(std_tuple_2__type_info(...))` for `Args.own`. It occurs at the actual `is_less(&*left, &*right)` call. This establishes tuple argument ownership as the first witnessed blocker. It does not test the associated Boolean output projection or direct-unwind recovery, which must remain open after this component advances.

O10 (`37707814634`) confirms that the transparent tuple-own parser transfer alone is not enough to construct the actual call's argument resource. The exact normal/readonly exports, decodes, and refinement passed; the call site and tuple aggregate are present in decoded MIR. VeriFast still fails at the same `Args.own` clause with the actual value `mk_std_tuple_2_(fn_outcome_result(outcome0), fn_outcome_result(outcome2))`, so the output projection remains untested. The callback fixture has `init_ref_share` resources for its actual borrow values, but did not apply stock `close_ref_own` to package each shared pointee permission as reference `.own`, nor close tuple `.own` before the call. [`CALL-ARGS-OWN-REVIEW.md`](CALL-ARGS-OWN-REVIEW.md) records the fixture-only checked transition and trust boundary for the next hosted replay. The false-post callback also failed at this earlier call and is inconclusive. O10 does not justify HRTB changes.

O7 (`37705052264`) did not reach that proof obligation. The tuple runner stopped during source-profile setup because copying the exact release bundle adds `bin/VERSION` and `bin/libgtksourceview-2.0.so.0` as untracked support files. No tuple fixture, callback proof, or HRTB output check ran in O7. The narrow retry gate now admits only those two paths after comparing them against the extracted pinned release archive; every other untracked path remains an error. Since no post-tuple `FnOnce::Output` failure has been observed, O7 does not warrant an HRTB semantic patch. Retry the tuple transfer first; only a full log that reaches the actual associated-output comparison can justify that next component.

O4 (`37702049156`) is not yet such a full proof log: exports/decode/refinement all returned zero, but `-dump_ast_with_locs` crashed in the optional OCaml AST emitter with `Failure("TODO")` before the target timed header (count zero). The unsupported serializer node is `MergeFractionsStmt`, emitted by the fixture helper's `merge_fractions lifetime_token(k)`; `ocaml_expr_of_ast.of_stmt` explicitly has a TODO case for it. Treat this as a diagnostic-serialization limitation, not a VeriFast callback failure or intended negative. The required proof invocation must omit that flag; any follow-up AST capture is separately optional and non-gating.

## Minimal tuple-2 ownership semantics

The source declaration is the internal tuple carrier `std_tuple_2_<T1, T2>(T1, T2)`. The proposed generated predicate body is exactly the structural ownership meaning:

```text
std_tuple_2__own(t, v) = <T1>.own(t, v.0) &*& <T2>.own(t, v.1)
```

The call's `Args.own` can then be closed from the two actual reference-value ownership chunks produced by the reference expressions. This does not create either reference, prove its referent valid, or discharge either source-cell borrow. It only packages the two tuple fields the stock FnMut spec consumes. The existing one `.own` alias must resolve to this one transparent predicate; do not append a second RSSPEC predicate, add an assumed close/open lemma, or replace the tuple's actual fields with a generic guard.

The narrow parser boundary is the exact internal declaration name and arity `std_tuple_2_` with type parameters `T1,T2`. Other structs and tuple arities retain their current generated opaque ownership. The generated predicate body is checked by VeriFast, but the parser's mapping from this Rust internal tuple layout to fields `.0` and `.1` remains part of the trusted translator/frontend boundary. Avoid introducing layout, address, or representation claims beyond the prelude's tuple declaration.

Required controls before considering the component usable:

- Close and reopen the exact tuple-2 ownership for unrelated generic `T1,T2`, including a non-`Copy`/Drop-bearing value; preserve both field values and both field resources.
- Exercise the exact reference-pair tuple used as `FnMut::Args`, and show `Args.own` is discharged from the two independently prepared reference resources.
- Confirm existing tuple-2 `.share` behavior remains compatible.
- Confirm tuple-0/1/3/4 and an unrelated generic struct do not receive new ownership bodies or new passing paths.
- Keep source signature, body, unwind/leak checks, and refinement unchanged; no tuple-specific resource may be assumed at the callback call.

The old 26.09 patch is an appropriate semantic sketch, not a source patch to cherry-pick. The 26.10 parser file is a different hash (`b26422aff8a6091181485a1355fc60e3a2afde5c8bff2bbe5176fdee07b08622`); any implementation would need an exact-source precondition and fresh hosted source build and controls.

## Minimal higher-ranked output instantiation

The source predicate universally quantifies two independent reference lifetimes. At the actual callback call, the diagnostic intentionally names the concrete instance in which both reference types use the borrow lifetime `'cmp`. A valid matcher can therefore derive, from the matching exported universal clause, the one instance:

```text
<F as FnOnce<(&'cmp T, &'cmp T)>>::Output = bool
```

The narrow transfer must require all of the following at the same function and call:

- the compiler-origin projection is exactly `FnOnce::Output`, has exactly two distinct bound regions, and its RHS is Boolean;
- its arguments are exactly `F` and a two-field tuple of shared references to the same generic `T`, with each reference lifetime paired with the corresponding bound region;
- the exported trait bounds include `FnMut` for those same `F` and argument types;
- the actual call is `FnMut::call_mut`, with exactly matching MIR `F`/`T` and ghost substitutions, both ghost reference lifetimes equal to each other and to the explicit method lifetime `'cmp`;
- there is one unambiguous matching projection; absence, mismatch, different result type, unequal instance lifetimes, or ambiguity produces no equality.

Register only this projection equality before the actual call. Do not rewrite the call result type, infer Boolean from its destination, replace the `FnMut` bound, erase source predicates, or apply equality to all `FnOnce::Output` projections. The equality is justified by universal instantiation, independently of whether the tuple arguments or reference resources can be proved.

The old patch uses this narrow matching strategy and eight matcher cases, but its implementation is 26.09-specific. Its regression matrix is a useful control inventory: matching Boolean positive; `u8` RHS; no output equality; wrong ghost `F`; wrong referent `T`; unequal lifetimes; later unannotated call; and a later body with a different output. These must be regenerated against 26.10 MIR and run on a newly built, pinned hosted binary if transfer is later proposed. A second `FnMut` call in the same body must not inherit a pending equality from the first call.

This matcher/registration step changes trusted translation semantics: it is not a kernel axiom and the resulting equality must be consumed by ordinary typing. The evidence must include raw/decode MIR, matcher traces, the exact equality registration site, and the negative controls. The 26.10 translator file hash is `c1eb897673f88b0b8dc50798deca603bdad2c60818b6d5380ccf1dda055fe445`; do not reuse 26.09 line numbers or assume patch applicability.

## Borrow and unwind boundary remains separate

Tuple packaging and a Boolean projection equality do not complete the callback proof. Stock `FnMut::call_mut`'s normal clause returns current `F` and the Boolean result; its unwind clause returns current `F`, but neither clause independently restores the two borrowed source cells. The callback may mutate permitted interior state, so any eventual source-cell post must describe the current valid state and must not restore snapshots or require purity.

Normal borrow recovery after the natural lifetime block has an existing checked `recover_pair` route in the repository. The direct `Continue` unwind edge exits the call/body before that trailing normal ghost helper runs. A full actual helper/sort4 unwind contract therefore needs a checked route that returns the current source resources and the exact reference-init, close-fraction, lifetime, borrow-end, thread, and callback resources on every direct panic edge, or a sound explicit debt post that the real caller can discharge before using/dropping those elements. It cannot assert full `T.own` while omitting the required recovery tokens, nor assume callback rollback.

This is not solved by either old patch. The right next action after callback evidence is to classify whether tuple packaging or output typing was reached, then design only the next witnessed component. No broad lifetime-scope/kernel extension is proposed here. An ordinary state-mutating comparator that actually panics remains an essential later control; a one-call generic translator result alone is not that evidence.

## Design-review result

The smallest conceivable transfer is two independently reviewed changes: (a) a transparent, exact tuple-2 field-own body, checked as ordinary generated predicate code; and (b) a per-call, single-instance HRTB equality registration guarded by the exact compiler predicates above. Neither asserts source-cell recovery, comparator behavior, or `sort4_stable` safety. The callback's normal/unwind resource proof and any later panic-recovery mechanism remain mandatory and separate.

Before transfer, use the hosted callback log to establish which layer is actually first. Then require source-built 26.10 probes with exact-pair tuple controls, all HRTB mismatches, the unchanged false post, and full normal/unwind/leak/refinement checks. A matching call advancing one type check is component evidence only; it does not accept either component for actual sort4 or close generic/ZST behavior.
