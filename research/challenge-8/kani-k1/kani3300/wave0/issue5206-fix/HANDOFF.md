# HANDOFF — issue #5206 offline implementation

Stage complete; stop here. Implementation and static checks only. No push or CI.
Read upstream issue with `gh issue view 5206 -R model-checking/kani`.

## Candidate

- Worktree: `/root/kani-fix-5206-w13`.
- Branch: `fix/stub-contract-target-conflict`.
- Fetched upstream main/base: `0997d11c14cb2da0824efc34e2c4001e53ac0faf`.
- Fix commit: `e58623967899e51f9716bdb1d76b8d5bf7f80944`.
- Exactly one commit above main, authored and committed by
  `Tiramisu-Cake <igkharin@gmail.com>`.
- Subject: `Reject ordinary stubs of contract targets`.
  No skip-ci marker or Co-Authored-By trailer. Source worktree is clean.

`kani-compiler/src/kani_middle/stubbing/mod.rs:39` checks resolved original
function IDs in `harness_stub_map` against this harness's `proof_for_contract`
and `stub_verified` targets. Only an overlap emits an error; the stub map is
unchanged. Qualified paths resolve to the same identity. Diagnostics use the
harness span, as existing stub resolution and compatibility errors do.

`codegen_units.rs:251` calls this before grouping/transitivity;
`validate_units` aborts on errors at line 325. `CodegenUnits::new` completes
before `BodyTransformation::new` in the CPROVER and LLBC backends. The fix
does not depend on #5204 and edits none of its transform files.

## Tests added

- `tests/ui/function-contracts/ordinary_stub_target_conflict.rs` has the two
  conflicting harnesses. The ordinary stub uses `crate::f` in the verified
  case. A proof-for-contract harness exists for `f`, avoiding the unrelated
  missing-contract-proof error.
- Its `.expected` requires both complete diagnostic texts and
  `error: aborting due to 2 previous errors`.
- `tests/expected/function-contract/ordinary_stub_different_target.rs`
  proves `caller` while stubbing its uncontracted callee `f` with `g`.
  `f` returns false, `g` returns true, and `caller` ensures true: the control
  requires the replacement to take effect. Its `.expected` requires success
  and a one-harness successful completion.

Main supports the distinct-target control by source inspection: ordinary
stubs replace the uncontracted callee, while contract instrumentation applies
to `caller`. Execution remains unverified. Compiletest uses independent
substring blocks, so the negative expectations tolerate harness iteration
order; they are exact message texts, not an exact transcript oracle.

## Static validation and #5204 compatibility

`git diff --check HEAD^ HEAD`: PASS. Commit scope: five files, 74 insertions.
The parent is the fetched main; no #5204 commit is in the candidate's ancestry.

`git merge-tree --write-tree` results, both exit 0 with no conflicts:

- Base main + #5204 head `b3019ab3f9c83a25cd4d870e49e49121b3327bb1`:
  tree `ff09d83ed7a12a04458f91cbcd7a76410011a9f5`.
- Candidate + the same #5204 head:
  tree `0ab16585785ea831d572c48530c5614d0df4b33f`.

Comparing those trees yields exactly this candidate's five-file change.
`transform/{contracts,stubs,mod}.rs` are identical between the two merge
results, and all five candidate files are identical between the candidate
and its merge result. Main already includes #5008 changes in `contracts.rs`,
so the baseline merged tree, rather than the older PR head alone, is the
correct preservation comparison. #5204's worktrees, branches and PR were
not changed; no actual merge or cherry-pick was performed.

Cargo/rustc/Kani/CBMC, formatting tools, native regression execution and CI:
NOT_RUN. Independent review: NOT_RUN; the required Luna High helper model is
not available. No proof credit is claimed. No external writes, push,
coordinator, build, ledger or historical evidence changes occurred.

[PR-DRAFT.md](PR-DRAFT.md) contains the title and local PR body draft.
Future authorized work: review the exact candidate, run both new test files
on main and with #5204, and replace the testing placeholder with actual
results before publication. This HANDOFF grants no build or publication
authority. Its containing documentation commit uses `[skip ci]`; that SHA
is reported with the fix SHA in the final response.
