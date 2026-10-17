# A1 bounded AST structural gates (UNRUN)

`a1-ast-gates.py` parses selected records from VeriFast's location-bearing
OCaml constructor dump. It accepts bounded constructor, tuple, list, string,
location and big-int syntax; delimiters are string-aware. Unsupported OCaml
printer syntax fails closed. It extracts exact 13-field `Func` records and
six-field `CallExpr` nodes from the selected caller body.

`threshold_posts(ast, inventory, *, stage, baseline=None, common_line)` requires
one common bodyless threshold prototype and one
prototype plus one definition for each numeric compiler inventory alias. The
caller supplies two distinct `TraitImpl`/item DefIndices and exact generated
source lines from the paired compiler inventory; a printed alias alone is
insufficient. The AST `Func` location and verifier focus bind to compiler
`Body.span.lo`; `diagnostic_post_line` separately binds to `fnSigSpan.lo`.
It checks the pinned `Func` envelope for a safe zero-argument
`ConstructedTypeExpr("fn_outcome", [ManifestTypeExpr(Int(Unsigned, PtrRank))])`
return, regular/nonvirtual status,
one `Self: Sized` common or `T: Sized` impl type parameter, and original
body/prototype headers. Other full-unit `small_sort` implementation
aliases are allowed; their separate identity/inventory gate remains required.
Body and interface stages require a native-only common
prototype, while each actual body and its generated conformance prototype
carry one exact outer `Sep(native_returning, 16<=result && result<=32)`.
The caller stage requires the common prototype to carry that range and to
match the native baseline from a previous exact-source stage. The gate
requires exactly returning and unwinding arms, one result binder, no default,
no checked range in the unwind arm, and equal native pre/returning/unwind
subtrees after removing only the exact appended range. It erases source
locations and alpha-normalizes only the explicit outcome/result binders.

`caller_calls(ast, *, owner, expected, source_line, call_lines,
expected_arguments)` checks the
final observer or original `quicksort` body for
the source-line-bound common trait threshold call, and for P1 the original
common `small_sort` call. It rejects generated aliases, duplicate or missing
calls, non-static bindings, wrong type/value arity, and wrong value operand
names relative to the paired direct-reborrow MIR binding; the first type
arguments must be `T` and `F` as appropriate. It does **not** establish
late-bound lifetime identities, MIR operand provenance, dispatch resolution,
body execution, native conformance, or a verifier verdict. Those remain
independent same-Build gates. An observed `-focus` argument by itself cannot
establish a successful body count; the verifier's actual same-invocation
proof stage and location must be classified independently. All returned
records say `proof_credit=false`.

Synthetic parser tests exercise native/range preservation, caller publication,
extra arms, unwind range, duplicate IDs, alias refusal and bounded syntax.
They include full-unit extra `small_sort` body aliases and a quoted decoy
`Func` to check scanner boundaries. The synthetic native post uses two
resource call subtrees, so the equality gate retains the whole native subtree.
The eleven isolated synthetic parser tests passed locally. No actual AST dump,
compiler, exporter, verifier or proof was read or executed. Actual printer
compatibility and every matrix verdict remain UNRUN.
