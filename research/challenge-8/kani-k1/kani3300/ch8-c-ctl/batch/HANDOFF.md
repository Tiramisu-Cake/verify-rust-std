# C controls batch runner candidate

Status: local skip-ci preparation candidate committed; no build, CI, Kani, CBMC, proof, or dispatch was run. The eight frozen C rows remain NOT_RUN and proof credit is NONE. This is correctness verification preparation.

## Identities

- Coordinator batch requirement input: g0 commit `82cc48368e`.
- C source/control base: `cdd3c6d04112cc1b1e1a80a850389236647bc849`.
- Revised candidate: `64ec781bc119279ccc4365aa831d2a9d0a792fee`, tree `33e95dc779cefde33132f8e265d9588b9d905b14`, branch `uninit-ci/ch8-c-ctl-w14-pprime`; parent is previous candidate `d095a7eeca5c56d1664f852c54161c720a2991cc`. Commit message has `[skip ci]`.
- Frozen std source: `d073585946093071b696eada41b8c8cac18362a7`, tree `e8e9fa63b59ff886077e938d40cffe7ce8c12d42`; frozen P′ base: `c5ff36ff433692140605891f646043f991db05de`, tree `1302063846873aa300f8bac64fe09e8a3ed1280f`.
- Frozen tool: `0aac16ef62da9e9d5645782d458593e5d78143ba`, tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`.

The eight selectors, source hashes, expected results/classes, unwind values, cover requirements, mode/target rows, flags, and oracle source are unchanged. Scheduler fields and CI payload integrity digests were refreshed. The frozen P′ base is now read from the request for `source_under_test`.

## Runner and scheduler

- The `inventory` stage seeds selectors and expected source targets offline from the frozen CI request. It invokes no Kani global list command and makes no independently observed target-map claim. Run preflight checks request identity and the frozen group inventory.
- Seven unwind-8 selectors share one `verify-std` invocation; the unwind-12 selector uses a second. Each uses repeated `--harness`, `--exact`, `--jobs=1`, one export JSON, and `--harness-timeout 600s`.
- PFC binding is directly `exported attributes.kind.ProofForContract.target_fn == row.target`, plus a nonempty `contract.contracted_function_name` (the pinned stock schema's generated closure name). Every C harness must be explicit/manual (`is_automatically_generated == false`) in crate `core`. The export target triple, 600-second harness timeout, full checks configuration, unstable feature set, tool identity, contracts, outcomes, checks, covers, and failed-property inventory are validated.
- Export paths must be fresh; a pre-existing group export is rejected, preventing stale INCOMPLETE markers from satisfying the compile boundary. In the pinned tool the fresh atomic INCOMPLETE marker is emitted after std build/target discovery and before harness checks. Its identity, target, timeout, and requested selectors are checked. A bounded compile receipt is persisted at that boundary with the marker SHA-256 and immutable head/tail snapshots (up to 4 KiB each per stream); later verifier output cannot alter the snapshot. Both marker and terminal export parsing check file size before reading.
- Each group wall cap is the sum of row budgets plus a 900-second compile cap: 5,100 seconds for the seven-row group, 1,500 seconds for the one-row group, and 6,600 seconds total. The workflow run step is 112 minutes; the job ceiling is 150 minutes. Request budgets record run step 6,720 seconds, setup 1,800, reserve 300, and job 9,000 seconds (180 seconds remain inside the ceiling).
- Aggregate expected exit follows the final export: all selected harness outcomes SUCCESS requires exit 0; any FAILURE/TIMEOUT/OUT_OF_MEMORY/CRASHED outcome requires exit 1. A wrong exit, process timeout/cap/signal, missing or incomplete export, or pre-existing marker keeps group and batch `complete=false`/PARTIAL. A valid row observation remains in that row's receipt with `complete=false`; absent/incomplete roots remain UNKNOWN. Group RSS peak is sampled/reported, per-root RSS is UNKNOWN, and the dynamic cap does not exceed `min(12 GiB, MemAvailable - 2 GiB)`.

## Validation

- Python compilation of runner and package scripts — PASS.
- `python3 -m unittest discover -s ch8-c-control -p 'test_*.py'` — PASS, 33 synthetic tests.
- Frozen request load and 7+1 grouping check — PASS.
- `git diff --check`, payload digest checks, and semantic request comparison (all non-digest request fields unchanged) — PASS.
- Parsed comparison confirms frozen row/oracle/source/flag fields match the parent request; no Rust, Kani, CBMC, build, push, CI, or ledger operation occurred.

## Review and activation boundary

Independent review is complete in `REVIEW.md` for the exact final candidate; no static/synthetic blocker remains. `REVIEW-SPEC.md` records the review contract. The current runner prep commit is not an activation commit. If a later separately authorized activation is prepared, preserve the existing same-tree sibling mechanism: create a sibling commit with sole parent `0aac16ef62da9e9d5645782d458593e5d78143ba`, without `[skip ci]`, and retain this skip-ci candidate. Do not push or dispatch on the basis of this preparation.

The current local host has `MemAvailable <= 2 GiB`, so the runner correctly refuses to start a proof group there; RSS behavior is tested synthetically with available memory mocked. No proof credit is implied.

Final terminal-schema delta: required top-level `outcome={kind:COMPLETED}` is validated before per-root or aggregate completion. Final skip-ci parent is `d095a7eeca5c56d1664f852c54161c720a2991cc`; previous local candidates are preparation history. Independent review: `REVIEW.md`; final structured packet: `review-packet-terminal/`.
