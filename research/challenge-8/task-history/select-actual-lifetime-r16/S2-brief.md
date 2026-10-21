# SmallSort Evidence Brief — d1376298

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit (source claim): `0`; evidence complete: `True`

## Further bounded evidence

- Complete catalogue: 431 verified members; retained content: 427 files.
- CLI: `smallsort-brief d1376298-d147-43b5-a0b7-e5832cb564b1 --catalogue`, `--search LITERAL`, `--file ID --pointer /key` (JSON), or `--file ID --start 1` (text). Requires the v0.8 client installed on the caller host.
- Reader: `/builds/d1376298-d147-43b5-a0b7-e5832cb564b1/catalogue?q=literal`, `/search?q=literal`, `/fragment?file_id=ID&start=1` (text) or `&pointer=/key` (JSON). Use the same /builds/UUID prefix for all routes. Search is over sanitized retained data only; inspect coverage and next_offset. No raw fallback or proof inference.

## Failure diagnostics (verified archived sources)

- Diagnostic status: **OBSERVED**; causality: **UNKNOWN**
- OCAML_COMPILER_ERROR: This expression has type at `rust_frontend/vf_mir_translator/vf_mir_translator.ml:7852`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-tool/a1-final-schema-exporter-console-build.log` line 40; SHA-256 `e756c4e02f4845baab9b1595337c1219bdc2fe3881e3159254ed6c8bc10430bd`
  - Type context: ACTUAL_AND_EXPECTED_OBSERVED; actual=`(string * Ast.type_expr list * RustBelt.v list *`; expected=`(string * Ast.type_expr list * RustBelt.v list * RustBelt.v list *`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-tool/a1-final-schema-exporter-console-build.log` line 45; SHA-256 `e756c4e02f4845baab9b1595337c1219bdc2fe3881e3159254ed6c8bc10430bd`
- MAKE_FAILURE_SUMMARY: make reported Error 1; child cause/status UNKNOWN
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-tool/a1-final-schema-exporter-console-build.log` line 49; SHA-256 `e756c4e02f4845baab9b1595337c1219bdc2fe3881e3159254ed6c8bc10430bd`

## Tool build milestones (individual observed records)

- `translator-build`: NOT_PRESENT_IN_VERIFIED_ARCHIVE
- `console-build`: EXIT_ZERO; exit=`0`; records=1; omitted=0
  - Source: `allprooflogs/console-build-exit-code.txt` line UNKNOWN; SHA-256 `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`
- `exporter-build`: NOT_PRESENT_IN_VERIFIED_ARCHIVE
- `decoder-build`: NOT_PRESENT_IN_VERIFIED_ARCHIVE
- `refiner-build`: NOT_PRESENT_IN_VERIFIED_ARCHIVE
- `tracked-md-compile`: NOT_PRESENT_IN_VERIFIED_ARCHIVE
- `tracked-md-preparation`: NOT_PRESENT_IN_VERIFIED_ARCHIVE

## First comparator source results

- Coverage: NO_SUPPORTED_SOURCE_RECORD_OR_NAMED_ARTIFACT; projected=0; omitted=0; scan_truncated=False; showing up to 6 records
- A joint false/true/panic claim does not provide separate per-branch receipts; absent records do not establish NOT_RUN.

## Stage observations (exit codes are not proof verdicts)

- Record counts: EXIT_NONZERO=1, EXIT_ZERO=122; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- `a1-final-schema-exporter-console-build`: exit=`2`; linkage=`RECEIPT`; diagnostic=`OBSERVATIONS_EXTRACTED`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-tool/a1-final-schema-exporter-console-build-stage.json` line UNKNOWN; SHA-256 `66d7986d7b6dd44702611c20ecd030d9e0eb52629f2710feeac89f5a3609fdd8`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 0}
- Expected-control nonzero records (source-classified): 0; details in evidence-index.json.
- Exit 0 observed: `console-build`, `a1-R-only-native-reference-build`, `apply`, `check`, `apply`, `check`; references in evidence-index.json.
- Coverage: {'candidate_records': 123, 'parsed_records': 123, 'not_captured': 0, 'invalid_records': 0, 'omitted_records': 0}; showing up to 4 nonzero and 6 zero records.

## Campaign aggregates (source claims)

- No supported aggregate captured; absence from this section does not prove absence from archive.
- Aggregate coverage: {'aggregate_candidates': 0, 'aggregates_captured': 0, 'stage_metadata_captured': 96, 'stage_summaries_retained': 123, 'context_logs_streamed': 1, 'diagnostic_logs_captured': 16, 'diagnostic_log_bytes': 84186, 'oversized_logs': 0, 'budget_omitted_logs': 111, 'aggregates_not_captured': 0}; showing up to 4.

## Representative cases (source verdicts)

- `allprooflogs/cases/sort4-c1-current-recovery`
- Cases: 1; showing up to 4. More references and source claims in evidence-index.json.

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
