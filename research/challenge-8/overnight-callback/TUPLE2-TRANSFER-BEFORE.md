# BEFORE — exact generic tuple-2 ownership transfer

Status: implementation authorized within OVERNIGHT-SELECT-SORT4-26.10. The rationale, semantic boundary, controls, and self-review are recorded here before changing the VeriFast source patch. The task transfers only the tuple-2 ownership lowering witnessed in O5; it does not transfer HRTB or unwind semantics.

## Witnessed problem and hypothesis

O5 (`37702922138`) ran the unchanged generic callback with the actual `FnMut::call_mut` in the named function. NORMAL/readonly export and decode plus refinement all passed. VeriFast then failed at `lib.rsspec:47` while consuming `<Args>.own(t, args)`, with `No matching heap chunks: own(std_tuple_2__type_info(...))`, at the exact expression `is_less(&*left, &*right)`. This is a concrete proof obligation, not the previously observed optional AST-dump serialization failure.

The pinned prelude declares `struct std_tuple_2_<T1, T2>(T1, T2)`. The parser currently emits a bodyless opaque fixpoint as `std_tuple_2__own`, then aliases the tuple's sole `.own` predicate to it. Hypothesis: changing only that parser-generated definition for this exact internal struct and exact two type parameters to a transparent predicate constructor with body

```text
<T1>.own(t, v.0) &*& <T2>.own(t, v.1)
```

lets ordinary field resources form the callback's tuple argument. The actual references must still be constructed and justified by the existing borrow setup; the tuple predicate packages them and does not create referent permissions.

## Domain, semantics, and trust boundary

The generic tuple proof covers arbitrary well-formed, sized `T1` and `T2`, without `Copy`, `Clone`, `Freeze`, or `Drop` restrictions. The actual callback instantiation is `T1 = &'cmp T`, `T2 = &'cmp T`. Tuple `.own` means ownership of each actual field, with no duplication, omission, value transformation, callback summary, or synthetic resource.

The tuple-2 component changes only the Rust parser's generated `.own` predicate for the exact internal declaration shape recorded below. The generated `PredCtorDecl` body is checked by the verifier; it is not a trusted lemma or axiom. One existing `.own` alias remains, and the existing tuple-2 `.share` prelude definition remains byte-identical. Every other struct and tuple arity must keep its opaque prior behavior. In O7's cumulative profile, separate S6/A1/CFG components also modify `std/lib.rsspec` and the MIR translator; the callback runner allows only those three exact files, checks stock FnMut/prelude invariants, and records the full profile diff and per-file hashes.

Trust remains at the Rust frontend/parser correspondence that the exact named internal tuple declaration's two source fields are the tuple's field indices `.0` and `.1`, plus VeriFast's existing modeling of generic field ownership. This does not claim ABI/layout/offset facts or alter Rust runtime behavior. The tuple component does not change the trusted stock FnMut contract, exporter/decoder, kernel, or refiner. Cumulative-profile changes are separately named and hash-recorded by the main workflow; this tuple runner rejects any extra modified or untracked source paths.

## Hosted checks and outcome mapping

Use a fresh checkout of VeriFast `f76012fb518703b1d98e243ac4f487f16877cfcb`; assert the original parser SHA-256 `b26422aff8a6091181485a1355fc60e3a2afde5c8bff2bbe5176fdee07b08622`, apply this standalone patch once, and record the resulting parser hash, exact source diff, binary/tool hashes, and complete hosted build logs. The prelude SHA and tuple-2 `.share` bytes must match stock. In standalone mode only the parser source file may change; O7 cumulative mode separately allows the exact three-file set described below.

The fresh source-built binary must run all selected cases with leak/dead-code checks active and source integrity/refinement checked independently:

- Generic close/open positives: construct tuple-2 ownership from independent `<T1>.own` and `<T2>.own` fields, then open it back to those same fields. These fixtures contain no `Copy`/`Clone` premises and preserve both field values and both field resources; the generic domain imposes no `Drop` restriction. The concrete non-Copy fixture below tests shared-reference fields, not a Drop-bearing tuple owner; add a concrete Drop-bearing instantiation if hosted logs show that generic proof does not cover the intended destructor path.
- Non-Copy referent reference positive: construct/close a tuple of two shared references to a type with no `Copy` implementation, from the two independently prepared reference ownership resources; this is the actual `FnMut::Args` shape.
- Tuple `.share` compatibility positive: close the stock pair-share predicate from its two field-share resources. This directly exercises existing tuple `.share`; an exact prelude hash alone would show only that its definition was not edited.
- Resource-loss negative: open tuple ownership but require only one field's ownership on return.
- Resource-duplication negative: open tuple ownership but require one field resource twice.
- False-post negative: the same body and inputs with only `ens ... &*& false` changed.
- Scope controls: tuple-1/3/4 and an unrelated generic struct remain opaque; tuple-0 keeps its existing special family/lemmas; tuple-2 `.share` remains compatible. The pinned prelude is hash-checked to remain unchanged.
- Unchanged callback: rerun both callback cases from their unchanged runtime/template source under the patched verifier. The positive must pass the witnessed `Args.own` precondition or report a new clearly later obligation at the same actual call/body. The false-post control must still fail specifically at its false normal post, not at setup. Do not add an HRTB equality during this transfer.

