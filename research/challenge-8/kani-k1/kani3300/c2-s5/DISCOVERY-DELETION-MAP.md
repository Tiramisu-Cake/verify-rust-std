# S5 discovery / deletion map

DISCOVERY-INVENTORY.json records native naming/discovery rules and before/after file selectors.
FIXTURE-INVENTORY.json lists all22 replacement oracle inputs, exact selectors, one harness/root,
golden and source hashes/counts. ORACLE-MAP.json maps all21 old semantic roots/cases.

Static expected input discovery changes725→740: remove legal-pair.rs (two old harnesses),
add legal-ordinary/legal-pfc (one each), add seven mode inputs (six old roots plus same-mode
bounded false Replace return companion), add seven composition inputs. Six other strong expected
inputs are reused and strengthened. This accounts for all16 added/one removed file selectors.
Independent existing expected controls stay. Native discovery remains NOT_RUN, required in CI.

All input sources are self-contained and have exactly one proof/proof_for_contract attribute.
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
