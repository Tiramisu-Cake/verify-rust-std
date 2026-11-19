# HANDOFF — PR #5172 Copilot fixes

2026-11-19. Coordinator task, one stage; implementation complete, stopped at HANDOFF.

- PR: https://github.com/model-checking/kani/pull/5172
- Remote PR branch: `Tiramisu-Cake:fix/kani-uninit-unresolved-call-v3`; unchanged.
- Verified base/head: `ac0304a8bfde3002ef0411ae0e73f94ce0cd7878`, the maintainer's merge of main `0997d11c14cb2da0824efc34e2c4001e53ac0faf` into the PR.
- New worktree: `/root/kani-pr5172-copilot-w15`.
- New local branch: `fix/pr5172-copilot-20261119`.
- Code commit: `cea872ac973f98daef320e056987b6d5365d9e8b` — `Fix shim type inspection and reuse checked call bodies`.
- Author and committer: `Tiramisu-Cake <igkharin@gmail.com>`. Code commit has no skip-ci marker or Co-Authored-By trailer.
- Diff: two source files, 31 insertions and 25 deletions. No rebase, push, CI, compiler, Cargo, Kani, or CBMC execution. Replies below are drafts only; nothing posted.

## Compile fix and API sweep

In `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs`, changed `field.ty(tcx, args)` to `field.ty(tcx, *args)`, preserving `.skip_normalization()`. Matching `ty.kind()` borrows the generic arguments; the updated `FieldDef::ty` needs their value.

Reviewed the PR's six changed compiler files against the merged main parent, including their added rustc-facing calls. Grepped the changed code and neighboring compiler code for field/type calls and generic-argument handling. This was the only added `FieldDef::ty` call needing this adjustment. Merged main already has the analogous `.ty(tcx, *args).skip_normalization()` in `kani-compiler/src/kani_middle/intrinsics.rs` (`simd_len_and_type`). No other instance of the same mismatch was found.

`rust-toolchain.toml` pins `nightly-2026-11-18`. `/root/.rustup` does not exist; the usual shared rustup/Rust source locations checked were also absent. Direct comparison with that nightly's installed rustc_middle source was therefore unavailable. This is a static API sweep, not a claim that the whole compiler builds.

## HIGH: repeated shim type inspection

Comment: https://github.com/model-checking/kani/pull/5172#discussion_r4633384394

`shim_type_may_carry_shadow` now creates a fresh `HashSet<rustc_middle::ty::Ty>` for each classification. Every recursive edge passes the same set, and a repeated type returns false before inspecting its fields again. All type-kind decisions, field instantiation, pointer/reference boundaries, and conservative handling of unknown types remain unchanged. Each distinct type's match/children are inspected once; expected work is O(V + E) for the visited type graph, including repeated incoming edges. For `T(n+1) = (Tn, Tn)`, this makes traversal linear in the number of levels.

Soundness: traversal combines children only with short-circuiting `any()`/OR, or directly returns a child's answer. If any inspection returns true, that result propagates immediately to the classification's root; no later repeated visit can suppress it. A type seen again during a continuing traversal has already evaluated to false. An in-progress ancestor cannot be encountered through valid by-value storage because by-value cycles are impossible; pointers and references are leaves. Thus returning false for a repeated type preserves the original Boolean result. The set is local to one root, so results are not shared across classifications or compiler contexts.

## MEDIUM: discarded checked bodies

Comment: https://github.com/model-checking/kani/pull/5172#discussion_r4633384489

Call-path analysis at the specified head:

- There are two actual direct `resolve_call` call sites, rather than four: `PointsToAnalysis::apply_primary_terminator_effect` and the local visitor's `try_resolve_instance` wrapper. The imports/re-export are not calls. `InitialTargetVisitor` has its own separate fallible `Instance::resolve`; delayed-UB instrumentation no longer calls the shared resolver.
- The local visitor calls its wrapper once per visited call terminator. Different call sites can resolve to the same callee instance.
- Points-to calls the resolver on every call-terminator transfer. Fixpoint iterations can revisit a block; result-cursor seeks can replay effects; every regular call transfer recursively starts another callee analysis. Multiple harnesses/call sites add more analyses. There is no once-per-instance bound or per-instance cache here.
- Before this patch, each successful non-foreign regular call transfer requested `checked_body` twice: once in resolution and once in `apply_regular_call_effect`. For N such transfers to an instance, those paths alone made 2N requests, plus local-visitor and other body-loading requests. `checked_body` explicitly scans blocks for tail calls when `instance.has_body()` is true, then calls `instance.body()`. Lower-level caching does not remove that explicit scan.
- `report_tail_calls` returns silently for an empty span list. Otherwise it emits the body's tail-call errors and immediately calls `abort_if_errors`, before stable MIR conversion. The first nonempty scan aborts compilation, so a later duplicate request does not emit another copy of those diagnostics. Shims with definition-level `has_body() == false` skip this scan.

Implemented the small body-reuse option: `resolve_call` returns `(instance, Option<checked body>)`. Intrinsics and foreign items retain their existing special paths and return no body. Accepted ordinary items/shims return the same body that established availability. Points-to passes that body to `apply_regular_call_effect`, which converts it to internal MIR without a second lookup. The local visitor maps the result back to the instance. Resolution failures still leave the accumulated points-to graph unchanged; rejection reasons and the tail-call guard remain intact.

This reduces 2N checked-body requests to N on the regular-call transfer path. It does not cache across dataflow iterations, callers, or harnesses. A broader per-instance body cache remains a possible follow-up after profiling. A definition-level `has_body()` shortcut was rejected because it excludes generated shims; a new instance-availability predicate would need checking against the pinned bridge/toolchain implementation. Returning the already checked body avoids that API assumption and extra cache state.

## Validation and test decision

`git diff --check` passed before commit and for the committed patch. Reviewed the complete two-file diff, every recursive `inspect` edge, both resolver callers, the ordinary/intrinsic/foreign/bodyless branches, and the tail-call helper. The new branch is directly based on the required merge commit; its worktree is clean after the code commit.

No regression fixture added. This is a traversal-work regression: a small tuple fixture passes with both algorithms and does not enforce a visit bound. A sufficiently deep fixture needs a generated-shim route and a reliable runtime/visit bound, and can also stress unrelated type handling. Neither that route nor its output can be verified under the explicit no-compiler/no-Kani restriction. A compiler-context visit-count test or separately validated performance case is a better follow-up. Existing generated-shim/unresolved-call tests are unchanged. No build, formatter, test execution, performance measurement, or independent review is claimed.

Next owner: review the local code commit, then arrange separately authorized compilation and targeted regression checks on nightly-2026-11-18 before deciding on publication. This task authorizes no push or CI. Stop here.

## Draft reply — HIGH

Added a visited set of rustc types, shared by all recursive calls within one classification. Shared fields are inspected once. Returning false for a repeated type preserves the result: a true result short-circuits to the root immediately, and valid by-value storage cannot cycle. The type-kind decisions are unchanged. This reduces the nested-tuple traversal to linear work in its distinct types and edges.

*Disclosure: this comment was prepared with the help of AI assistants.*

## Draft reply — MEDIUM

The resolver now returns the checked body with the instance, and points-to analysis reuses it in `apply_regular_call_effect`. This removes the second body request and tail-call scan per regular-call transfer. The tail-call diagnostic aborts on the first nonempty scan, so repeated requests did not duplicate it. Iterations can still repeat body checks; caching across analyses can follow after profiling.

*Disclosure: this comment was prepared with the help of AI assistants.*
