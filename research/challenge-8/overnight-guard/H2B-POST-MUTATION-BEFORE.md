# H2b generated-post adversarial test profile: before implementation

O17 proves the local source-shaped generic guard Drop against the selected
H2b generated post. The separate generic method probes show that its
summary cannot return the initialized value or `<T>.own`, but those probes
do not directly establish that `gen_drop_contract`'s **selected Drop post**
cannot silently include them. A test-only adversarial post profile should
make that precise without changing the accepted O17 verifier binary.

The candidate is a separate overlay applied **after** H2a/H2b/H2c to a
disposable hosted verifier build. It may add one opt-in environment key,
`SORT4_GUARD_TEST_POST_MUTATION`, read only after the same local source and
full typed-MIR certificate has selected `DropOnPanic<T>`. Unknown values or
use without the ordinary H2b same-root gate are rejected. With no key,
the AST and verifier behavior are the same assertion AST as the production H2b profile.
For each named value, change one generated **post** assertion, never the
precondition, Rust body, nominal owner predicate, H2a method contract,
source/MIR gate, free drop glue, memory rules or verifier checks. The
mutation profile is test evidence only and cannot be cited as a positive
proof profile even if its no-key control passes.

The exact H2b positive post is stock thread/field/padding resources and
one optional `*inner |-> _` on both normal and unwind. The adversarial
variants are:

| Variant | Exact extra obligation | Intended failure |
| --- | --- | --- |
| `initialized` | replace the selected `Ast.DummyPat` with an initialized-value pattern on both outcomes | selected guard Drop's normal post cannot close initialized `points_to<T>` after real generic `drop_in_place` |
| `t_own` | append an existential `<T>.own(_t, ?value)` to both outcomes, using `Ast.TypePredExpr(T,"own")` | selected guard Drop's normal post lacks consumed generic owner |
| `second_cell` | append a second `*inner |-> _` to both outcomes | one returned optional cell cannot satisfy two full pointee cells |
| `false_normal` | conjoin `Ast.False` to the normal post only | normal return must fail after the checked call |
| `false_unwind` | conjoin `Ast.False` to the unwind post only | normal path still returns/leak-checks; unwind path fails after the checked call |

`initialized` should use `Ast.DummyVarPat`: the inspected
`assertions.ml:1638–1651` chooses the uninitialized pointee symbol only
when the pattern is exactly `DummyPat` (or the kind is `MaybeUninit`), so
`DummyVarPat` selects the initialized symbol. This still requires a hosted
negative proof before the control is accepted. `t_own` must use the generic type-predicate
AST, not a hard-coded primitive owner. The two false-post variants need
separate outcome ASTs passed to `Rust_parser.mk_outcome_post`, retaining
the stock resources in the other outcome.

The hosted runner should first prove the unmodified positive with the
test overlay key absent and the full H2a/H2b gate active. It should then
run the five negatives on the **same source bytes** and same verified
generic method, constructor, concrete owner witness, local guard body and
ordinary Drop. For each, preserve original/verified source, paired NORMAL
and readonly MIR, independent refinement, full VF log and a manifest of
the exact test overlay SHA and selected mutation. An intended negative
requires no setup or certificate failure; the checked callee must prove
both return/leak paths; the selected guard body must enter and execute the
real method call; the sole failure must be the named generated post,
normal or unwind as specified. Ordinary Drop remains a same-profile
unselected control in the no-key positive. If a mutation fails at AST
construction, source compatibility, or an unrelated function, it is
inconclusive and cannot be counted.

No `Element` right exists in this generic `T` guard unit. Extra Element
permission belongs to the later actual `select_unpredictable` ownership
protocol and cannot be inferred from this test. The actual nested std Drop
DefPath also remains a separate admission obligation.

Candidate overlay and root static review now exist; no hosted result yet.
The isolated TEST diagnostic is approved for O20. Acceptance still requires
inspection of each actual post failure and exact production/test manifests.
