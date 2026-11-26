# Worker task: fix for kani issue 5232 (`<` on symbolic `bool` is unconstrained)

Issue: https://github.com/model-checking/kani/issues/5232 (ours, opened 2026-11-26, no maintainer reply yet). Read it first; it has the MRE, the expected/actual output and the root cause.

Root cause in short: Kani lowers `bool` to CBMC `c_bool` and emits `Lt`/`Le`/`Gt`/`Ge` on `c_bool` operands unchanged. CBMC 6.11.0 `boolbvt::convert_bv_rel` has no `c_bool` case, so the relation becomes a fresh propositional variable. Equality is fine; only ordering relations (and everything built on them: `PartialOrd`, `Ord::cmp`, `min`, `max`, sorting) are affected.

## Do

1. Fresh worktree `/root/kani-5232-fix-w14` on upstream `model-checking/kani` main (fetch from GitHub; current head `8c6dba5935`). Branch `fix/bool-ordering-comparison`.
2. Fix in Kani codegen, minimal and local: when an ordering comparison (`Lt`, `Le`, `Gt`, `Ge`, and three-way `Cmp` if it reaches the same path) has `bool` operands, cast both operands to an unsigned bit-vector (e.g. `u8`) before building the relation. Start from `kani-compiler/src/codegen_cprover_gotoc/codegen/rvalue.rs` (binop codegen near L1854 at 8c6dba5935) and find every path that emits these relations for `bool`, including intrinsics such as `three_way_compare` if they bypass it. Do not touch `Eq`/`Ne`. No unrelated refactors.
3. Regression test: add the issue's MRE as a Kani test that must verify (both harnesses from the issue, plus `<=`, `>`, `>=`, `cmp`, `min`/`max` on symbolic `bool`, and a covers check that `a < b` is reachable and `b < a` with `a < b` is not). Put it where similar codegen tests live (`tests/kani/...`); an `expected` test only if needed.
4. Check that nothing else emits relational ops on `c_bool` (search codegen for `.lt(`/`.le(`/`.gt(`/`.ge(` and `cmp` lowering). List findings in the handoff.
5. Local checks allowed: `git diff --check` and `/root/rustfmt-toolchains/bin/kani-fmt-check.sh`. No local cargo/rustc/Kani/CBMC. Do not push anywhere; the coordinator runs fork CI.
6. One commit, author and committer `Tiramisu-Cake <igkharin@gmail.com>`, no Co-Authored-By, Kani commit message style.
7. Write `HANDOFF.md` next to this file: commit SHA/tree/parent, diff summary, the list from step 4, and a draft PR title and body in the style of earlier small Kani fixes (short, plain; "Resolves #5232"; a Testing line placeholder; the license line "By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses."; then a final line `*Disclosure: this change and description were prepared with the help of AI assistants.*`). Commit the handoff to g0 branch `experiment/kani-k1-kani3300g0-20261111` with `[skip ci]` and no hash sign before numbers in the message, stop and report the SHA.
