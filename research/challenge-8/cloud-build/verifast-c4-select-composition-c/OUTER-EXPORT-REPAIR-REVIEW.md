# Outer-export blocker review

**Recommendation: GO for a lossless `MergeFractionsStmt` projection as a
narrow candidate; HOLD any claim that this alone resolves the archived outer
export failure.** This is static review only. I did not run or change the
translator, verifier, build, or Cloud job.

The Build1492d638 outer-negative log reaches the callback and then raises
`Failure("TODO")` while `typed_transport_view` calls
`Ocaml_expr_of_ast.of_package`. The stack ends at `of_body_ss` line 1137 and
`of_decl` line 1031. Since export walks all `headers, flattened`, that stack
does not name the first unsupported statement or limit the scan to the outer
fixture body.

There is a concrete required constructor in the exact pinned fixture:
`recover_pair` contains `merge_fractions lifetime_token(k)` at
`verified/lib.rs:43`. The Rust parser lowers this to
`MergeFractionsStmt(l, a)` (`rust_parser.ml:673`); `asn` is an alias for `expr`
(`ast.ml:692`). The generic projection currently unconditionally raises
`TODO` for this constructor (`ocaml_expr_of_ast.ml:844`). A complete local
encoding is simply a `MergeFractionsStmt` node containing `of_loc l` and
`of_expr a`. It preserves both AST fields and introduces no normalization or
admission change.

The other current unconditional statement failures are `PerformActionStmt`,
`SplitFractionStmt`, `CreateBoxStmt`, `CreateHandleStmt`, and `DisposeBoxStmt`
at `ocaml_expr_of_ast.ml:842–847`. The archived stack cannot establish whether
one of those occurs earlier in an imported/header package. Do not catch the
exception, omit a node, substitute a placeholder, or claim full export success
based only on projecting the known fixture merge. Keep each other constructor
unsupported until its occurrence and full-field encoding are justified. A
labelled failure naming each unsupported constructor would make a subsequent
Cloud diagnostic decisive without broadening the projection domain.

The export hook’s exact fixture source/target/strictness/output checks remain
the relevant admission boundary. Any successful output must still represent
the full AST losslessly; proof of the intended negative VC remains separate
from export success.

## C2 post-review and delivery

**Verdict: GO to submit the exact C2 candidate for its authorized Cloud
preflight.** This is a source/delivery review only; it does not resolve the
outer-export failure or grant proof credit.

Reviewed tool diff `09389e2c0a4d6d2ed4e1146df0ad6321832c12cb` to
`2e95eec0c0a08c071f896fd9d00a606f572d5352`. In
`ocaml_expr_of_ast.ml`, `MergeFractionsStmt(l, a)` now serializes both fields
as `C("MergeFractionsStmt", [of_loc l; of_expr a])`. The other five currently
unsupported statement cases now fail with constructor-specific messages and
remain fail-closed. This is lossless for the known merge node and does not
silently admit the other statement forms. The only additional translator delta
since the independently reviewed C1 tool is the normal-path `Open` of
`raw_ptr_own<T>()(t, min)` after the selected-pointer identity assertion; it
matches the previously reviewed pointer-cut scope and location. No proof or
export run was performed here.

Independently checked `PATCH-DELIVERY-CHECK-C2.json` against the C2 integration
manifest. All three ordered patch hashes match the patch files, and the
receipt's six effective-source hashes match the manifest; in particular the
sixth, `src/frontend/ocaml_expr_of_ast.ml`, is
`cd90799926cfc73d86e3c9b137ed84e977b1a918d1ba8723f3f26125cbb7aafe`. The
candidate is explicitly marked experimental/unaccepted, and the receipt marks
compilation, extraction, and proof as not executed. Delivery integrity permits
submitting this exact candidate for the next Cloud run; it does not show that
the full outer AST export now succeeds. The previous stack may proceed to one
of the other five labelled unsupported nodes, so keep that gate open and
classify any such refusal as pre-proof setup failure.
