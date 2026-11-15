# Slice03 static compile-seam review

Candidate `5ca51679e3f433718807a2e44add0d5abac128e7`, parent
`932fb8395a58f8c86c0d702ba2cae835823b2962`, reference F
`ad499e41dd2db9ccd432f89721638a1f3a0bbd44`.
This executes the procedure from `../slice-02/COMPILE-SEAMS.md` and
`../seam-audit/README.md`: every changed Rust file, current imports/impls,
new/removed declarations, cross-file generic impls and explicitly bound call sites.
Source Git reads only. No compiler, formatter, build, verifier, push or CI.

The exact command is:

```sh
python3 -B ../seam-audit/check_seams.py --repo /root/kani-fix-3300-c2-slices-w14 --base 932fb8395a58f8c86c0d702ba2cae835823b2962 --head 5ca51679e3f433718807a2e44add0d5abac128e7 --reference ad499e41dd2db9ccd432f89721638a1f3a0bbd44 --contracts CALL-CONTRACTS-03.json --out SEAM-AUDIT-03.json
python3 -B ../seam-audit/test_check_seams.py
```

## Manual inventory and concrete bindings

| File / interface | Paired pieces, imports and consumers at this head | Review |
| --- | --- | --- |
| initial_target_visitor | Struct/inherent impl retain `<'tcx>`, MirVisitor retains `<'_>` from accepted2. RawEq adds two `push_operand(&args[index])` seeds; same one-argument helper as casts/copy destinations. Intrinsic, Operand, TyKind/RigidTy, InstanceKind imports already2. Sole constructor and its two arguments remain2. | No declaration/signature removal; exact F file. |
| ptr_uninit/uninit_visitor | CheckUninitVisitor generic struct and all three impl targets retain explicit arguments. RawEq iterates both reference operands, makes `[u8; full layout size]`, emits existing CheckAs or explicit Unsupported, and is removed from can_skip_intrinsic. `Ty`, `TyKind`, `RigidTy`, and **`UintTy`** resolve through rustc_public::ty; two arguments to `Ty::try_new_array`. Existing LayoutComputationError/TargetFinder/MemoryInitOp/InsertPosition/body APIs remain ancestor definitions. | Missing UintTy import found manually and corrected before final head; no storage helper needed. |
| relevant_instruction | MemoryInitOp and both enum impls retain ancestor signatures/variants. CheckAs calls mk_cast with5 arguments. Reference Copy/Move place is reborrowed through ProjectionElem::Deref and mk_ref with4 arguments; constants are cloned directly. New ProjectionElem leaf has first consumer here; no ConstantKind/storage imports. All existing mk_ref users retained. | No new variant, helper signature or exhaustive-match obligation. Both imports and helper bodies available now. |
| check_uninit/mod | UninitInstrumenter<'a> unchanged. Existing CheckAs dispatch computes a pointer to byte-array type; mk_operand reborrows references via the paired helper. New reference diagnostic arm uses explicit pointee_ty; raw-pointer CheckAs keeps the existing operation.operand_ty path. build_get_and_check4, mk_operand3, operand_ty1 arguments at all bound sites. PointeeInfo/PointeeLayout and Ty APIs remain available. | Existing builder ABI/runtime marker only. No CheckRefAs or future operation/runtime dependency. |
| ty_layout | PointeeLayout/PointeeInfo/Display impls unchanged; data_bytes_for_ty keeps3 arguments at11 call sites; generate_byte_mask keeps2 at6 sites. Enum variants compare enum-local field masks and add enclosing offset once after equality; tag uses current_offset. Pat passes current_offset to recursive base call. MachineInfo/MachineSize/VariantsShape/TagEncoding/IndexedVal and TyKind/RigidTy imports are present from baseline/2. | No signature changes, storage4/closure5 helpers or new generic context. Existing unsupported closure arm retained. |
| One complete zero-extent fixture | immutable-masks/empty source/golden equal exact F; both referents have zero MaybeUninit elements. The18 nonempty MU/raw-union fixtures are absent and reassigned4 by ORACLE-MAP-CORRECTION.json. | Original B1/upstream/accepted2 fixtures untouched; production unchanged from d0345ddf4f. Native lowering/qualification still NOT_RUN. |

All current imports/impls and changed/removed signatures for these five production files and
one fixture are retained in SEAM-AUDIT-03.json (six Rust files). Production has no
new/removed function/type/impl declarations; only two use lists change (ProjectionElem,
UintTy). Unchanged ancestor contracts are retained in CALL-CONTRACTS-03.json; nine additional
contracts bind the actual affected APIs, including unchanged callers. The checker's
same-spelling reference inventory is navigation, not symbol resolution.

## Neutral import ownership correction

The stage0 map put the one-line UintTy import replacement in owner4, while owner3 RawEq
already uses UintTy::U8. Automated token inventory alone passed the preliminary candidate;
manual consumer/import review found the missing prerequisite. SEAM-PRIOR.json records the
superseded local candidate and bounded checker limitation; no native compile failure was run.
SOURCE-MAP-CORRECTION.json assigns exactly B1--F:19:005 old29/new33 to3. This is the TASK's
neutral-import/first-consumer rule; no substantive semantics moved from4. The effective owner3
set has22 parts (original20 plus two import parts); owner4 loses those two, owners1/2/5/6/7
remain byte-identical. Canonical maps and historical slice02 receipts stay unchanged. Future
extraction must apply this explicit delta before composing4; it must not count the import twice.

## Result and limits

Exact final-head report: PASS_BOUNDED_STATIC_SEAM_AUDIT, errors[]. Ten synthetic checker
tests PASS. Exact extraction/ownership, protected ancestor files, complete F fixtures,
reference CheckAs/import binding and source/residual alternate-index endpoints are checked
separately in STATIC-VALIDATION.json.

This is bounded source-token and manual dependency evidence, **not compile PASS**. No macro
expansion, Rust name/type/trait/borrow checking or native tests ran. Worker15 independent
review and coordinator exact-head CI remain PENDING. In particular, u8/raw_eq controls do
not qualify nested Pat/enum offsets; all nine owner3 fixtures mapped to4 plus18 reassigned owner4 fixtures remain pending.
The old19-fixture dependency assessment was contradicted by coordinator run43704461635;
this rewrite preserves production and corrects fixture placement only. Qualification on3
is NO_REGRESSION, with integration PENDING on4; see DEFERRED-OBLIGATIONS.json.
