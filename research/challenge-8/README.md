# Challenge 8 research

We are developing our own solution. Existing PRs are references for requirements,
review feedback and performance observations; their proof code is not imported.

## Target and scope

- Target: the standard library in this repository, not a reimplementation.
- Requirements: `doc/src/challenges/0008-smallsort.md`; discussion: upstream issue #56.
- Initial upstream commit: `dd2bbad51eb50fdf9730e14802dcaf8a9290092a`.
- Kani is pinned by `tool_config/kani-version.toml`, initially
  `152c6a8c875d9886a67e229247b4826d6105ccfd`.
- Runtime code in the standard library must not change.

## First experiment

`smoke.rs` contains two original proof harnesses for the actual `swap_if_less`:

1. For arbitrary four-element `i32` arrays, comparing positions 1 and 2 with `<`
   produces an ordered pair, preserves the exact values and leaves both neighbours unchanged.
2. For either symbolic comparator decision, those same positions preserve the
   exact values and leave both neighbours unchanged. This does not assert sortedness
   for an invalid comparator.

There are no input assumptions, behavioral stubs or copied sorting algorithms.
Reachability covers exercise less-than, equality, greater-than and both swap decisions.
These are bootstrap checks for a fixed allocation and two fixed positions. They
do not establish generic type/index coverage, comparator panic safety, uninitialized
memory safety, or the full Challenge 8 contracts. Kani's default enabled checks
apply; we do not claim that these cover every UB required by the challenge.

## Run

In the fork's Actions tab, enable workflows if GitHub asks, choose **SmallSort
research**, click **Run workflow**, select `challenge-8/research`, and leave
`proof=all` and `budget_minutes=90` for the initial cold run.

The workflow definition must exist on the default branch for GitHub to expose
the manual trigger. Its dispatch branch is the source being verified.
After a source fix, start a new **Run workflow** on the updated branch. **Re-run
jobs** on an older run checks that run's original commit and will not pick up the fix.

For a Linux machine with Rust/rustup and the required system tools:

```bash
bash research/challenge-8/run-smoke.sh all 90
```

Use a disposable checkout: the runner appends only the cfg(kani) proof module to
`smallsort.rs` at execution time. It refuses to append twice. Kani's repository
script builds the pinned verifier and installs its dependencies; that cold build
counts toward the time budget. The initial cache retains Cargo downloads only,
not a complete verifier installation.

Every run records the source commit, source checksums, runner information, Kani
pin, complete verification log, exit status and GNU time resource statistics.
The appended source is included in the artifact so the checked input is reviewable.

Success requires both requested harnesses to verify and every reachability cover
to be satisfied. A timeout, build error or absence of harnesses is not a proof.
### Run log

- [First run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37381869926),
  2026-10-06 (Europe/Moscow), source `99af1446fc89bf3792be88090eb534982d688313`:
  runner preparation and the pinned Kani 0.67.0 build succeeded. Compilation of
  the bootstrap failed with five E0433 errors: this std integration exposes
  `kani::cover` as a function, not the `kani::cover!` macro. No proof was checked.
  The five calls were changed to the function form, whose signature was checked
  in the pinned Kani source. A fresh verification run is still required.

## Next experiments

1. Confirm the bootstrap on Actions and fix environment issues before expanding scope.
2. Write our own functional specification for insertion and merge: valid memory,
   sortedness under a valid ordering, and value/multiset preservation.
3. Check whether reusable contracts can describe those primitives without changing
   generic signatures or runtime behavior; then try a small caller using summaries.
4. Expand domain and type coverage while recording assumptions and runtimes.
5. Investigate length-32 scalability, contracts on specialized trait methods, and
   uninitialized-read coverage as separate obligations. Choose VeriFast or a hybrid
   approach on evidence from these experiments.

Experiments may use a larger time budget than the upstream CI; the final solution
must remain automated and acceptable to the upstream CI and review committee.
