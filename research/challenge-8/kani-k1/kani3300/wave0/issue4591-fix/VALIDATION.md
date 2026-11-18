# Static and mock validation

`python3 -B validate.py` passes the source identity, scope, clean-worktree,
hash, whitespace, license, issue-verbatim, fixture-inventory, patch-replay,
protected-tree, exact workflow/job inventory and future-head checks.
The split regression/main patch followed by the source patch and the full
patch independently reproduce candidate tree
`98fae98ce9e783bed0393d35657674da09c3aa31` in temporary Git indexes.

The full source diff is three compiler files plus eight test files, based
directly on pinned main. All16 workflows, all actions/scripts/libraries and the
toolchain/dependency files retain their exact main trees or hashes. The
verbatim issue code comparison passes. Original contract-mode selection and
closure search remain unchanged below the new source-selection hook.

Synthetic publication checks accept a same-tree nonskip sibling and reject
the local candidate, main, abbreviated SHA, tree drift, merge/wrong parent,
empty/extra range, skipped ancestor and every supported skip directive. Actual
read-only CLI invocations reject the candidate, main and abbreviated SHA.
No future publication commit is created for these tests.

The arithmetic check independently enumerates safe `u8` MRE inputs and the
out-of-original-precondition example, and records the `i32::MAX + 1` overflow
endpoint. This checks the expected oracle, not compiled Rust semantics.

Compiler/typechecking, macro expansion, rustfmt, Kani/CBMC, new main/fix native
regressions, fullrunner, performance and CI remain NOT_RUN. Static source
checks and synthetic Git metadata do not establish verification success or
an independent review. Independent11 and root GO remain pending in sequence.
