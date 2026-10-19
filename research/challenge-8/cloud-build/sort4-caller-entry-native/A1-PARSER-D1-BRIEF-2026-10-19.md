# SmallSort Evidence Brief — f8748a4d

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit (source claim): `0`; evidence complete: `False`

## Further bounded evidence

- Complete catalogue: 419 verified members; retained content: 388 files.
- CLI: `smallsort-brief f8748a4d-c5f6-47fe-b157-4a9e60839d4e --catalogue`, `--search LITERAL`, `--file ID --pointer /key` (JSON), or `--file ID --start 1` (text). Requires the v0.8 client installed on the caller host.
- Reader: `/builds/f8748a4d-c5f6-47fe-b157-4a9e60839d4e/catalogue?q=literal`, `/search?q=literal`, `/fragment?file_id=ID&start=1` (text) or `&pointer=/key` (JSON). Use the same /builds/UUID prefix for all routes. Search is over sanitized retained data only; inspect coverage and next_offset. No raw fallback or proof inference.

## Failure diagnostics (verified archived sources)

- Diagnostic status: **SOURCE_REPORTED**; causality: **UNKNOWN**
- Runner-reported blocker: `P0a` / `adapter_error`; detail: InventoryError: decoded VfMir parse failed: invalid quoted string at byte 9362
  - Source: `proof-audit.json` line UNKNOWN; SHA-256 `8555a4a6a1b872f605ab31abaa8bc5ade9c1daedd551685434757fc06f266d07`

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

- Record counts: EXIT_ZERO=110; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- Expected-control nonzero records (source-classified): 0; details in evidence-index.json.
- Exit 0 observed: `console-build`, `a1-R-only-native-reference-build`, `a1-final-schema-exporter-console-build`, `normal-decode`, `normal-export`, `readonly-decode`; references in evidence-index.json.
- Coverage: {'candidate_records': 110, 'parsed_records': 110, 'not_captured': 0, 'invalid_records': 0, 'omitted_records': 0}; showing up to 4 nonzero and 6 zero records.
- Source assertions: {'proof_attempted': False}
  - Source: `proof-audit.json` line UNKNOWN; SHA-256 `8555a4a6a1b872f605ab31abaa8bc5ade9c1daedd551685434757fc06f266d07`
- Runner-reported cases: 26; INCONCLUSIVE=1, NOT_RUN=25

## Campaign aggregates (source claims)

- No supported aggregate captured; absence from this section does not prove absence from archive.
- Aggregate coverage: {'aggregate_candidates': 0, 'aggregates_captured': 0, 'stage_metadata_captured': 96, 'stage_summaries_retained': 110, 'context_logs_streamed': 0, 'diagnostic_logs_captured': 16, 'diagnostic_log_bytes': 523685, 'oversized_logs': 0, 'budget_omitted_logs': 98, 'aggregates_not_captured': 0}; showing up to 4.

## Representative cases (source verdicts)

- `allprooflogs/cases/sort4-c1-current-recovery`
- Cases: 1; showing up to 4. More references and source claims in evidence-index.json.

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
