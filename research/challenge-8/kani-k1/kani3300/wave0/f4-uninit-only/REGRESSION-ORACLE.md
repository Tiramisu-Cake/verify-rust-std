# Two-mode regression contract

All new native results below are EXPECTED_FROM_SOURCE, with execution NOT_RUN.
Counts and property identities in synthetic tests are fixture data, never measured
native inventories. Compilation order remains UNKNOWN: delayed-first switches
call paths and carries no order guarantee.

| Mode | Export features, exact set | Independent padding control | Delayed alone/paired, both cfg paths | Initialized alone/paired, both cfg paths | Expected exits |
| --- | --- | --- | --- | --- | --- |
| uninit enabled | export-json, ghost-state, uninit-checks | FAILURE at control.rs:16, safety_check uninitialized pointer read | FAILURE at src/lib.rs:12, safety_check uninitialized pointer read | SUCCESS, result == 7 assertion SUCCESS | independent 1, delayed singleton 1, initialized singleton 0, paired 1 |
| uninit disabled | export-json | SUCCESS | SUCCESS | SUCCESS, result == 7 assertion SUCCESS | every command 0 |

Enabled and disabled each run the independent control, delayed singleton,
initialized singleton and paired selection for both delayed_first/control_first
call-path variants. Every selection is --exact, -j1, with exactly the requested
filters, no unmatched filters, matched count, native outcome and complete regular
property inventory consistent with export counters, partitions, failed properties
and process exit. Singleton/paired signatures retain check class/semantic ID,
status, description, source location and multiplicity; numeric ID suffixes may
vary. There are no fixed property-count expectations.

The ordinary expectations follow from these unchanged source/API facts:

- kani-driver/src/call_single_file.rs forwards --ub-check=uninit and ghost state
  to the compiler only for UnstableFeature::UninitChecks. Direct kani invocation
  uses CLI arguments; `// kani-flags:` in control.rs is a compiletest directive,
  not a CLI option consumed here.
- Both DelayedUbPass::is_enabled and UninitPass::is_enabled use the Uninit predicate.
  Disabled runs request export-json alone, so padding reads have no memory
  initialization-state instrumentation. The padded write stays within an aligned
  u64; the raw u8 padding access is inside Padded and aligned. All u8/u64 bit
  patterns are valid. The delayed value is discarded; the initialized harness
  reads 7 and asserts 7. No ordinary bounds/overflow/unwinding failure is expected.
- memory_safety, overflow, unwinding, undefined_function, assertion_reach_checks
  stay true; prove_safety_only and ignore_global_asm stay false, coverage false,
  and cbmc_args empty. Enabled unsafe expectations are applied only in enabled
  mode. Disabled ordinary results must contain no uninitialized-pointer checks.
- Export enabled_unstable_features comes from driver arguments in
  kani-driver/src/frontend/schema_utils.rs; exact equality prevents hidden mode
  inheritance. Common KANIFLAGS/RUSTFLAGS/KANI_LOG are cleared, encoded Rust flags
  and Cargo target overrides removed. Enabled-only arguments are built afresh;
  targets include mode/cfg/case, preventing artifact reuse between modes.

Frozen-main enabled evidence is the immutable compact intake of run 44177926794:
initialized succeeds alone and fails paired in both cfg paths. validate.py rejects
that observed compact data; explicitly reconstructed export envelopes test parser
compatibility only. Its expected-fixed enabled fixtures replace paired inventories
with singleton copies. Disabled fixtures are wholly synthetic small ordinary
inventories. Neither fixture family establishes a runtime PASS for the new head.
`regression-main.patch` installs the two-mode test on frozen main for a future
main-vs-fix check; actual execution of that new test is NOT_RUN.

Local validation exercises positive and negative cases for both modes: feature
mismatch, unsafe failure suppression, ordinary unexpected failure, assertion/site/
composition/multiplicity drift, partial/missing/malformed/null/wrong-type exports,
NOT_RUN/unresolved/native outcome/selection/configuration errors, spawn failure,
timeout, signal, nonstandard exit and stale exports. Mocked subprocess execution
covers all argument/environment combinations under poisoned inherited flags.
