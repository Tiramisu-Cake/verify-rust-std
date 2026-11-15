# Worker15 independent stage P review — PASS

Reviewed only `8e299aa6243bc5f06a29c51e98aafa9564478220..14bc57fdb99960240c4944845a3d985c8af4dcf7`
and its final-C2 dependencies, 2026-11-15. Candidate tree
`1efb6e4dfa69d346df8e23741d11839b1932403d`, sole parent exact C2.
No blocking findings. This accepts P for preparation of Q; native compilation and Q remain NOT_RUN.
Worker14 source/tests/docs and `port/` were not modified.

| Invariant | Independent source inspection |
| --- | --- |
| One fallback predicate | `kani_middle/mod.rs:153` checks `!must_be_overridden && has_body`; codegen `statement.rs:928` and reachability `:285` share it. The select classifier additionally checks intrinsic kind/name, actual core definition path, nonvariadic `(bool,T,T)->T`, and checked body. No second codegen result/shadow model. |
| Validate before transfer | Visitor `:185` checks sized layout and existing `PointeeInfo` mask/argument_size; call `:626` checks actual operands/result before Begin/Store/Load/deinit. Entry and Return validate too. Other intrinsic, foreign, bodyless, shim and marker-hook boundaries remain. |
| Referents of both arms | Points-to `:373` invokes the existing regular-call analysis, not an aggregate/address shortcut. Parameters receive `successors_for_operand`, fallback assignments join branch aliases, Return connects destination to successors of slot0. Bool has no referent; selecting a pointer does not read or initialize its pointee. Existing body overrides, active-cycle error latch and no-partial-result boundary remain. |
| Slots and Move order | For shadow payload `(bool,T,T)`, bool is excluded by `transfers_shadow`; enumerate indices become slots2/3, count2, with the same `instance.ty()` on both sides. `store_call_arguments` emits ALL stores before its separate Move-clearing loop. Copy remains live. Moving the ordinary Item emission into this helper preserves the C2 protocol and F6 reset order. |
| Selected false/padding and return | Fallback assignments retain existing union/typed-storage operations. Both typed loads use existing masks, including false padding; no initializedness OR or blessing. Return stores slot0 before Return; caller loads slot0 After on the normal continuation only. Existing `build_argument_operation` and body insertion implement these edges. |
| B1/F5/F6/F7 | `super_terminator` still precedes resolution, refusal uses `break 'call`, and the common final target flush remains. Hook conjunction and both `reset_nested_call` calls are preserved. All five F7 files are byte-identical to C2, including both `replace_delayed_body` writers and both backend scopes; no shared-cache write was added. Runtime/mask implementation and existing C2 tests are unchanged. |

Compile seams: independently bound 17 contracts / 36 calls using this directory's
`check_seams.py` (unchanged source-token tool from the worker15 slice audit), with
separately prepared `CALL-CONTRACTS.json`. `SEAM-AUDIT.json` is
`PASS_BOUNDED_STATIC_SEAM_AUDIT`: 34 changed Rust files, no errors; ten tool synthetic tests PASS.
All declarations/imports/impls in changed files and compiler consumers were inventoried.
Stable `Instance`/`Ty` feed the classifier/visitor; points-to explicitly converts its internal
Instance to stable and retains internal MIR args/Place/Location for arity5 regular-call effects.
`TyCtxt` is supplied at all three protocol consumers. Signature inputs are `&Ty`, comparisons
use `left != right` and `*left == output`; actual args/result use stable Ty equality.
Slot/count/length/index arithmetic is `usize` (`idx + 1`); sized mask is `Option<usize>`;
no new narrowing cast, numeric cross-type comparison or mutable shared borrow was introduced.
Layout constructors return the same `Result<PointeeInfo, LayoutComputationError>`;
module privacy/import leaves resolve within the current C2 hierarchy.
This lexical/manual check is not Rust name resolution, typechecking or a compilation claim.

`IDENTITY-CHECKS.json`: exact parent/tree/scope, source diff-check PASS;
65/65 fixture files match corrected old SEL1 `39a6521bf1` byte-for-byte, in12 groups.
All29 selectors remain:12 intended SUCCESS,17 intended failure/refusal, each with its own
exact root/golden. Inspected shared controls, Copy/Move, both arms, overwrite, padding,
pointer holes/null/dangling and real hint-wrapper bodies. Existing C2 controls are unchanged.
Nested/UnionAsField is a general construction refusal before select, not select-guard coverage.
Absent/overridden fallback and unsized T are static-only; no runtime coverage is claimed for them.
Quick must preserve all inherited suites/modes/negatives/ignores, S5 4/4 and F7 18 comparisons.

No local compiler/build/verifier, push, dispatch, Cloud spend or proof credit.
Historical runs were read as context only and are not rebound to this candidate.
