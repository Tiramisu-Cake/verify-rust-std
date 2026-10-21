# SmallSort Evidence Brief — 909fb226

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit (source claim): `0`; evidence complete: `True`

## Further bounded evidence

- Complete catalogue: 603 verified members; retained content: 551 files.
- CLI: `smallsort-brief 909fb226-b3c0-49f7-a882-2b634624ec3a --catalogue`, `--search LITERAL`, `--file ID --pointer /key` (JSON), or `--file ID --start 1` (text). Requires the v0.8 client installed on the caller host.
- Reader: `/builds/909fb226-b3c0-49f7-a882-2b634624ec3a/catalogue?q=literal`, `/search?q=literal`, `/fragment?file_id=ID&start=1` (text) or `&pointer=/key` (JSON). Use the same /builds/UUID prefix for all routes. Search is over sanitized retained data only; inspect coverage and next_offset. No raw fallback or proof inference.

## Failure diagnostics (verified archived sources)

- Diagnostic status: **OBSERVED**; causality: **UNKNOWN**

## Bounded diagnostic context (untrusted observations)

- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/actual-sort4/stage/body-verification.log` line UNKNOWN; SHA-256 `ddfadc8b643009c36c2a2dd08947e782cd6a89b1253d5bb579deed56d877973c`
> L6672: 0.161145s: Entering Redux.assume_with_implications(!(own(F_typeid) = points_to_))
> L6673: 0.161150s: Exiting Redux.assume_with_implications
> L6674: 0.161154s: Exiting Redux.query
> L6675: verified/lib.rs(68,17-20): error: No matching heap chunks: array?T?(v_base, 4, _)
> L6676: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
> L6677: ? ^^^
> L6678: verified/lib.rs(68,17-20): note: Consuming assertion
> L6679: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
  - Scanned 495004/495004 bytes; scan limit reached=False; lines shown=8/12.
- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/raw-copy-missing-destination-rights-negative/stage/body-verification.log` line UNKNOWN; SHA-256 `281dbf7e11543168b694c03bab8b6f1093ebf656c0761c97631238145dd50d6c`
> L1185: 0.096827s: Entering Redux.assume_with_implications(!(!(1 = 0)))
> L1186: 0.096831s: Exiting Redux.assume_with_implications
> L1187: 0.096836s: Exiting Redux.query
> L1188: ?REDACTED_LONG_VALUE?.rsspec(643,55-58): error: No matching heap chunks: array_?T?(dst, 1, _)
> L1189: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
> L1190: ? ^^^
> L1191: ?REDACTED_LONG_VALUE?.rsspec(643,55-58): note: Consuming assertion
> L1192: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
  - Scanned 95114/95114 bytes; scan limit reached=False; lines shown=8/12.
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

- Record counts: EXIT_NONZERO=9, EXIT_ZERO=146; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- `body-verification`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/actual-sort4/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `457c42f6ae6a42c773034f019acb23f935c12bbda534a8528a4fdb2f67afeceb`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 0}
- `body-verification`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/raw-copy-missing-destination-rights-negative/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `90a9da117c5ccd060e6cba2e4a2f3b095ecefe8c7d73d0c4140581dc2b9aee4b`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 1}
- `body-verification`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/raw-copy-missing-initialized-source-negative/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `934bcef764c7f775d285e4bb0b299ced18c411de426d4a4553fe6c9be28c0bba`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 2}
- `body-verification`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/raw-copy-one-owner-duplicate-negative/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `dbff66ce1dc6786ad8b8adb0fceba3b8f880ba99e614f87bc50f280d0fbe78e7`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 3}
- Expected-control nonzero records (source-classified): 0; details in evidence-index.json.
- Exit 0 observed: `console-build`, `lemma-verification`, `lemma-verification`, `normal-decode`, `normal-export`, `readonly-decode`; references in evidence-index.json.
- Coverage: {'candidate_records': 155, 'parsed_records': 155, 'not_captured': 0, 'invalid_records': 0, 'omitted_records': 0}; showing up to 4 nonzero and 6 zero records.
- Missing/ambiguous diagnostics: VERIFIED_FAILED_LOG_WITHOUT_RECOGNIZED_COMPILER_DIAGNOSTIC, MULTIPLE_STAGE_FAILURES_CAUSALITY_UNKNOWN

## Campaign aggregates (source claims)

- No supported aggregate captured; absence from this section does not prove absence from archive.
- Aggregate coverage: {'aggregate_candidates': 0, 'aggregates_captured': 0, 'stage_metadata_captured': 96, 'stage_summaries_retained': 155, 'context_logs_streamed': 8, 'diagnostic_logs_captured': 16, 'diagnostic_log_bytes': 1559465, 'oversized_logs': 0, 'budget_omitted_logs': 143, 'aggregates_not_captured': 0}; showing up to 4.

## Representative cases (source verdicts)

- `allprooflogs/cases/sort4-c1-current-recovery`
- Cases: 1; showing up to 4. More references and source claims in evidence-index.json.

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
