# R8 S3 focused dead-code control applicability

S2's three C controls did not reach the intended gate. The positive focused
function finished with zero verifier errors but the process then failed the
executable link check because the fixture had no `main`. The negative source
put an assignment after `return`; VeriFast rejected it during C parsing with
“An epilog statement must be a pure statement.” Neither observation tests the
R8 function-scoped dead-code registration change, so the S2 control receipt is
inconclusive and no tool behavior or proof progress is inferred from it.

The replacement fixture uses ordinary C control flow before a normal return:
`if (0) { x = 1; }`. In the pinned tool source, `IfStmt` is checked as a
condition and both branches are explored under `assume(w)` and `assume(not w)`
(`src/verifast.ml:1136-1147`); integer constant zero makes the assignment
branch infeasible. The dead-code registration walk uses `stmt_iter`, so it
includes statements nested in branches (`src/verify_expr.ml:459-467`). This
gives a source-located unreachable assignment without invalid post-return
syntax or a ghost assumption. The clean control focuses a separate function;
the no-focus control must reject the same assignment at its exact source line.

All three commands use documented `-shared` library mode, which requires no
`main` (`src/vfconsole/vfconsole.ml:597`) and is used for C verification by
official example scripts such as `examples/fm2012/fm2012.mysh:5-8`. This is
appropriate for the two standalone function controls and removes only the
unrelated executable-entry/link requirement observed in S2. A main stub was
considered, but it would add a third function and another source obligation
to the dead-code fixture. Keeping a statement after `return` is invalid for
VeriFast's C epilog grammar; the constant-false branch is valid source syntax
and preserves the intended dead-code predicate. The actual Rust target flags
and semantics do not change.

The three intended controls and acceptance rules remain unchanged:

1. Focus `dead_body`: exit 1 and the exact `x = 1;` source line is reported
   dead.
2. Focus a distinct clean body: exit 0 with no dead-code diagnostic from the
   excluded `dead_body`.
3. Run without focus: exit 1 and the same exact assignment line is reported
   dead.

Wrong diagnostics, parser/setup failures, missing evidence, or partial/timeout
stages remain inconclusive. No verifier, compiler, tool preparation, or proof
is run locally. This fixture-only correction changes no native patch,
semantic source pin, kernel identity, or 26-case input/acceptance criterion.
