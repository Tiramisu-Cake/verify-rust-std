# H2b: exact nominal SAFE Drop template extension, design before patch

This design is separate from H2a generic pointer-method linkage and the
accepted S6 pointer-only component. O11 full MIR/source captures must be
reviewed before an executable patch is admitted to a hosted profile.

## Stock contract and compatibility

`vf_mir_translator.ml:4408–4574` generates the SAFE Drop template from
`self_ty ^ "_full_borrow_content"` plus `thread_token(_t)`. The borrow
predicate expands to the guard's `inner` field points-to, padding and its
nominal `.own`. The generated post folds over fields, producing each field
points-to and field-value own, then padding and thread. It passes the same
post AST to both normal and unwind in `Rust_parser.mk_outcome_post`.

`translate_body:5109–5152` applies this template to any SAFE Drop body.
Adding a user contract does not replace it: `verify_expr.ml:194–295`
produces template pre and consumes user pre; it then produces user post,
consumes template post and leak-checks. A user pre needing an additional
cell would fail compatibility, while a user post returning an extra
uninitialized cell would leak during compatibility. The actual Drop body
should therefore have **no user contract**; it should ghost-open the
generated full borrow and truthful nominal owner, call the checked generic
method, and prove the extended generated post directly.

## Minimal code shape

The new frontend module holds a single selected ADT name, set only after
whole-file std source, fixture source, ADT and complete typed method MIR
certification. It is reset for every translation. A new environment key,
such as `SORT4_GUARD_REPO_ROOT`, activates this isolated component; absence
leaves stock behavior exactly unchanged. Two **distinct** admitted modes
are required: source-equivalent top-level adapter for H2b controls, and
actual nested `select_unpredictable::DropOnPanic`. The former is explicitly
not evidence for the latter DefPath. Each mode has its own exact source
signature/ghost-contract and complete MIR gate; neither can be selected by
name alone. The selected ADT must have one private non-ZST `inner:*mut T`
field, ordinary generic `T`, and an associated `isDropFn=true`, SAFE
generic Drop body with the reviewed two-block graph and typed
`mut_ptr::drop_in_place<T>` call. The actual mode additionally pins the
unchanged std `hint.rs` whole-file SHA and exact nested body bytes, and
retains the outer helper's full CFG/cleanup gate.

Inside `gen_drop_contract`, after stock construction of `pre`, retain
its original field fold and stock padding/thread clauses. For **only** the
selected ADT, append an uninitialized pointee-cell assertion to the field
fold accumulator. The field fold introduces the binder `inner`; its raw
pointer own is stock `true`. Schematic OCaml AST:

~~~ocaml
let padding = Ast.CallExpr (... padding_pred_name self_ty ...) in
let suffix =
  if Sort4Guard.is_selected self_ty then
    Ast.Sep (limpl,
      Ast.PointsTo (limpl,
        Ast.Deref (limpl, Ast.Var (limpl, "inner")),
        Ast.RegularPointsTo, Ast.DummyVarPat),
      padding)
  else padding
in
List.fold_right produce_stock_field_post fds_no_zst suffix
~~~

The `PointsTo` must use the **generic pointee `T`**, inferred from the
`inner:*mut T` binder; it states optional storage (`*inner |-> _`) without
`<T>.own`, an initialized payload or an `Element` right. Placing it in
the fold accumulator means the field chunk introduces `inner` before it
is referenced. The post still goes to both normal and unwind. No
`gen_contract`, ordinary ADT, free drop-glue, kernel, parser, prelude,
leak/dead-code/refinement setting or generic SAFE Drop type is changed.

## Independent acceptance gates

H2a must prove a source-equivalent unsafe generic method with normal and
unwind `thread + *slot |-> _`, using the stock generic free-drop contract.
An exact typed-call redirect in the actual generic Drop body may then use
that checked summary. It must pin the source method body, receiver/callee
types, `Move(_2)`, destination, two-block CFG and unwind `Continue`; it
must not reuse S6's pointer-preserving/no-unwind rule.

For H2b, positive acceptance requires the actual SAFE Drop body to open
the real guard owner, invoke H2a, and discharge the extended template
normal **and unwind** posts with return/leak checks. The constructor and
concrete `u32` witness must close owner from a real initialized cell.
Missing cell, duplicate cell, wrong target, initialized-preservation and
false normal/unwind posts must fail at intended obligations; source and
MIR mutants must reject before proof; ordinary Drop controls must prove
under the same console/profile. NORMAL/readonly exports, decoding,
refinement, source immutability and all verifier checks stay enabled.

The exact actual nominal DefPath and guard/drop-flag cleanup in the outer
helper require a later separate admission case; a green standalone adapter
is never labeled actual helper proof. The template change is a trusted
frontend shape rule whose truth is still checked by proving the Rust body;
it is not a lemma or an axiom asserting the target helper result.

## Candidate patch after H2a, not yet accepted

`verifast-h2b-nominal-drop-template-26.10.patch` is a separate overlay on
the H2a local-only gate. A second env key is required; its root must equal
the already certified H2a root. In `gen_drop_contract`, only a selected
`DropOnPanic<T>` with one `inner` field appends the optional pointee cell
as the tail of the existing field fold. The same generated post goes to
normal and unwind; stock field own, padding and thread remain. Ordinary
Drop types take the original stock padding tail.

No hosted verifier result exists for this patch. The O13 concrete `u32`
owner witness stopped at a parser restriction on `close <u32>.own`; the
fixture now uses the stock primitive declaration `close u32_own`, whose
body is `true`, and still needs a new hosted proof. The H2a linked fixture
omits the witness to isolate the SAFE Drop method transition. Acceptance
of this template needs a fresh H2a proof on its revised minimal contract,
then an isolated run with this template active and the concrete owner
witness independently proved. A template-only PASS without body return
and leak checks, both outcomes, and ordinary Drop controls does not count.
