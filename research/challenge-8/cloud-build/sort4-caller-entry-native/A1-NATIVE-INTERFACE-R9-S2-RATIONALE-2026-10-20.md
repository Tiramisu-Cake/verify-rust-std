# R9 S2 rationale — select the compiler-bound implementation definition

## Observed defect and source applicability

S1 Build `2f7b5d56-f9b6-44d1-a1fd-89f7b79870a4` terminated FAILURE after 905
seconds. Actual R-only and final-C compilation completed. The source-reported
R-only P1 baseline failure is at `lib.rs:42:1-59:2`:
`A1 small_sort implementation signature compiler item body is not unique`.
That diagnostic is retained as the S1 report; it does not establish a verifier
result.

At tool SHA `f76012fb518703b1d98e243ac4f487f16877cfcb`,
`src/frontend/ast.ml` defines `Ast.Func` fields in order, with its eleventh field
`body : (stmt list * loc) option`. `translate_trait_required_fn` emits required
trait function declarations with `body=None` (translator lines 4707–4782).
`translate_body` builds a separate body declaration with `body=Some (...)` and a
signature declaration with `body=None` (lines 5160–5235). The consumer builds
`traits_and_body_decls = traits_decls @ List.map snd body_decls`; it does not add
`body_sigs` to this collection (lines 8120–8129). The S1 patch searches this
collection by the translated `trait_impl_item.def_id` name alone, so a
same-named trait prototype can make the implementation candidate non-unique.

## Narrow fix and preserved checks

For `StableSmallSortTypeImpl::small_sort` only, require the candidate's AST
`body` field to be `Some _` in addition to exact equality with
`TrName.translate_def_path item_def_id`. Keep the existing fail-closed
zero/multiple-candidate errors and all subsequent checks: compiler identity
equals `<self_ty as trait>::small_sort`; expected generic and lifetime binder
roles/counts and Sized bounds; native result and first-input structure; then
specialize `Self` while preserving the trait prototype's pre/post and native
signature checks. The patch must not change the required declaration, native
pre/normal/unwind contracts, equality/refinement criterion, C patch, source
transition, or runner core.

## Distinguishing controls

Apply the patch only to a temporary copy of the pinned source. Confirm the
diff adds a body-presence discriminator to the exact compiler-item-name match,
preserves fail-closed uniqueness and signature checks, and leaves all source
outside the existing translator overlay unchanged. Run only static patch,
manifest/profile hash checks. Inspect same-name prototype+definition, absent
definition, duplicate definitions, and wrong compiler item identity as static
source cases; actual OCaml behavior remains Cloud-only. A Python reimplementation
of this OCaml predicate is not treated as validation. No compiler, extractor, or full runner is run
locally; source selection success is setup evidence only.

## R9 source-candidate version and static application

The historical R8 candidate remains pinned at translator SHA
`4be0d553bc99ee638ef173f2d6b48d9f2ef6ed6bb3245d6b3cf032afbb86d799`. R9
versions the candidate to `894bfe9032a19caef1370a563be1c8c9ea09a06bcdf51061f5b1d60b60c37c0a`
after adding the body-presence discriminator. Applying the unchanged C patch
to that R9 candidate gives translator SHA
`d69dd8c87093ebdce275c61b718d339b4425da6a6d97ebd866e36c1724d680dd`. Both
patches applied with `git apply --check` and `git apply` to a disposable copy
of the pinned `9391bff0376ad008798a950d76dbaac095cacbe8fd5acf5b2ea4d336a759f33f`
SOURCE scratch. The R9 manifest and profile pin these new candidate hashes;
the R8 profile and release bytes remain unchanged. No compiler, extractor,
runner, verifier, or Cloud control was run.
