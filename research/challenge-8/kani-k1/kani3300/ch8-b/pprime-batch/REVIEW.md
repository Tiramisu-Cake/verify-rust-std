# Independent review — B P-prime batch candidate

- Baseline: `4d7e34383a3af504a261228fdee59e6c7093e633`
- Candidate: `99dbb2157bdb4f0322bcb3677f4ee51991de2f28`
- Candidate tree: `10421f334c1a90b723dde5378678b0439f862125`
- Packet diff SHA256: `15b7377bdc1511efd265ee745dd1d6b0413b4382556d18d8f1904952c17a6903`
- Review scope: static package-readiness review only. Runtime Kani/compiler/CBMC is **NOT_RUN**; no proof credit is established.

## Review result

No blocking defect found in the reviewed batch runner against the stated B package scope. Frozen `roots.json` is byte-identical to baseline. The runner constructs one `verify-std` invocation with all 235 exact selectors, `--jobs=1`, the 600-second Kani harness timeout, and one export path. The pinned Kani source confirms that `--harness` is repeatable, exact matching checks each requested filter, the export marker is written after project construction and target selection, and Kani exits nonzero when any harness result fails.

Per-row classification binds an export entry by unique exact harness name, `core` crate, manual-harness status, pinned Kani SHA/clean state, and requested target triple. It validates the selected harness's completed outcome, checks/covers partitions, failure IDs, row class/oracle, wrapper stop, and the group exit against all exported harness outcomes. Missing/duplicate/unexpected entries and malformed or incomplete exports become unknown; wrapper timeouts/stops cannot yield PASS. A completed, uniquely bound row may retain its own diagnostic class in a valid `PARTIAL` group export; missing rows and the overall census remain partial. This is consistent with the reviewed per-root evidence contract.

## Limitations retained by design

- A synthetic mutation of `contract.contracted_function_name` to another well-formed string still classifies as PASS. The runner validates this source-reported `AssignsContract` field's shape, not an expected value. The frozen B manifest has no contract-target oracle, and this package explicitly makes no independent contract-target-binding claim; treat this as a metadata boundary, not established target binding.
- The wrapper's theoretical group cap is 143100 seconds (2100 + 235×600), while the workflow job timeout is 210 minutes. The external job ceiling can interrupt a group that remains within its wrapper cap. The documented result is PARTIAL with seeded NOT_RUN rows, not a promise that every worst-case per-root envelope fits the host job. This is a scheduling limitation for eventual completeness, not a false-PASS path.
- Per-root RSS remains `UNKNOWN`; only sampled aggregate process-tree RSS is reported and capped. Sampling can overshoot between intervals.

## Validation performed

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/ch8-b-census -v` — 17 tests passed.
- `PYTHONDONTWRITEBYTECODE=1 python3 scripts/ch8-b-census/static_check.py` — PASS.
- `/tmp/kani3300-d0-ci-tools/actionlint -shellcheck= .github/workflows/ch8-b-census.yml` — PASS.
- `git diff --check 4d7e34383a3af504a261228fdee59e6c7093e633..99dbb2157bdb4f0322bcb3677f4ee51991de2f28` — PASS.
- Static source inspection only; no cargo, rustc, Kani, CBMC, workflow, CI, publication, push, or ledger action was run.
