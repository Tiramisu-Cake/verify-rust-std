# SmallSort Evidence Brief — 92524a3d

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit (source claim): `1`; evidence complete: `True`

## Failure diagnostics (verified archived sources)

- Diagnostic status: **OBSERVED**; causality: **UNKNOWN**
- COMPILER_ERROR: this file contains an unclosed delimiter at `original/lib.rs:156:3`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/focus/P0a/refinement.log` line 2; SHA-256 `4bce889a6a5400408eae1fce79e40f54f271fd956bfbb95e96a388902e021109`
- COMPILER_ERROR: aborting due to 1 previous error
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/focus/P0a/refinement.log` line 18; SHA-256 `4bce889a6a5400408eae1fce79e40f54f271fd956bfbb95e96a388902e021109`

## Bounded diagnostic context (untrusted observations)

- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=TAIL_OF_SCANNED_PREFIX_NO_MARKER
  - Source: `full-stderr.log` line UNKNOWN; SHA-256 `f77216c41aadf6c667ac1a602069951966cea350daab793ffe11ae0de1225ddc`
> L1: debconf: delaying package configuration, since apt-utils is not installed
  - Scanned 74/74 bytes; scan limit reached=False; lines shown=1/1.
- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/focus/P0a/normal-export.log` line UNKNOWN; SHA-256 `c900746adb0ce66e2257161db65868be30366bc35dba3ad545bcb3dbc9e7f27b`
> L1: 2026-10-18T19:12:08.529844Z TRACE vf_mir_exporter: Calling the Rust Compiler with args: ?"?REDACTED_LONG_VALUE?", "verified/lib.rs", "?REDACTED_LONG_VALUE?", "--edition", "2021", "-Coverflow_checks=off", "--crate-type=lib", "--error-format=
> L2: 2026-10-18T19:12:08.537340Z TRACE vf_mir_exporter: FileLoader::read_file("verified/lib.rs")
> L3: [WITHHELD: OVERSIZED_LINE]
> L4: ?"$message_type":"diagnostic","message":"aborting due to 1 previous error","code":null,"level":"error","spans":??,"children":??,"rendered":"error: aborting due to 1 previous error\n\n"?
  - Scanned 2742/2742 bytes; scan limit reached=False; lines shown=4/4.
- Up to 2 short windows shown; complete bounded context and availability counts are in evidence-index.json. Context does not establish causality.

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

- Record counts: EXIT_NONZERO=4, EXIT_ZERO=104; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- `normal-export`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/focus/P0a/normal-export-stage.json` line UNKNOWN; SHA-256 `7b5d3e116cbe1c634c099899fd09ad31b2f3cd006540d6c39f7db08f2911cdbc`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 1}
- `readonly-export`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/focus/P0a/readonly-export-stage.json` line UNKNOWN; SHA-256 `07999b52a6ff52d3333116171f4cbcc26428d3ffe84624f069b021e70d192882`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 2}
- `refinement`: exit=`1`; linkage=`RECEIPT`; diagnostic=`OBSERVATIONS_EXTRACTED`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/focus/P0a/refinement-stage.json` line UNKNOWN; SHA-256 `5b12b67e48919511a7319bcf96c9955d60fcacbfed0979cd2e50d8d71e7aec11`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 3}
- `sort4-c1-current-recovery`: exit=`1`; linkage=`PAIRED_FILENAME_ONLY`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/sort4-c1-current-recovery-exit-code.txt` line UNKNOWN; SHA-256 `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 4}
- Expected-control nonzero records (source-classified): 0; details in evidence-index.json.
- Exit 0 observed: `console-build`, `a1-R-only-native-reference-build`, `a1-final-schema-exporter-console-build`, `apply`, `check`, `apply`; references in evidence-index.json.
- Coverage: {'candidate_records': 108, 'parsed_records': 108, 'not_captured': 0, 'invalid_records': 0, 'omitted_records': 0}; showing up to 4 nonzero and 6 zero records.
- Missing/ambiguous diagnostics: VERIFIED_FAILED_LOG_WITHOUT_RECOGNIZED_COMPILER_DIAGNOSTIC, MULTIPLE_STAGE_FAILURES_CAUSALITY_UNKNOWN

## Campaign aggregates (source claims)

- No supported aggregate captured; absence from this section does not prove absence from archive.
- Aggregate coverage: {'aggregate_candidates': 0, 'aggregates_captured': 0, 'stage_metadata_captured': 96, 'stage_summaries_retained': 108, 'context_logs_streamed': 5, 'diagnostic_logs_captured': 16, 'diagnostic_log_bytes': 90608, 'oversized_logs': 0, 'budget_omitted_logs': 96, 'aggregates_not_captured': 0}; showing up to 4.

## Representative cases (source verdicts)

- `allprooflogs/cases/sort4-c1-current-recovery`
- Cases: 1; showing up to 4. More references and source claims in evidence-index.json.

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
