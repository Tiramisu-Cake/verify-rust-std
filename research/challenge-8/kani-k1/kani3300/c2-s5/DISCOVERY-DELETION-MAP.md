# Discovery / deletion map

Before/after source HEAD is 3b382c812a1b8541946e6dc732cf04497ebcf995; working tree unchanged. No selectors deleted or added.
INPUTS.json records all 29 files in exactly the three named suites.
Proposed 21 per-root rows in ORACLE-MAP.json are not installed selectors.

Existing expected siblings are not equivalent: p1/lawful/legal-pair are verdict-only;
p2/postcondition/clause lack exact count and/or intended target blocks; frame lacks count
and next allowed-write SUCCESS. Multi-harness legal-pair needs two one-harness files,
with unchanged body/contracts; existing independent controls must remain.

Discovery uses tools/compiletest/src/main.rs::collect_rs_tests_from_dir: every normal .rs
is a test, directory `auxiliary` is excluded. Future shared helpers belong under auxiliary;
otherwise use self-contained sources. Each installed expected input must have one harness,
matching Checking harness and Complete - one total. Validate native discovery in CI.

After resolved map + review only tests/json-handler/uninit-contract-oracles,
uninit-contract-mode-boundaries and uninit-part1-composition may be removed.
Shared scripts/validate_json_export.py, matcher/driver/schema, other upstream suites and
S4 units remain untouched. Check all references before deletion. No deletion is authorized
by this incomplete map; all old source/research references remain valid at present.
