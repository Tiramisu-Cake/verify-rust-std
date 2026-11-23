# Diagnostics next stage: base comparison and SLICE fixture

Read first: DIAG-RUN-45163409005-ANALYSIS.md (g0 73fb12996f), DIAG-PLAN.md, DIAG-HANDOFF.md, DIAG-FIX2-HANDOFF.md.
Repository: /root/kani-ch8-kani5196-diag-control-20261123, branch ch8-kani5196-diag-control, head 5b5aa3cb61.
Author for commits: Tiramisu-Cake <igkharin@gmail.com>, control commits end with [skip ci], no '#' followed by a number
in any message. No pushes. No cargo, rustc, Kani, CBMC or Miri locally; Python unit tests of the control are allowed.

Prepare two independent, frozen dispatch candidates (each its own trigger commit made with git commit-tree on
467af9cb8d, on local branches ch8-kani5196-diag-base and ch8-kani5196-diag-slice2). Each will be one fork run on the
same workflow and ref, one at a time.

## A. Base comparison (branch ch8-kani5196-diag-base)

Same standalone fixtures, selectors, OFF/ON flags and checker settings as run 45163409005, but the tool pin is the
merged Kani main commit 5d80a641d333c929e00ed1e1255c637265f15749 (parent of da0406b78 in the PR series), as named in the
analysis. Verify from the pinned checkout /root/kani-5196-uninit-tool-20261122 (read-only git commands only) that its
toolchain and dependency pins match the head and that it accepts the -Z uninit-checks flag. Roster: CAL-POS, CAL-NEG,
ITER OFF/ON, ITER-INIT OFF/ON, SELECT OFF/ON, SELECT-INIT OFF/ON (10 roots). Recompute the time envelope for this
roster. Everything else in the run contract stays as reviewed.

## B. SLICE fixture fix (branch ch8-kani5196-diag-slice2)

Tool pin stays at the PR head bcdc1a0f8d. Change only the shared SLICE observer as the analysis recommends: assert
src.len() == WORDS and compare the eight u64 elements with individual indexed assertions at both observer sites, so
no memcmp loop is emitted; keep allocation, raw-slice modifies, initialization, covers and OFF/ON flags. Roster: CAL-POS,
CAL-NEG and the six SLICE roots (8 roots). Fix the binder anchors so that each mode uses its own rooted anchor, as the
analysis notes for Replace. Also constrain the select_call matcher to the direct typed public call at its source
coordinate and accept the mangled MaybeUninit receiver form for assume_init_read, as the analysis describes; keep
negative tests for both.

## Both

Update the frozen request, payload hashes and tests; run the synthetic tests the way the workflow step does, for both
triggers. Write DIAG-NEXT-HANDOFF.md next to this file with: diff summary, test commands and results, control heads,
trees, trigger SHAs, rosters and envelopes. Commit it in the g0 worktree with [skip ci]. Stop after the handoff.
