# Selected binding / caller length interface — maintainer review J

Read-only review of incoming `5ffebdf53cc37b5814fa78ad3acb4081519288d8`.
No candidate integration, compilation, extraction, verification or classifier
replay. Both new candidates remain **uncompiled / NOT_RUN**. First agent retains
implementation and caller-proof ownership. [Exact inputs](INPUTS.json),
[independent review](INDEPENDENT-REVIEW.md), [session checkpoint](END-CHECKPOINT.md).

| Part / next experiment | Verdict | Boundary |
| --- | --- | --- |
| Compiler-selected binding admission | **CHANGES_REQUIRED** | Actual body TypingEnv query is suitable; emitted evidence is insufficient for binding admission. **GO only for evidence-only observation**, selected translator mode disabled, in a separately authorized Cloud session. |
| Native selected-method/helper interface and abort alias | **CHANGES_REQUIRED** | Pure-bound design and narrow divergence alias are statically reasonable. Executable admission/runner integration and observed full signatures are incomplete. No new semantic rule is justified. |
| Complete selected-route proof admission | **BLOCKED** | Missing final call cardinalities, unobserved complete clauses/lifetime substitutions and no same-input compiler-evidence validator. Current candidate cannot qualify a caller proof. |

The preserved I tool is `b6cb276afd13107c2a90ca50acbb12ff0a992dd8`, profile
`verifast-slice-as-mut-ptr-native-c3-20261011-i`, checkpoint
`4214cbe06cad959c17ec6e87d345f1063516b167`. Its reviewed two-Build readiness is
unchanged. Full runner `0371f4f8c19e488cd32fb719a8b2f8fcf3dbcbd0` remains UNRUN;
this review does not require another run.

## 1. Compiler identity is not the threshold-body theorem

In the incoming directory, `compiler-selected-instance-evidence.patch` at the
`encode_fn_call_data` hunk calls `Instance::try_resolve(tcx,
body.typing_env(tcx), callee_def_id, callee_args)`. This is the actual MIR body's
environment; the patch neither invents an environment nor changes encoded MIR.
Default-off provider/phase/fixture/method filters bound its observation scope.
This is a useful way to investigate the pinned compiler's answer.

The success `info!` record saves caller/callee DefPaths, TypingEnv, resolved
DefId/DefPath and source/call spans. It omits **Instance kind, original callee
DefId and generic args, resolved instance args, and caller DefId**. A selected
body path is not sufficient to distinguish an item instance from another
instance kind or to connect substitutions to the exact call. Debug spans/DefIds
are run-local evidence, not standalone persistent source identities. The probe
also has no required-record coverage check; exact path filters and logging
configuration must be observed, not assumed to emit records. None/error are
logged but do not themselves enforce rejection. No runner validator exists for
this new evidence (`driver.py` only runs the older threshold lane).

Before enabling binding: retain complete instance/call identities, compiler
pin, exact source/manifest and normal/read-only MIR hashes, body/basic-block/
callsite identity and observed clauses/substitutions; validate the selected
DefId against the actual local implementation body and arguments of that same
extraction. Require coverage of both threshold and small_sort calls, and
separately check the direct same-argument helper edge. Missing, duplicate,
none/error, unexpected instance kind/args or foreign-source evidence must refuse
admission. `SORT4_SELECTED_COMPILER_BINDING_VERIFIED=1` is only a runner assertion
until those checks are implemented and evidenced.

Historical Build `8fa3210b-1dd2-4578-b0d1-49819cc07a84` verified selected32/default16
under **source/clauses-based routing**, not exported compiler selection. Preserve
that theorem and its unaccepted binding assumption separately. The new probe
whitelists only selected-branch wrappers; it does not yet provide observations
for the two-implementation threshold probe or unconstrained quicksort. A
selected-only fixture cannot establish dispatch in the original blanket/default
inventory. No observation here qualifies unconstrained `quicksort<T,F>`.

## 2. Native interface and abort

`selected-branch-binding.patch`, `add_len_bound` / `interface_contract`, returns
`(Ast.Sep(bound, pre), post)` with only `ptr_len(v) <= 32`, for the renamed
selected small_sort/helper. It transforms the generated `pre_post_template`
before `contract_template` is created. For these fixtures (no explicit contract
on those two functions), existing translation uses that template for both body
and callable interface. No native source/scratch/F/thread/type/lifetime conjunct
is removed; the normal/unwind post tuple is passed through. The threshold's
explicit strengthened result post remains a body obligation with native safety
refinement, rather than a literal32 substitution at the caller.

