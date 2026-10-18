# SmallSort Evidence Brief — 7c26b389

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit (source claim): `0`; evidence complete: `True`

## Failure diagnostics (verified archived sources)

- Diagnostic status: **CORROBORATED**; causality: **CORROBORATED_SOURCE_REPORT**
- Runner-reported blocker: `tool-reconstruction` / `adapter_error`; detail: RuntimeError: A1-TOOL: R-only native reference build
  - Source: `proof-audit.json` line UNKNOWN; SHA-256 `216c3a8ce72b1e6a0bdff71e0a67f25e9eac0e9fba6930212e3a82789de593f4`
- Runner-reported causal stage: `tool-reconstruction` (source assertion)
- OCAML_COMPILER_ERROR: The constructor D.Type expects 0 argument(s), at `rust_frontend/vf_mir_translator/vf_mir_translator.ml:6681`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-tool/a1-R-only-native-reference-build.log` line 1283; SHA-256 `f3ba5380316c6aee2aad00bc004aaaade6af5f9d2ba75f6b0569134314c81a9b`
- MAKE_FAILURE_SUMMARY: make reported Error 1; child cause/status UNKNOWN
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-tool/a1-R-only-native-reference-build.log` line 1285; SHA-256 `f3ba5380316c6aee2aad00bc004aaaade6af5f9d2ba75f6b0569134314c81a9b`

## Stage observations (exit codes are not proof verdicts)

- Record counts: EXIT_NONZERO=1, EXIT_ZERO=95; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- `a1-R-only-native-reference-build`: exit=`2`; linkage=`RECEIPT`; diagnostic=`OBSERVATIONS_EXTRACTED`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-tool/a1-R-only-native-reference-build-stage.json` line UNKNOWN; SHA-256 `66620752e728d7b7f66dfe0a20704d714845afd825a1f3fe1f18123e3b0e1e90`
- Exit 0 observed: `apply`, `check`, `apply`, `check`, `apply`, `check`; references in evidence-index.json.
- Coverage: {'candidate_records': 102, 'parsed_records': 96, 'not_captured': 6, 'invalid_records': 0, 'omitted_records': 32}; showing up to 4 nonzero and 6 zero records.
- Runner-reported cases: 26; NOT_RUN=26
- Missing/ambiguous diagnostics: STAGE_COVERAGE_INCOMPLETE_SEE_INDEX

## Campaign aggregates (source claims)

- No supported aggregate captured; absence from this section does not prove absence from archive.
- Aggregate coverage: {'aggregate_candidates': 0, 'aggregates_captured': 0, 'stage_metadata_captured': 96, 'diagnostic_logs_captured': 16, 'diagnostic_log_bytes': 80806, 'oversized_logs': 0, 'budget_omitted_logs': 90, 'aggregates_not_captured': 0}; showing up to 4.

## Representative cases (source verdicts)

- `allprooflogs/cases/sort4-c1-current-recovery`
- Cases: 1; showing up to 4. More references and source claims in evidence-index.json.

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
