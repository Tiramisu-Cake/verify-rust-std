# HANDOFF — issue #5206 review revision

One coordinator stage complete; stop with this HANDOFF. Review findings R1
and R2 are addressed by source changes and static inspection. Native behavior
remains unverified. No push or CI.

## Candidate and commit identities

- Worktree: `/root/kani-fix-5206-w13`.
- Branch: `fix/stub-contract-target-conflict`.
- Original w13 fix and sole parent of this revision:
  `e58623967899e51f9716bdb1d76b8d5bf7f80944`.
- Revision commit: `a5ebb0bf8ac2ad141f7e8f173ae5e8548948b097`.
- Subject: `Deduplicate contract stub conflicts and complete positive coverage`.
- Author and committer: `Tiramisu-Cake <igkharin@gmail.com>`.
- Revision has no skip-ci marker or Co-Authored-By trailer. Candidate is clean.
- Review read in full: [issue5206-fix-review/HANDOFF.md](../issue5206-fix-review/HANDOFF.md).

## Review findings applied

R1 (required): expanded the existing positive fixture
`tests/expected/function-contract/ordinary_stub_different_target.rs` without
changing its original discriminating `caller` control. Added a contracted
`h` returning true and three harnesses:

- `check_different_verified_target`: `stub_verified(h)` with `stub(f, g)`;
  asserts both `h()` and `f()`. Because `f` returns false and `g` returns
  true, the latter assertion requires the ordinary replacement to take effect.
- `check_reverse_contract`: `proof_for_contract(h)` with `stub(g, h)`.
- `check_reverse_verified`: `stub_verified(h)` with `stub(g, h)`.

Both reverse cases call only `h`, whose body does not call `g`. They guard
acceptance when the contracted target is the ordinary replacement value,
without exercising the separate #5204 body-source problem. The contract-proof
harness for `h` is retained in the same fixture. Its `.expected` now requires
all four harness names and four successful completions with zero failures.
No separate test file or optional duplicate-attribute regression was added.

R2 (optional in the review, requested for this revision): deduplicated
`interpret_stub_verified_attribute()` results by their resolved `def_id()`
with the existing `Itertools::unique_by` before conflict checks. This retains
first-occurrence order and emits at most one new verified-target conflict
per target per harness invocation. Existing duplicate-attribute warnings,
diagnostic wording/spans, contract-proof checking, returned stub map and
validation placement are unchanged.

The revision changes exactly three candidate files: the stubbing module and
the existing positive `.rs`/`.expected` pair; 33 insertions, 2 deletions.
All other review discussion required no change. No #5204 or transformation
files were edited.

## Validation and limits

- `git diff --check` before commit: PASS.
- Static fixture/scope checks: PASS. Original positive source is preserved
  verbatim as a prefix; four harness names each have one expectation; the
  successful completion count is four; only the intended three files changed.
- Static source inspection: resolved IDs are deduplicated before reporting;
  the different-target assertion discriminates dropped stubbing; reverse
  harness bodies avoid calling the ordinary stub's original function.
- Commit parent, author/committer, message restrictions, final diff check,
  and clean candidate status: checked locally.

Cargo/rustc/Kani/CBMC, formatter, native regressions, push and CI: **NOT_RUN**,
as explicitly required. No runtime acceptance, fresh independent review,
or new #5204 merge/runtime compatibility result is claimed. No build,
coordinator, ledger, evidence history or external publication changes.

[PR-DRAFT.md](PR-DRAFT.md) is the updated local draft for this revision,
including deduplication and the expanded testing TODO. Original author and
review packages remain unchanged. License and AI disclosure remain intact.

This HANDOFF and draft are committed separately in the documentation
worktree with `[skip ci]`, as `Tiramisu-Cake <igkharin@gmail.com>`; that
documentation SHA is reported in the final response. Next authorized stage
may review the revision and obtain native validation, including the existing
main/fix and #5204 combinations, before replacing the Testing TODO or
publishing. This HANDOFF grants no execution or publication authority.
