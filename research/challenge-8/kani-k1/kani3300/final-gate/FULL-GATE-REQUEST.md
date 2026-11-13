# Gate A request — C1_FROZEN / NOT_RUN / NOT_AUTHORIZED

Owner: coordinator (dispatch), worker15 (preparation). Phase: Gate-P preparation;
future run phase/owner/slot and ledger **UNASSIGNED**. Preparation Cloud cap $0;
future budget and run count **NOT_GRANTED**. One proposed Linux full job, no
automatic retries. C1 is frozen at the exact identities in EXPORT-MANIFEST.json. This is not run authorization. See CI-REQUEST.md for publication refs and proposed limits.

Run the unchanged exact-C1 `scripts/kani-regression.sh` in a separate clean
export checkout. Upstream recipe is frozen C1 `.github/workflows/kani.yml` → local
`.github/actions/setup`: OS-specific dependencies, pinned rustup/toolchain,
submodules, dependency and solver checks. Proposed first platform ubuntu-24.04,
one concurrent job (`kani3300-fullgate`, cancel-in-progress=false), no added
RUST_TEST_THREADS override. Upstream regression also lists ubuntu-22.04,
ubuntu-24.04-arm, macos-15-intel and macos-14. Linux alone is not full-platform
evidence; coordinator chooses any further matrix, runner availability and caps.

Proposed job cap 360 minutes, regression subprocess 340 minutes (20400 seconds),
with 20 minutes for setup/artifact handling. These are proposed envelopes, not
measured runtimes or assurance that a run fits. They need coordinator approval;
setup exceeding its reserve or the full script exceeding its cap is incomplete,
not permission to filter tests. Per-test timeout stays default 2400 seconds.
CBMC stays 6.11.0, Kissat 4.0.1, nightly-2026-10-23 unless final reviewed C1 pins
explicitly differ; no CBMC-ZST patch or dependency upgrade is imported.

`KANI_REGRESSION_KEEP_GOING` must be empty: nonempty disables script errexit.
The observer sets it to `""`, rejects unexpected flag/build environment overrides,
and invokes `bash scripts/kani-regression.sh` directly without tee or filters.
No global object-bits, slicing or disabled-check arguments; accepted per-fixture
object-bits12 flags remain in the export. Shell observation does not edit the
regression script. The CI overlay's observer is itself not yet exercised in Bash
or CI; only its synthetic Python protocol has been tested locally.

Required ordered receipt stages:

1. CBMC version and Kissat version checks; fmt; cargo build-dev.
2. Unit packages cprover_bindings, kani-compiler, kani-driver, kani_metadata,
   compiletest, kani-cov, kani/concrete_playback, kani_macros/syn/extra-traits.
3. Compiletest dry configuration and build kani-cov.
4. All 15 suites, with the exact modes in the unchanged script: kani/kani,
   expected/expected, ui/expected, std-checks/cargo-kani, firecracker/kani,
   prusti/kani, smack/kani, cargo-kani/cargo-kani, cargo-ui/cargo-kani,
   script-based-pre/exec, coverage/coverage-based, cargo-coverage/cargo-coverage,
   kani-docs/cargo-kani, kani-fixme/kani-fixme, json-handler/exec.
5. Firecracker codegen; cargo smoke harness trivial_success; cargo clean for
   that manifest; final `RUSTFLAGS="-D warnings" cargo build` with cprover.

Expected outputs: complete ordered presence/exit per stage, unit/suite counts
(including ignored/expected-negative), original overall exit, termination kind
and signal, source identities/clean status, effective argv/environment policy,
binary/runtime/model and CBMC/Kissat SHA-256 inventory, artifact hash, and
bounded receipt. Save the CI-created full event artifact even on failure;
ordinary Cloud readers must use Brief, never raw-download it. Observer emits
EXIT_ZERO only for completed commands; no counts/order/exit means incomplete.
An aggregate exit0 alone gives no stage acceptance. Expected negative tests
passing their oracle are distinct from unexpected compiletest failures. Ignore
counts require review; no newly ignored/excluded tests are accepted implicitly.
Infrastructure failure means NOT_RUN for later stages, INCOMPLETE for interrupted
stage. Timeout/OOM/object-limit/signal is not proof failure or accepted replay.

Artifact upload uses `always()`. Hard runner loss can prevent EXIT/final JSON or
upload; that is an explicit evidence GAP, never inferred success. No retry until
coordinator classifies the cause. No export source edits to repair run output;
new source/test changes require new freeze and affected receipts/gates.
