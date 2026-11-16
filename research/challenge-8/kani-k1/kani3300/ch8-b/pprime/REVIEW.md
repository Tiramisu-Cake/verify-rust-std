# B P-prime candidate review

## Identity and disposition

- Candidate: `4d7e34383a3af504a261228fdee59e6c7093e633`; tree `18796b2baeee695aa180c4f8e83da2009f179df6`.
- Baseline: `0aac16ef62da9e9d5645782d458593e5d78143ba`.
- Final packet diff SHA256: `21a591c13ad996a4cb1a70cd2140b97a443a12cce111eac2f5e35404584de1ed`.
- **Review: READY for coordinator consideration.** No blocking static defect found. This is not CI admission, a dispatch GO, or proof credit.

## Findings

- The final candidate is the requested P-prime rebase. The host workflow pins verify-rust-std `c5ff36ff433692140605891f646043f991db05de` and pristine `model-checking/kani` `0aac16ef62da9e9d5645782d458593e5d78143ba`; request tree pins are consistent. The g0 source audit reports 235 unchanged root names/modules and 16 byte-identical source files. `roots.json` SHA256 is `7dee264da4c0afecb75e55b962520a1f14d5ef569a9bd1ca51ad70d206f78a85`, matching the request; shard counts remain 183/52.
- The runner invokes direct exact per-root `verify-std` selectors and does not run `kani list` or `scripts/run-kani.sh`. It retains the 600-second root cap, 6-GiB root RSS cap, bounded receipts, and fail-closed unknown/partial classification. The workflow uses sibling `control`, `export`, and `std` checkouts and the exact export checkout's setup action. The prior B candidate's added push triggers on unrelated workflows are absent; the candidate control checkout keeps only the dedicated census workflow, while the separate pristine export checkout is unchanged.
- The final amendment from `44f528237653b986ae3dcc44e682dc21e6a6eb03` removes the in-workflow `static_check.py` invocation, avoiding a PyYAML dependency in CI. The offline static check remains available and passed locally. The workflow still runs the 13 standard-library synthetic tests.
- No execution of Cargo, rustc, Kani, or CBMC was performed. All 235 runtime rows remain `NOT_RUN`; no proof credit is established.

## Checks performed

- Final packet validator: `PASS_STATIC_ONLY` (candidate identity, 235 roots, 16 source files, manifest hash, no global inventory, no proof credit).
- `static_check.py`: PASS.
- 13 isolated synthetic tests: PASS.
- `actionlint -shellcheck= .github/workflows/ch8-b-census.yml`: PASS.
- `git diff --check` baseline-to-candidate: PASS; candidate worktree clean.

## Limitations

This review establishes static package consistency and runner-control behavior only. It does not establish actual compiler/harness binding, runtime completion, proof acceptance, cross-OS behavior, or proof credit. The coordinator must independently apply current slot, ledger, and authorization controls before any trigger or CI run.
