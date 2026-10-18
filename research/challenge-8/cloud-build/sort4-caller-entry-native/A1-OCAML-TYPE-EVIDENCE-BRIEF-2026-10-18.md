# SmallSort Evidence Brief — 7987e81f

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit (source claim): `0`; evidence complete: `True`

## Failure diagnostics (verified archived sources)

- Diagnostic status: **CORROBORATED**; causality: **CORROBORATED_SOURCE_REPORT**
- Runner-reported blocker: `tool-reconstruction` / `adapter_error`; detail: RuntimeError: A1-TOOL: R-only native reference build
  - Source: `proof-audit.json` line UNKNOWN; SHA-256 `67f1e16b2609e8c153f398f385b08ba4df47c04a9b6361b49edacc863b642b13`
- Runner-reported causal stage: `tool-reconstruction` (source assertion)
- OCAML_COMPILER_ERROR: This pattern matches values of type D.rvalue at `rust_frontend/vf_mir_translator/vf_mir_translator.ml:6884`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-tool/a1-R-only-native-reference-build.log` line 1288; SHA-256 `685b0ffaa59c21d321fda7aa473555f768cc5821ee0ca405d11e868f46254b49`
- MAKE_FAILURE_SUMMARY: make reported Error 1; child cause/status UNKNOWN
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-tool/a1-R-only-native-reference-build.log` line 1290; SHA-256 `685b0ffaa59c21d321fda7aa473555f768cc5821ee0ca405d11e868f46254b49`

## Stage observations (exit codes are not proof verdicts)

- Record counts: EXIT_NONZERO=1, EXIT_ZERO=95; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- `a1-R-only-native-reference-build`: exit=`2`; linkage=`RECEIPT`; diagnostic=`OBSERVATIONS_EXTRACTED`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-tool/a1-R-only-native-reference-build-stage.json` line UNKNOWN; SHA-256 `7409eab6ea453f5fc21a51d23b1d348b83975d2b7c67f555ce893178c9d4145a`
- Exit 0 observed: `apply`, `check`, `apply`, `check`, `apply`, `check`; references in evidence-index.json.
- Coverage: {'candidate_records': 102, 'parsed_records': 96, 'not_captured': 6, 'invalid_records': 0, 'omitted_records': 32}; showing up to 4 nonzero and 6 zero records.
- Runner-reported cases: 26; NOT_RUN=26
- Missing/ambiguous diagnostics: STAGE_COVERAGE_INCOMPLETE_SEE_INDEX

## Campaign aggregates (source claims)

- No supported aggregate captured; absence from this section does not prove absence from archive.
- Aggregate coverage: {'aggregate_candidates': 0, 'aggregates_captured': 0, 'stage_metadata_captured': 96, 'diagnostic_logs_captured': 16, 'diagnostic_log_bytes': 81007, 'oversized_logs': 0, 'budget_omitted_logs': 90, 'aggregates_not_captured': 0}; showing up to 4.

## Representative cases (source verdicts)

- `allprooflogs/cases/sort4-c1-current-recovery`
- Cases: 1; showing up to 4. More references and source claims in evidence-index.json.

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
