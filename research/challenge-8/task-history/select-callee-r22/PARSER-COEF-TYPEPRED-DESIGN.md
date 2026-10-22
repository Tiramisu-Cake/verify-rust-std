# R22 parser fix: coefficient before a type predicate in assertions

**Defect.** In `rust_parser.ml` (applied SHA-256 `7bf12f12…`), `parse_suffix_expr` returns a list literal `[c]` without suffixes. In an assertion such as `req … &*& [1/2] <T>.own(tid, t);` the expression chain then reaches `parse_rel_rest`, which reads `<` as `Lt` with right operand `T` and fails at `>`. Build `71401a80` shows this exact failure at `verified/lib.rs(123,61-62)` for all eight fractional rows. `open`/`close [c] <T>.p(..)` statements use `parse_coef` and are unaffected. The verifier already supports the intended AST: the translator itself builds `CoefAsn(_, ExprCallExpr(TypePredExpr …))`.

**Applicability.** Assertions (`req`/`ens`/`assert`/`inv`) in which a one-element coefficient literal is immediately followed by `<Type>.pred`. Before this fix such text never parsed, and `<` on a list never type-checks, so no previously accepted program changes meaning.

**Change** (`verifast-r22-coef-typepred-parser-26.10.patch`, SHA-256 `dfdaff60…`, result `6a866aa5…`). In `parse_suffix_expr`, a one-element `#list` followed by `< Type > . Ident` parses that type predicate with the normal suffix parser and returns `CoefAsn(l, coef, …)`. This is the same shape as `[c]p(..)` via `parse_pointsto_expr` and the same `TypePredExpr` rule as the primary at line 349. All other list literals keep the previous path. The translator (`50a77b8d…`), its fractional pins, all source/unit/body/annotation pins and the verifier are unchanged.

**Invariant.** The source and ghost bytes of the approved candidate are unchanged. No trusted rule, summary, axiom or ownership bridge is added. The parser can only accept more text; the AST it produces is checked by the unchanged verifier. The runner pins the patch, the pre/post `rust_parser.ml` SHAs and the translator SHA after it. Its profile-hash check admits only the new parser SHA.

**Distinguishing controls.**
- Positive must now reach symbolic execution.
- The seven fractional controls (`callee-false-normal`, `callee-owner-duplicate`, `callee-owner-loss`, `callee-thread-duplicate`, `no-retained-half`, `omit-selected-own`, `omit-unselected-own`) must fail with distinct, non-parse diagnostics. Any row still failing on a `Parse error` is a parser regression and stops the route.
- `candidate-proof` (the baseline O26 row, which parsed before) must keep its prior outcome class.
- The control targets themselves remain TARGET_UNPINNED until pinned from this evidence.
