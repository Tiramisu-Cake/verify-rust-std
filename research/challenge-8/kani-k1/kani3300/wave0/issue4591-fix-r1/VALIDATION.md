# Static and mock validation

Run python3 -B validate.py from this immutable directory. VALIDATION.json is
the executed result and check inventory. This validates source/git bindings,
cleanliness, author/skip message, sibling/sole-parent provenance, exact hashes,
compiler tree identity, fixture-only delta, protected main files/trees and all16
workflow inventories. Both regression-main.patch + fix.patch and full-main.patch
replay independently through temporary Git indexes to tree
01140856c15e161ff6fc4c1ce460fd4208a298cd.

pfc_fixture_check.py checks direct lexical selected-target calls in each of the
13 PFC harnesses. It pins the two repaired bodies' unconditional direct and
copied calls and the dedicated identity provider/zero postcondition, then checks
the direct-0 PASS/copied-1 FAILURE source oracle. Sixteen narrow checks include
rejections of both original unreachable fixtures, missing/comment-only/dead/
cross-harness direct calls, a failing direct input, a passing or removed copied
call and a weakened postcondition. Every other original function/attribute is
compared unchanged; all old negative output groups are preserved. The overlap
compile-error fixture is inventoried lexically and gains no semantic credit.

Synthetic publication metadata accepts a same-tree nonskip sibling and rejects
candidate, main, short SHA, tree drift, merge/wrong parent, empty/extra range,
skipped ancestors and all supported skip directives. Actual read-only CLI
checks reject the candidate, main and abbreviated SHA. No future final commit
is created. These tests exercise metadata only and do not authorize publication.

Frozen g0 package and review file bytes are compared with their exact committed
objects. Main is rechecked read-only; observed upstream drift is bound into
checkpoint and CI request, with GO blocked pending root/coordinator decision.
The pinned source parent remains unchanged. No historical evidence is upgraded.

Compiler/typechecking, macro expansion, rustfmt, cargo/rustc, Kani/CBMC,
new main/fixed native regressions, fullrunner, performance, CI and publication
remain NOT_RUN. The static/mutation model is not an AST/MIR/FnDef proof or
native execution. Same11 delta APPROVE and root GO are still pending.
