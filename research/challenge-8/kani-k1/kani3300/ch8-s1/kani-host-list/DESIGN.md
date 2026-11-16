# S1 list timeout — source basis and minimal repair

Task input g0 `45498717e2d67a9e98aa5b6c1b398cc50f72f72c`. Prior run facts below come from TASK-CH8-S1-LIST-W13.md, not an independent reread of CI logs. Source inspection is read-only against clean stock Kani `0aac16ef62da9e9d5645782d458593e5d78143ba` at `/root/kani-upstream-ch8-s1`.

## Why list codegens

`kani-driver/src/list/collect_metadata.rs:88` (`list_standalone`) creates a KaniSession and calls `std_project` before processing/outputting metadata. `kani-driver/src/project.rs:363` builds a dummy project through `cargo_build_std`; `call_cargo.rs:84-124` invokes Cargo build with `-Z build-std=panic_abort,core,std`, Kani compiler, and harness reachability on all crates. `session.rs:100-108` selects ProofHarnesses by default. `kani-compiler/src/kani_middle/codegen_units.rs:85-96,375-393` keeps all manual harnesses when filters are empty. `codegen_cprover_gotoc/compiler_interface.rs:430-463` loops through harnesses, calls `codegen_items`, and writes metadata afterwards. This explains the task-reported per-harness ~11 MB `.out` files and empty JSON when killed at 600 s. `list` is not metadata-only.

## Why option (a)

Standalone `list --std` has no supported harness filter: `StandaloneListArgs` (`kani-driver/src/args/list_args.rs:21-42`) flattens CommonArgs only. Root `StandaloneArgs` (`args/mod.rs:141-160`) uses `args_conflicts_with_subcommands=true`; root VerificationArgs `--harness`/`--exact` cannot accompany this subcommand. Internal compiler filtering and repeatable verification selectors therefore do not supply option (c) on this CLI. `--no-codegen` is also a VerificationArgs option; moreover backend metadata is emitted during codegen. No usable metadata-only switch is established here.

Export JSON has an exact selection record, a harness attributes kind with `ProofForContract.target_fn`, and optional contract metadata. The existing runner already checks these against the list's contracted-function mapping; `contracted_function_name` is a generated wrapper name, not the same target identifier (see existing tests). Removing list would remove the separate observed mapping and the six-distinct-target / activation-to-positive checks unless replaced with new binding logic. Option (b) is a broader change. Preserve the current binding for this final retry.

Set `LIST_SECONDS = 1500`, independently pinned in request budgets. Keep `MAX_ROW_SECONDS = 600`, RSS 6 GiB, every row timeout/oracle/flag, shared phase 4500 s and job 120 min. The phase starts before list and its elapsed time remains charged to rows. At the list maximum there are about 3000 s left in the phase; a row starts only if the existing 600 s plus cleanup reserve is available. List includes the reported ~6 min std compilation; 1500 s leaves ~19 min for remaining codegen. Planning metadata changes from 300 s to 1500 s for list; estimated rows stay 2760 s (total 4260 s). These estimates are not per-row guarantees; the last-row 610 s reservation guard is unchanged.

The unchanged job partition is at most 30 min setup + 75 min list/rows + 15 min fallback/upload. This is bounded preparation, not evidence that the global list or all rows will fit; exhaustion still stops with UNKNOWN/NOT_RUN.

## Receipts and limits

`list/receipt.json` is atomic before execution, after execution, and after validation. It records argv, pins, timeout, stage/state, child exit/signal/external interruption, timeout/cap reason, elapsed and sampled process-group RSS. Preflight/launch/JSON/binding errors leave FAILED receipts; no frozen inventory survives a failed retry. Success records COMPLETE only after the unchanged inventory binding checks pass.

List opts into bounded head+tail capture (each stream still capped at 1 MiB, with cap termination unchanged). Its receipt includes up to 2048 bytes of head and 2048 bytes of tail per stream, capture/omission counts and log hash. Rows retain the previous head-only behavior. Fallback preserves completed receipts and marks a still-running one INTERRUPTED with unknown execution outcome, or creates NOT_RUN_OR_INTERRUPTED after earlier setup failures. SIGKILL cannot supply a final exit/RSS observation; the last atomic receipt remains explicitly incomplete. SIGTERM/SIGINT caught during execute retain child and external signal data.

No push, CI, publication, ledger, local cargo/rustc/Kani/CBMC, or raw-log access. No proof obligations closed; all 23 actual proof rows NOT_RUN, proof credit NONE.
