# C2 Gate A — coordinator request / NOT_RUN

Local CI-only overlay `e795403859f5b61e37b5bae9dce705b9a8ede8e0`, tree `42ce47f065ae6aeb3c9ad23d1b15f95d7a0e82f7`.

Worker15 preparation only. Gate A NOT_RUN; no proof credit. Cloud preparation $0; no local toolchain, frozen regression/setup execution, push, dispatch, CI, retries or changes to freeze. Coordinator owns publication and the single dispatch. Research remains uncommitted.

Frozen export `ad499e41dd2db9ccd432f89721638a1f3a0bbd44`, tree `9829702c1aa0ecb73c860fc0ad5451757917d6cb`. Exact local CI overlay SHA and path are in CI-OVERLAY.json; its sole direct parent is this export. Before publication/dispatch, coordinator verifies fork refs `fix/kani-3300-c2-s6` and `freeze/kani-3300-c2` both equal the export. Never move freeze or force push. Publish only the exact overlay SHA to `Tiramisu-Cake/kani:ci/kani3300-c2-gatea-w15`, then dispatch `kani3300-c2-gatea.yml` once at that branch after checking the remote head equals the overlay. Instructions in CI-OVERLAY.json. No other workflows, replay, SEL1, perf or LLBC.

Exactly three independent regression rows: `ubuntu-24.04`, `ubuntu-24.04-arm`, `macos-15`; max-parallel 3, fail-fast false, one attempt each, common concurrency group `kani3300-c2-gatea`, cancel-in-progress false. Runner unavailable/setup failure means NOT_RUN/INCOMPLETE; no substitutions. The separate 10-minute lightweight summary is not a fourth regression job; it reports missing/cancelled/failed rows with nonzero aggregate status.

Each job has 360 minutes; maximum regression subprocess 20400 seconds (340 minutes), per-test timeout 2400 seconds. Sum of three regression-job envelopes is at most1080 runner-minutes, a limit, not a runtime estimate. At the first step a timestamp minus60 seconds conservatively accounts for startup; before regression compute `min(20400, floor(21600 - elapsed - 600))`. Reserve at least10 minutes for process-group termination, identity checks, runtime inventory, receipt and upload; with quick setup the20400 cap leaves an additional10 minutes. Setup/observer consume this allowance; nonpositive available budget means INCOMPLETE and no regression. No suite filtering to fit time, no low-RSS watchdog. No guarantee that full regression will finish within caps.

Control checkout is exact dispatched overlay SHA; a second independent `export/` checkout is literal frozen SHA. All execution source and the setup action come from export; `.github/actions/setup` receives matrix OS and `kani_dir: export`. Before setup and after setup/regression, require source HEAD/tree, tracked files/subtree hashes, gitlink pins and clean Git status including untracked. Normal ignored build outputs are allowed. Preserve bounded source diff if changed; no reset/cleanup to hide changes. Every platform starts separately with no shared target/cache.

Frozen pins: nightly-2026-10-23, CBMC6.11.0, Kissat4.0.1, cvc5 1.3.0; macOS Z3 5.3.1, Ubuntu distribution Z3 (capture actual installed version). Other dependencies and OS setup identities are in EXPORT-MANIFEST.json. No solver upgrades/model substitutions/patched CBMC.

Run exactly once `bash scripts/kani-regression.sh` from export. KEEP_GOING empty; timeout2400. Reject unexpected external flags/build/BASH_ENV overrides before execution; no RUST_TEST_THREADS override. The script's original scoped RUSTFLAGS are preserved. No tee/filter/new ignores/suppressions/global object-bits12/--no-slice-formula/arrays-uf/check disabling. Accepted per-fixture flags remain frozen. Top-level Bash observer does not instrument child shells/tests, preserves original exit/errexit/pipefail/argv, and qualifies with a synthetic shell self-test before regression.

Combined stdout/stderr/events ≤256MiB per platform; parser has same cap. Receipt/metadata total ≤16MiB, artifact package ≤384MiB, retention14 days. Summary counts ≤20 lines/stage, each≤4096 bytes; overflow explicitly TRUNCATED/INCOMPLETE, unknown fields UNKNOWN. Timeout/cap/cancellation terminate entire process group TERM→bounded grace→KILL, preserving subprocess exit/signal; OOM/runner loss remain separately classified or UNKNOWN. No global RLIMIT_FSIZE, target/sysroot/source archive upload or full environment capture.

