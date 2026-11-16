# Independent bounded review — S1 list timeout

**Decision: PREPARATION_ONLY — no correctness blocker found for coordinator review.** This review does not authorize dispatch, publication, or proof credit.

## Reviewed identities

- Candidate: `/root/kani-ch8-s1k-list-w13` commit `c03363b3b0a83fa9e78c4841720cb48ee7638c6a`, tree `8c51bd047ed6d3287572277eba23b28f458e7e87`, sole parent stock Kani `0aac16ef62da9e9d5645782d458593e5d78143ba`.
- Review spec SHA-256: `54765f5e12de636da05142a2a69558d93881a96c31bcad74d23727c3d9f09f08`.
- Review packet SHA-256: `9171b6a9b8255dcea2847fa1ccaf562474736895305b2722969679cfe6cab299`.
- `/usr/local/bin/smallsort-session review check` returned `PACKET_VALID_NOT_REVIEWED` for these exact identities before this report was written.

## Findings

No blocking or nonblocking correctness findings.

Source inspection supports the selected repair: standalone `kani list --std` flows through `std_project` and `cargo_build_std`, invoking Kani codegen over std harnesses before list metadata is emitted. `StandaloneListArgs` exposes only common arguments and has no harness selector; root standalone args conflict with subcommands. The proposed narrowed-list option is not available through this CLI, and dropping list would remove existing independent PFC target-mapping checks.

The candidate gives list its own 1500-second cap while preserving the 600-second per-root cap and 4500-second shared phase. It updates both `list_seconds` and `planned_list_seconds` to 1500; estimated rows remain 2760 seconds, for 4260 seconds total before the existing 10-second cleanup margin. This is internally consistent. These are planning estimates, not a guarantee that list or every row will finish; the unchanged phase guard leaves unstarted rows UNKNOWN/NOT_RUN if time runs short.

List inventory binding remains fail-closed: exact requested selectors must occur in the correct standard/PFC set; every PFC selector must map to one contracted function; six smoke roots must map to six distinct targets; activation diagnostics must map to their positive targets. Invalid version, missing selector/mapping, collapsed targets, wrong diagnostic mapping, and oversize inventory are covered by synthetic regressions. Failed attempts remove stale inventory before starting and do not freeze inventory on nonzero exit, signal, timeout, resource/output cap, missing/invalid JSON, or binding failure.

Receipts are atomically written before execution and after execution/validation, with bounded head/tail output previews. The synthetic coverage exercises success, nonzero exit, child and external signals, timeout, RSS/output caps, launch/preflight errors, malformed inventory, and fallback marking of interrupted/no-run receipts. Row execution behavior remains unchanged; the report grants no evidence credit.

## Validation and limits

- `python3 -m unittest -v test_runner test_package`: 20 tests passed (synthetic Python subprocesses only).
- The task-reported static validation identifies 23 unchanged rows, unchanged workflow, and byte-identical inventory-binding logic.
- No Cargo, rustc, Kani, CBMC, build, list, run, CI, push, publication, ledger, or raw-log operation was performed. All 23 proof rows remain NOT_RUN; proof credit is NONE.
