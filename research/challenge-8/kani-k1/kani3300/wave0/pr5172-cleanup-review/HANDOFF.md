# HANDOFF — independent review of PR5172 cleanup

**Verdict: APPROVE.** No required changes found in the cleanup candidate or the proposed PR description. This verdict covers the requested offline cleanup review; it does not establish successful compilation, native regression outcomes, CI acceptance, or proof credit. One stage complete; **STOP WITH HANDOFF**.

Reviewed candidate `/root/kani-pr5172-cleanup-w11`, branch `cleanup/pr5172-20261119`, commit `fef46d2d9d65bf3eb91a282da004043ecd26a208`, tree `2e6c41da31c3e5a96a9a7d39efa8eb93e6c973e7`. Its sole parent is the pinned PR head `80e5d6fabc0103b0b3117440007ad2d9475f9a9c`; it is exactly one commit above that head. The candidate worktree was clean and was not modified.

The actual diff, compiletest implementation, affected fixtures, compiler context, author package, and original recommendations were inspected. Preservation was checked with a newly written [static_review.py](static_review.py), independently of the author's checker and receipts. Its [STATIC-REVIEW.json](STATIC-REVIEW.json) records PASS, exact identities, per-harness body hashes, effective oracle paths/hashes, and the complete change scope. All Kani source citations below refer to the pinned candidate and are relative to its worktree.

## Harnesses and standalone source structure

All **24 harnesses in the same 22 source roots** remain: eleven plain/seeded pairs, with two harnesses in each generated-positive source and one in each other source. All eleven plain files are byte-identical. In every seeded file, replacing the new path module with the original helper and changing the qualified helper calls back to `seed()` reproduces the entire parent source exactly. This checks attributes, flags, custom MIR, statements, assertions, initialization distinctions, and call positions, rather than relying on counts alone.

The bodies are therefore unchanged **apart from the explicit helper-call qualification**. They are not literally byte-identical: all twelve `seed()` calls became `analysis_target::check_byte_copy()`. No harness was merged, renamed, removed, gated off, or moved between compilation roots. Both `generated_function_item` and `drop_closure_glue` remain independently marked harnesses (`tests/expected/uninit/unresolved-calls/generated-positive-seeded.rs:28`, `:34`).

The helper preserves the original four operations, comment, and `#[inline(never)]`; its only necessary interface change is `pub fn check_byte_copy()` (`tests/expected/uninit/unresolved-calls/auxiliary/analysis_target.rs:4`). It has the standard copyright/license header, uses only `std`, has no proof attribute, and is imported only by the eleven seeded roots. Every seeded harness calls it once, at its original location.

The wiring matches what compiletest actually supports:

- Expected mode goes through the Rust-source collector (`tools/compiletest/src/main.rs:376`) and runs `run_expected_test` (`tools/compiletest/src/runtest.rs:83`).
- Each eligible `.rs` becomes a separate test (`tools/compiletest/src/main.rs:501`); recursive discovery explicitly skips directories named **`auxiliary`** (`:514`). The helper is consequently not collected as an extra standalone test.
- Each root uses Rust's explicit `#[path = "auxiliary/analysis_target.rs"] mod analysis_target;`, for example `generated-positive-seeded.rs:25`. This includes the module in that root's crate; it does not require a separately built auxiliary crate or an `aux-build` directive. An existing repository example uses the same mechanism (`tests/ui/coverage-spaces/test.rs:6`).
- `run_kani` forwards that one original source path and its own Kani flags (`tools/compiletest/src/runtest.rs:363`) and forwards compile flags through `RUSTFLAGS` (`:355`). Header flags are read from that root (`tools/compiletest/src/header.rs:53`).

Thus every test retains a complete, independently invocable source with its local module available; plain and seeded inputs remain separate compilations. Actual compilation was NOT_RUN under the task restriction. Static inspection cannot certify the compiler's post-relocation output or emitted MIR/InstanceKind.

## Expected files and retained obligations

The directory fallback is real: `run_expected_test` first selects `<stem>.expected`, then sibling `expected` only when the named file is absent (`tools/compiletest/src/runtest.rs:488`). The cleanup removes exactly eight byte-identical named files, for erased-pointer, fn-pointer, global-escaped, and wrapped-pointer, each plain/seeded. Their shared `expected` is byte-identical to every removed file. The other **14 named files retain precedence and identical bytes**. For all 22 roots, the effective oracle after cleanup equals that root's previous oracle byte-for-byte.

The matcher reads the selected file (`tools/compiletest/src/runtest.rs:528`). A trailing backslash binds adjacent substring lines (`:564`); other groups can occur anywhere (`:591`). Sharing the same bytes across separate runs preserves those exact checks and their limitations. In particular:

| Retained cases, each plain and seeded | Required result retained |
| --- | --- |
| direct | One successful harness; ordinary direct-call acceptance |
| generated-positive | Both named successful harnesses; total two, no failures |
| entry-initialized | `indirect.safety_check` bound to SUCCESS and the `u32` description, plus unsupported-call FAILURE |
| entry-partial | The same safety property bound to FAILURE and the `u32` description, plus unsupported-call FAILURE |
| pending-ops | Operand safety property bound to FAILURE and its pointer description, plus unsupported-call FAILURE |
| virtual | Trait-object-specific unsupported FAILURE |
| fn-trait-pointer | Its existing `Failed Checks:` function-pointer diagnostic |
| erased-pointer, fn-pointer, global-escaped, wrapped-pointer | Adjacent FAILURE status and exact function-pointer unsupported description |

Every case still requires its verification verdict and complete harness summary. The initialized/partial status distinction remains explicit (`entry-initialized-seeded.expected:2`, `entry-partial-seeded.expected:2`), as does the pending operand failure (`pending-ops-seeded.expected:2`). No distinctive oracle was replaced with a generic failure check. Git's displayed 100% rename accounts for one of the eight removed names; independent scope checks used `--no-renames` to account for both endpoints.

## Compiler comment, deferred adapter, and guards

The **only compiler change is the two-line comment at `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs:409`**. Reversing that exact substitution reproduces the entire parent file byte-for-byte. The whole-tree diff contains no other compiler, driver, library, or compiletest edits.

The new comment correctly describes the allocation models in the following foreign-item branch and union argument-state stores in the non-foreign branch (`uninit_visitor.rs:411`, `:437`). The branch emits `MemoryInitOp::StoreArgument` (`:444`), with no return-state transfer. Removing the previous claim about return-state transfer is accurate.

The single-use adapter remains **DEFERRED**, consistent with the coordinator's recorded decision to avoid code churn during review. Both its call at `uninit_visitor.rs:282` and its definition at `:762` are unchanged. The separate initial-target adapter and its `.ok()` policy are also unchanged (`delayed_ub/initial_target_visitor.rs:130`).

No fail-closed guard or safety operation was weakened:

- Shim entry argument/result rejection remains (`uninit_visitor.rs:69`), as does call-site argument/destination rejection (`:291`). The recursive classifier and conservative unknown-type result remain (`:774`, `:797`).
- Operand visitation still precedes fallible resolution (`:280`); failure still queues Unsupported and breaks to the common terminator epilogue (`:285`, `:498`), preserving prior entry loads and operand operations.
- The shared resolver still rejects function-pointer, virtual, bodyless, and LLVM-intrinsic cases and uses `checked_body` for supported Item/Shim instances (`kani-compiler/src/kani_middle/points_to/points_to_analysis.rs:350`).
- Unsupported code generation retains `codegen_assert_assume_false` (`kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs:230`, `:240`).

The original recommendation's missing shim-rejection negative fixtures remain a previously recorded coverage gap, outside this cleanup. They were neither silently dropped nor claimed as newly covered. This review does not establish the emitted kind of a generated shim or a new soundness result.

## Proposed PR description

[PROPOSED-PR.md](../pr5172-cleanup/PROPOSED-PR.md) is accurate and concise (152 whitespace-separated words). It describes the resulting PR behavior, retained call/entry operations, shared resolution, shim limitation, separate fixture compilations, and static-only validation. Its testing paragraph explicitly says native regressions and CI have not run for this cleanup revision; it does not promote historical CI to current evidence or assert literal body identity. No wording changes are required.

The license confirmation and AI disclosure lines were compared against `open-pr-slop-inputs-20261119/pr-5172/PR-BODY.snapshot.md` and match exactly. Both remain intact. The author package and proposed description were left unchanged.

## Validation and stop boundary

PASS: independent source/byte preservation script, exact parent/branch/HEAD/tree/change-scope checks, candidate worktree cleanliness, effective oracles for every source, disclosure comparison, and `git diff --check` for the candidate. Only the new review directory is committed in the packaging repository, with `[skip ci]` and author/committer `Tiramisu-Cake <igkharin@gmail.com>`; its SHA is reported outside this file to avoid a self-reference.

NOT_RUN: cargo, rustc, rustfmt, Kani, CBMC, compiletest execution, native regressions, CI. No push, remote/PR write, build submission, raw CI evidence access, ledger change, or delegation occurred. No proof credit is claimed. The review is complete and stops here with HANDOFF; it does not start publication or another stage.