`selected-branch-cases.rs` retains the actual threshold call and branch, forwards
the same v/scratch/is_less, and asserts the bound in the branch and helper.
The required final artifact must show the caller derives the selected method
precondition from the proved threshold result and branch, and the method passes
it to the helper. Compare generated body/callable contracts and original normal/
unwind posts, typed arguments/Move edges and native resources in final AST;
verify all bodies, normal/early-return/unwind closure, free/leak/refinement and
nonvacuity. Source-level correspondence alone is not that result.

`selected_abort` matches zero-substitution/zero-operand intrinsics::abort, no
normal target/successor, Unreachable unwind, in the exact helper; the lowered call
must also have the exact AST shape. Pinned Rust declares the intrinsic `-> !`
and `#[rustc_nounwind]` (intrinsics/mod.rs:450–453). I's existing
`bin/rust/std/lib.rsspec:1553` process::abort has req true, both posts false and
terminates. Thus this alias creates neither a returning nor an unwinding path;
no other Unreachable edge is justified by it. Still require actual MIR/AST and
reachable scratch-insufficient arm evidence. The surrounding helper branch
structurally skips later checked no-unwind conversions for ordinary calls; the
predecessor's G1/selector body guards appear inapplicable here, so this is not a
demonstrated semantic defect. On any future I rebase, preserve its additional
`checked_r3_cleanup_no_unwind` handling and all unrelated call semantics.

## 3. Admission and controls

The four-body inventory/rename check and exact source MD5 whitelist are real
translator checks, as are full-unwind/no-skip and selected impl clause checks.
They are not a complete call inventory. `threshold_calls`, `small_sort_calls`
and `helper_calls` increment but are never checked after translation; missing
or repeated edges can escape that gate. Unhandled calls still enter
`fn_specializer`; the bound helper edge must be confirmed to take the exact
route, and relevant ignored-clause routing must refuse rather than merely warn.

`freeze_clauses` compares the entire caller clause list to only Sized<T> and
FreezeMarker<T>; substitutions admit T/F without lifetime arguments. Actual
wrappers/methods also have F: FnMut HRTB obligations. Their decoded full clauses,
projection equalities and erased lifetime substitutions have not been observed.
The present strict shape may reject legitimate input; that would be admission
failure, not a semantic negative. Do not widen it by assuming omitted predicates
or lifetimes are irrelevant. Observe and pin them first. Mode exclusion covers
old threshold binding, not an explicit complete native/C3 flag inventory;
runner-clean environment/effective inputs and default-off isolation still need
checks. Patch base hashes differ from I's translator: this is not an I-compatible
integration claim.

| Control | What it can establish / outstanding requirement |
| --- | --- |
| In-branch len<=31 | Suitable semantic negative: len32 is allowed by threshold32. Must reach this assertion with feasible native inputs and a verified actual threshold call. Earlier binding/overflow/resource failure gives no credit. |
| Missing source array | Suitable authority negative in design: leak only the source array, preserve foreach/scratch/F/thread/types, then fail the selected call's native array precondition. Must observe actual borrow/resource protocol and exact first failure; an earlier array assertion failure does not qualify. |
| Wrong selection (+Copy) | Historical frontend inability to specialize Copy/Clone remains **INCONCLUSIVE**. Source-digest refusal alone tests source admission, not selected-instance evidence validation. Wrong-target/args/kind/missing/foreign evidence rejection remains untested. |

Existing threshold false31 is `threshold == 31`; it does not replace the new
caller `len <= 31` control. No source/contract/edge or semantic negative is newly
executed. Missing cardinality, full clauses and evidence admission block use of
the conditional proof route; they need not block a no-credit exporter observation.

Recommendation: first observe the pinned compiler in real body TypingEnv with
selected translation disabled; then review complete evidence and fail-closed
admission before a selected-interface proof experiment. No handcrafted TypingEnv,
assumed summary or supplied ownership premise is admissible. Public IS_ZST
linkage, helper overflow, native C4+select/full sort4, general O23 and inherited
trust reservations remain OPEN. len<=32 is not nonzero-size evidence. Static GO
is neither compilation/proof success nor profile/consumer adoption.
