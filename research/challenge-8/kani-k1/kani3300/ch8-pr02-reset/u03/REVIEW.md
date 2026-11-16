# U-03 PR-02 RESET package review

**Recommendation: GO for preparation/review handoff only.** No blocker found in the committed candidate for this bounded preparation stage. This is not authorization to dispatch, push, run CI, or claim proof credit.

## Identity and scope

- `smallsort-session review check` validated candidate `80d0d98529445088db2fd2941fe9370ba6c0eaa6`, tree `4237f7d2c8d86f28655a88824480da2e7c911b6b`, baseline `952ea771be3827a495a9c9f29ad6a015bd796fc7`, packet SHA256 `6c828b3ccc9bf353c17b936a952034c0f4d749c3de1dcf3952be587ed6add054`, and spec SHA256 `c93869867dadb17bd1e646c988fd93687724986410cdd21b745f67cd139995c0`. Tool state was `PACKET_VALID_NOT_REVIEWED`; this review supplies the independent Luna High assessment.
- Candidate is a direct child of the stated baseline. Pinned source `f7e89f1942fa6f671f20ec45fde98d9d736dc122` is a direct child of PR-02 `932fb8395a58f8c86c0d702ba2cae835823b2962`.
- Compiler diff SHA256 from PR-02 is identical for U01, U02, and U03: `f7beb5f9fc63e3a0a63536c44b922f07937d91829ecb551a3cbea3d517f232da`.
- U02→U03 source diff changes only the two requested `main.rs` files. The five other fixture directories, all expected-output oracles, scripts, and modes are unchanged. Package scope is limited to the workflow/request, package/source checks, patch, runner/docs/tests, and those two fixture files; B runner and issue fixtures are unchanged.

## Findings

- The negative fixture reads offset 1 from a `#[repr(C)]` `{ u8, u32 }` object with both fields initialized; the companion writes and reads that same offset in place. This matches the pinned x86_64 padding intent. Existing oracles still require negative `FAILURE` with the uninitialized `u8` safety-check description and companion `SUCCESS`. See [negative fixture](/root/kani-fix-ch8-pr02-reset-u03-source/tests/script-based-pre/autoharness_entry_reset_uninit_read/main.rs:4), [companion](/root/kani-fix-ch8-pr02-reset-u03-source/tests/script-based-pre/autoharness_entry_reset_initialized_read/main.rs:4), and their unchanged `expected`/`run.sh` files.
- The A runner preserves fmt, source build, clippy, compiler units, compiletest build, both expected slices, focused reset autoharness slice, generic autoharness slice, and old-controls. After a successful source build it continues through every gate, captures each gate’s exit in its bounded receipt, and returns an aggregate failure. A failed source build leaves dependent gates unrun. Old-controls is last in the runner. See [runner](/root/kani-fix-ch8-pr02-reset-u03-ci/scripts/ch8-pr02-reset/run_arm_a.sh:11).
- Workflow keeps A-only execution, first-attempt/same-tree gate, dedicated push pattern, max-parallel 1, 120-minute cap, jobs/threads 2, and bounded finalize/upload. Explicit `always()` conditions let the A runner start after successful apply/setup/gate despite structure-test, runner-test, or old-build failure, while the job retains prior step failures. See [workflow](/root/kani-fix-ch8-pr02-reset-u03-ci/.github/workflows/ch8-pr02-reset.yml:95).
- The two new synthetic tests exercise success, each gate failure (including build prerequisite), combined failures, missing compiletest executable, receipt exits, and NOT_RUN state. No source/Kani/CBMC binary is used.

## Checks performed

- Package static checks and source-structure checks: PASS.
- Existing B result tests (5), A receipt tests (2), and new A gate runner tests (2): PASS.
- Isolated PR-02 and SEL1 patch applications: PASS; the patch script verified their declared patched trees. No source worktree was modified by these checks.
- Runtime fixture outcomes remain NOT_RUN. U01/U02 outcomes remain task-reported context; static and synthetic checks establish no proof credit.