Required ordered stages, bound to frozen script SHA-256 `b7dcc0c1418b4a79edc19073acf3d1a8ecb70e1b81e65d334812b594d4d4163b`:

| # | Stage | Mode | Source line |
| --- | --- | --- | --- |
| 1 | cbmc | — | 27 |
| 2 | kissat | — | 28 |
| 3 | fmt | — | 31 |
| 4 | build-dev | — | 34 |
| 5 | unit:cprover_bindings | — | 37 |
| 6 | unit:kani-compiler | — | 38 |
| 7 | unit:kani-driver | — | 39 |
| 8 | unit:kani_metadata | — | 40 |
| 9 | unit:compiletest | — | 41 |
| 10 | unit:kani-cov | — | 42 |
| 11 | unit:kani | — | 44 |
| 12 | unit:kani_macros | — | 47 |
| 13 | compiletest-config | — | 70 |
| 14 | build-cov | — | 74 |
| 15 | suite:kani | kani | 98 |
| 16 | suite:expected | expected | 98 |
| 17 | suite:ui | expected | 98 |
| 18 | suite:std-checks | cargo-kani | 98 |
| 19 | suite:firecracker | kani | 98 |
| 20 | suite:prusti | kani | 98 |
| 21 | suite:smack | kani | 98 |
| 22 | suite:cargo-kani | cargo-kani | 98 |
| 23 | suite:cargo-ui | cargo-kani | 98 |
| 24 | suite:script-based-pre | exec | 98 |
| 25 | suite:coverage | coverage-based | 98 |
| 26 | suite:cargo-coverage | cargo-coverage | 98 |
| 27 | suite:kani-docs | cargo-kani | 98 |
| 28 | suite:kani-fixme | kani-fixme | 98 |
| 29 | suite:json-handler | exec | 98 |
| 30 | firecracker-codegen | — | 111 |
| 31 | cargo-smoke | — | 116 |
| 32 | cargo-clean | — | 117 |
| 33 | warnings-build | — | 126 |

Per-platform receipt records command/source line/mode/ordered presence/exit/counts, passed/failed/ignored/filtered, script exit, termination kind/signal, timestamps/duration, actual timeout/caps, event hash/completeness, source/overlay/run identities and source checks before/after. Setup/preflight/observer statuses are separate from33 stages. Record actual runner label/OS/image/version/arch/host/RAM/disk and binary paths/versions/SHA-256 for compiler/driver/runtime/models, CBMC/goto-instrument, Kissat/used solvers and rustc/toolchain/dependencies/submodules; absent identities UNKNOWN. Binary hashes may differ by architecture. Effective argv and allowlisted environment policy are recorded; unobserved verifier argv remains UNKNOWN.

Upload and receipt preservation always run where runner survives; fallback on setup failure must not overwrite existing partial receipt. Hard loss without EXIT/upload is GAP, not inferred success/failure. Aggregate must require all three coherent rows; missing, duplicated, failed or cancelled rows cannot yield green acceptance.

Coordinator acceptance requires three complete exact-source receipts, all33 ordered completed stages, original script exit0, complete bounded streams, known required identities, clean source and no unexpected failures. Counts collected anew: no C1b baseline copied. Intended verifier FAILURE/Unsupported accepted by frozen oracle is distinct from test/oracle failure. Review all platform ignores/zero suites; new unexplained ignore/filter/skip, absent counts, duplicate/missing/order mismatch or nonzero stage exit forbids acceptance. `COMPLETE_EXIT_ZERO_REQUIRES_REVIEW` is technical reporting only; aggregate exit0 alone is insufficient and no independent proof credit/publication authorization follows.

macOS/ARM execution and actual full load remain future CI validation. Source/dependency/oracle drift or need to filter/change frozen source requires STOP/new freeze, no repair under this freeze and no automatic rerun.

Coordinator dispatch preflight: verify that the named manual workflow is dispatchable in the fork (default-branch workflow availability or an already registered/previously run workflow, as applicable). Availability is UNKNOWN in this local preparation. GitHub documents the default-branch requirement for workflow_dispatch and branch selection with `--ref`: [event reference](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch), [manual runs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow). If unavailable, STOP before dispatch; this request does not authorize default-branch edits/settings changes, a bootstrap run or an extra dispatch. This is a future operational prerequisite, not a claimed observed remote failure.
