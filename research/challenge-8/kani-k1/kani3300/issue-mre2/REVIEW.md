# Independent static review — issue MRE v2

**Decision:** `GO_STATIC_REVIEW_ONLY`

- Baseline: `0aac16ef62da9e9d5645782d458593e5d78143ba`
- Candidate: `47616f4105697ae3b6bc9a2203b53ccdf69168df`
- Candidate tree: `4700ee944e19804dd4d7374a6635754044f9c1a3`
- Parent: the declared clean upstream baseline; candidate worktree was clean.

## Findings

No static correctness or scope blockers found. The four fixtures use two-byte `alloc` storage without unions or `MaybeUninit`; the three contract variants differ as declared, all paths deallocate after successful allocation, and the negative control performs a real volatile byte read. The seven rows predeclare five `SUCCESS` and two exact uninitialized-read `UNINIT_FAILURE` outcomes, carry the required `-Z function-contracts -Z uninit-checks -Z stubbing` flags, and bind the slice failure to `safety_check` plus a `write_any_slice` property ID. The runner validates source/tool/request/selection/metadata identities and fails closed on malformed or incomplete exports, unexpected failures, timeouts, and unknown property-ID spelling; proof credit remains `NONE`.

The workflow is limited to the new branch family, attempt 1, read-only checkout permissions, the pinned upstream tool, and the bounded build/run/fallback/upload steps. The candidate changes only workflow paths and `ch8-issue-mre2-control`; the commit author/message and sole parent match the task. The review packet diff and all eight declared dependency snapshots match their SHA256 identities.

## Offline checks

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v` — 31 synthetic/static tests passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 check_package.py static` — passed; seven rows, four source files, and workflow control-repository path resolved as expected.

## Qualification

`ALL_NOT_RUN`: no compiler, Kani, CBMC, CI, or runtime harness was executed. Expected outcomes remain source predictions; this review establishes no reproduction, B1/B2 evidence, or proof credit (`NONE`).
