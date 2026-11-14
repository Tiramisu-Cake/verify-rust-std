# S5 discovery / deletion map

DISCOVERY-INVENTORY.json records native naming/discovery rules and before/after file selectors.
FIXTURE-INVENTORY.json lists all22 replacement oracle inputs, exact selectors, one harness/root,
golden and source hashes/counts. ORACLE-MAP.json maps all21 old semantic roots/cases.

Static expected input discovery changes725→740: remove legal-pair.rs (two old harnesses),
add legal-ordinary/legal-pfc (one each), add seven mode inputs (six old roots plus same-mode
bounded false Replace return companion), add seven composition inputs. Six other strong expected
inputs are reused and strengthened. This accounts for all16 added/one removed file selectors.
Independent existing expected controls stay. Native discovery remains NOT_RUN, required in CI.

All input sources are self-contained. Twenty have one proof/proof_for_contract attribute; the two Replace inputs have a caller plus the required local PFC companion, with exactly one caller selected via --harness/--exact.
There are no new helper .rs files requiring discovery exclusion. tools/compiletest/src/main.rs
collect_rs_tests_from_dir/is_test discovers every normal .rs except auxiliary directories;
run_expected_test uses .expected or directory expected. Goldens pin Checking harness and 1 total.

Exactly three JSON exec selectors are removed: uninit-contract-oracles,
uninit-contract-mode-boundaries, uninit-part1-composition. INPUTS.json records every old file hash;
original Rust inputs including CC4 diagnostic variants are retained in research source-inputs,
and all base source/manifest files remain accessible at exact base3b382c812a. These suites'
Python synthetic collector/binder/error-path tests are deleted with their removed runners.
Their process/schema/full-inventory comparisons are not silently claimed by expected;
MIXED-ISOLATION-DISPOSITION/REVIEW explain remaining invariant/unit/research basis and residual loss.
No new runner, JSON snapshot suite, T1b allowance or auto-blessing is added.

Shared scripts/validate_json_export.py, upstream JSON suites (including #5154), schemas,
compiletest matcher/driver, production compiler/runtime/pins, S4 units and independent controls
are unchanged. Check no external imports/docs reference removed suites before final commit.
Deletion occurs after completed semantic map and independent transfer review; CI results stay NOT_RUN.

## CI43636027466 correction: source-harness exception

Two Replace inputs require an in-crate `#[proof_for_contract(passthrough)]` companion
for `stub_verified` validation. Each now contains the original caller plus the full-domain
`replace_simple_check` companion, but `kani-flags --harness <caller> --exact` selects
exactly one caller (before --cbmc-args). This explicitly authorized exception changes
source harness count to two in these files, and preserves one selected root per oracle.
The separate replace-simple-check.rs fixture still executes the PFC oracle. Companion
presence does not constitute proof execution or mode qualification.

No goldens or intended native counts changed: Replace N2, false-return partition N0.
Only the selected caller emits the verification summary, with its own Checking harness,
consecutive SUMMARY / ** N of, verdict and Complete1total. Cover counts cannot satisfy
the anchored check-summary requirement. See fix-43636027466/REVIEW.md for source tracing.
Native verification of this correction remains NOT_RUN.