The hosted-only source builder is [`build-verifast-tuple2-26.10.sh`](build-verifast-tuple2-26.10.sh); it is for the standalone tuple profile and must not be used to replace O7's cumulative build. Invoke it with the pinned base bundle, an evidence directory, and a fresh source-checkout path. It records the full patch/build provenance and source build logs. Then run [`run-tuple2-own-cases.py`](run-tuple2-own-cases.py) with that patched source checkout/tool home, its generated Cap'n Proto schema, the hosted compiler sysroot, a fresh evidence directory, and the workflow deadline epoch. The default mode fails closed unless the source checkout is the exact pin with only this exact parser patch in the working diff. O7 may explicitly pass `--cumulative-profile`; that mode requires exactly the three changed files `bin/rust/std/lib.rsspec`, `src/rust_frontend/vf_mir_translator/rust_parser.ml`, and `src/rust_frontend/vf_mir_translator/vf_mir_translator.ml`, rejects staged and untracked source changes, still requires the canonical parser diff to equal this standalone patch byte-for-byte, and still hash-checks the stock prelude and active FnMut clause. Both modes save hashes for every allowed source file and the full effective source diff. The cumulative runner consumes the main workflow's separately recorded exact five-patch provenance and profile/tool hashes; it does not rebuild the cumulative verifier. The case runner independently exports/decodes normal and readonly MIR, verifies without the optional AST dump, refines each ghost-stripped pair, and stores per-case logs/hashes/outcomes. It also invokes the unchanged callback runner. Positive candidates, including `.share` compatibility, are not component acceptance by themselves.

Any build/setup/export/decode/refinement failure is inconclusive. The callback positive failing at the same `<Args>.own` is a transfer failure. A later `FnOnce::Output`/`bool` failure is evidence the tuple component advanced, but HRTB remains unmodified and unaccepted. A later unwind/recovery failure is a separate resource obligation. Passing generic close/open alone does not accept callback integration. Full source/refinement controls and negative location checks are required before component acceptance.

## Self-review and non-goals

### Exact source-shape guard, added before tightening the parser patch

Review found that checking only `sn = "std_tuple_2_"` and two type parameters is insufficient: a same-name declaration with a third field or another body form could be misclassified and its ownership silently omit source fields. The patch therefore must match the parser's exact tuple-struct AST: `Left ([], [Field (_, Real, IdentTypeExpr (_, None, "T1"), "0", Instance, Public, false, None); Field (_, Real, IdentTypeExpr (_, None, "T2"), "1", Instance, Public, false, None)], [], false)`. The transparent body is generated only for this exact declaration; every mismatch follows the existing opaque branch.

This narrows the accepted declaration shape without asserting new layout facts: the existing parser's tuple syntax maps the two declared type fields to indexed fields `0` and `1`, while the exact guard rejects added fields, methods/other members, packed or unsized forms, and differently typed or named fields. The hosted profile certificate must check that the exact guard and condition are present in the parser source, in addition to the pinned prelude hash and exact parser diff. Keep the existing tuple-1/3/4/Other opacity controls and add/record this shape guard as a separate profile control. Self-review: this prevents the transfer from silently accepting a future changed prelude declaration; it does not prove general parser soundness or layout correspondence.

The remaining risks are generated AST typing for generic `TypePredExpr`/field selection, duplicate `.own` alias creation, tuple-2 `.share` compatibility, and downstream other-arity behavior; the hosted source build and isolated controls target these risks.

Non-goals: do not implement tuple-1/3/4 ownership, a general struct ownership generator, field drop glue, pointer/provenance semantics, tuple normalization lemmas, HRTB matching, or callback unwind recovery. Do not alter the callback's full normal/unwind posts or turn a partial output-type pass into accepted actual callback evidence.
