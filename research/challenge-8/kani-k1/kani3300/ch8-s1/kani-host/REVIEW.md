# CH8 S1 Kani-host migration review

- Candidate: `36db70978a16144624abf94d480a593dae684451`
- Candidate tree: `f3d36d51f58bf7937f6f8778260e3e2816996b48`
- Parent: `0aac16ef62da9e9d5645782d458593e5d78143ba` (single parent)
- Packet: `/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-s1/kani-host/review-packet`
- Packet inventory SHA256: `e0954d1c62daa47aabec3c38c549ba3e6f0d0cb5b1bb23955ee6aef00b4aa8b1`
- Spec SHA256: `b3c3d812ed5dae708a0a6a9c521e8b78a76cb3e77271334ee0edf699bf94c3aa`

## Findings

No migration-scope blockers found. The commit changes only `.github/workflows/` and `ch8-s1-control/`; the only remaining workflow is `ch8-s1.yml`. The workflow is push-only for `uninit-ci/ch8-s1k-*`, guards `Tiramisu-Cake/kani`, checks out control at `github.sha` with depth 2, and pins the production std export and upstream Kani tool through the immutable request. The static checks bind those repositories, sibling checkout paths, submodules, fetch depth, and keep `runner.*` context references in step `env` only. Runner source checks enforce the pinned source SHAs/trees, clean checkouts, and cwd-resolved sibling layout.

Host control checks bind repository/event/ref/run attempt, control HEAD to `GITHUB_SHA`, exact tool parent and one-parent history, changed-path inventory/payload hashes, and the sole workflow. `runner.py`, `test_runner.py`, and both activation patches are byte-identical to original control `f88bf3f0ea0ef1f87ca01ba5da11b57be574adf1`. All request JSON fields other than the host-derived `ci_changed_paths` and `ci_payload_sha256` match; the request retains all 23 rows and each is `NOT_RUN`.

## Validation

- `actionlint` on `.github/workflows/ch8-s1.yml`: passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_runner.py test_package.py`: 16 tests passed, including YAML sensitivity, host identity/path guards, and original runner error paths. Build wrapper execution was mocked; no toolchain command ran.
- No cargo, rustc, Kani, CBMC, build runner, push, CI, publication, ledger, or raw evidence log was used.

## Decision

Approved for preparation-only handoff. This review grants no proof credit or dispatch authorization. All 23 proof rows remain `NOT_RUN`.
