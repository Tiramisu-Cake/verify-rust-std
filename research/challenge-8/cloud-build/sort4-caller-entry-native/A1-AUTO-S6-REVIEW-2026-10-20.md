# A1 Autonomous S6 independent review — 2026-10-20

**Decision: GO for the bounded S6 Cloud submission after exact committed-closure verification and coordinator live preflight.** This is approval of the AST scope reader repair only; it does not establish native AST acceptance or proof credit.

## Review finding

The pinned frontend confirms why the common threshold declaration appears bare: `modularize_decl` converts a qualified declaration name into nested `ModuleDecl` nodes, placing the bare `Func` under the corresponding module. `ModuleDecl` has fields `(loc, name, imports, decls)` and is printed with that structure; the Rust parser later flattens modules into package paths. Thus the former `functions()` regex extraction lost necessary ownership context.

The S6 reader now parses only outermost `ModuleDecl` source intervals, recursively carries the structural module path through declaration lists, and qualifies only direct child `Func` names. It rejects malformed module names, duplicate module paths, and already-qualified child names. It separately retains unscoped functions under their original names. The initial raw-substring containment issue is fixed with source offsets, so an identical top-level `Func` is not skipped merely because the same text occurs inside a module. Synthetic controls include nested paths, unscoped/module duplicates, duplicate common prototypes, and malformed/ambiguous module ownership. This does not add blanket name-prefixing or relax the threshold contract, source line, type/header, native post, unwind, or existing AST comparison gates.

Profile pins for `a1-ast-gates.py`, entry, runner, all helpers, and source-check matched. `control.py`, entry, runner, backend, profile gate, and sorted recipe all select S6. R2/C source pins remain the S5 versions; no compiler, exporter, schema, decoder, kernel, refinement, or model change is introduced. The window, owner, budget, timeout, lanes, and sequential-build controls remain unchanged.

## Controls and limits

The worker reports **22 AST controls PASS** and **5 profile-gate controls PASS**. I reviewed the changed traversal and test source; I did not independently run the suites. `git diff --check` is clean.

No actual AST replay, MIR replay, compiler/toolchain, Cloud evidence, or raw logs were inspected. Cloud must establish whether the qualified common prototype is now found and continue unchanged P0a/P1 and full-matrix obligations. All matrix rows remain NOT_RUN, including `N-false31`; `proof_credit` remains false.

Module-derived rows currently store the enclosing module source segment in their `raw` field; current gate decisions use the parsed function fields/name/kind, and I found no downstream use of that field. Treat it as diagnostic context, not as the exact raw Func slice.

## Post-submission applicability correction — 2026-10-20

**The GO above is withdrawn for the observed S6 failure path.** Fresh bounded root-AST observation `/tmp/select-auto-S5-root-header.json`, lines 2–3, shows `PackageDecl (dummy, "", [], [])` followed by `PackageDecl (verified32, "StableSmallSortTypeImpl", [], [`. The pinned `rust_parser.flatten_module_decls` converts `ModuleDecl` into `PackageDecl` before the translator's final AST dump. S6's new traversal handles `ModuleDecl` only, so it does not recover ownership from the actual `PackageDecl` surface at this downstream stage and cannot resolve the observed common-prototype lookup failure.

The S6 Build `773189aa` was cancelled before the session cutoff; it terminated `CANCELLED` at 00:34:58Z after 56 charged seconds. Its Evidence Brief request returned HTTP 404. No matrix result or proof conclusion follows from cancellation. The earlier source review and GO remain in the record as historical review of the submitted code, but are not applicable approval for the observed dumped-AST path. No runtime or proof criteria were changed.
