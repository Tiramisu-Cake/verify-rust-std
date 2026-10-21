# SmallSort Evidence Brief — b06e1738

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit (source claim): `0`; evidence complete: `True`

## Further bounded evidence

- Complete catalogue: 600 verified members; retained content: 551 files.
- CLI: `smallsort-brief b06e1738-89cb-467d-8f46-7ea26585fdb2 --catalogue`, `--search LITERAL`, `--file ID --pointer /key` (JSON), or `--file ID --start 1` (text). Requires the v0.8 client installed on the caller host.
- Reader: `/builds/b06e1738-89cb-467d-8f46-7ea26585fdb2/catalogue?q=literal`, `/search?q=literal`, `/fragment?file_id=ID&start=1` (text) or `&pointer=/key` (JSON). Use the same /builds/UUID prefix for all routes. Search is over sanitized retained data only; inspect coverage and next_offset. No raw fallback or proof inference.

## Failure diagnostics (verified archived sources)

- Diagnostic status: **OBSERVED**; causality: **UNKNOWN**

## Bounded diagnostic context (untrusted observations)

- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/join_four_owned_cells-positive/stage/body-verification.log` line UNKNOWN; SHA-256 `2e64235bf13271acebde4646a453d81123259cf3de1ee5aacad1d3968aefc68c`
> L108: 0.015127s: Exiting Redux.assume_with_implications
> L109: 0.015135s: Exiting Redux.assert_term: 0.000018 seconds
> L110: 
> L111: Fatal error: exception Failure("TODO")
> L112: Raised at Stdlib.failwith in file "stdlib.ml", line 29, characters 17-33
> L113: Called from Stdlib__List.map in file "list.ml", line 92, characters 20-23
> L114: Called from Stdlib__List.map in file "list.ml", line 92, characters 32-39
> L115: Called from Stdlib__List.map in file "list.ml", line 92, characters 32-39
  - Scanned 10566/10566 bytes; scan limit reached=False; lines shown=8/12.
- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/raw-four-copy-duplicate-owner-negative/stage/checked-four_copy_optional_destination_limits/lemma-verification.log` line UNKNOWN; SHA-256 `0bd7ac40eca233c7ceb08a3451633b67ce9a6d64ee43264a56213434d25bf8f3`
> L1107: 0.144398s: Entering Redux.assume_with_implications(!(0 ?= sizeof(T_typeid)))
> L1108: 0.144441s: Exiting Redux.assume_with_implications
> L1109: 0.144449s: Exiting Redux.query
> L1110: ?REDACTED_LONG_VALUE?.rsspec(24,9-10): error: Cannot prove condition. (Cannot prove 0 ?= sizeof(T_typeid).)
> L1111: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
> L1112: ? ^
> L1113: ?REDACTED_LONG_VALUE?.rsspec(24,9-10): note: Consuming expression
> L1114: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
  - Scanned 83256/83256 bytes; scan limit reached=False; lines shown=8/12.
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

- Record counts: EXIT_NONZERO=10, EXIT_ZERO=145; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- `body-verification`: exit=`2`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/join_four_owned_cells-positive/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `c8b0b29fedcd37201fbfa9ad207a7c5704c27a274ccf77396d987e1d6a89508a`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 0}
- `lemma-verification`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/raw-four-copy-duplicate-owner-negative/stage/checked-four_copy_optional_destination_limits/lemma-verification-stage.json` line UNKNOWN; SHA-256 `b594583ade480f0c7c508848ac285a05c6aa2f738353f2d4ef3ca88b3b2c7ce6`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 1}
- `lemma-verification`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/raw-four-copy-identity-positive/stage/checked-four_copy_optional_destination_limits/lemma-verification-stage.json` line UNKNOWN; SHA-256 `e55fd921a41bc715f5e6d5ba269943b6a320249179dfae5a53fa6a37acfaa18b`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 2}
- `lemma-verification`: exit=`2`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/recover-pair-missing-half-negative/stage/checked-recover_pair/lemma-verification-stage.json` line UNKNOWN; SHA-256 `6b96de53c8ec2232b0eeac91d95a1c2809ac4a297979be9c077c629cac80d793`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 3}
- Expected-control nonzero records (source-classified): 0; details in evidence-index.json.
- Exit 0 observed: `console-build`, `normal-decode`, `normal-export`, `readonly-decode`, `readonly-export`, `refinement`; references in evidence-index.json.
- Coverage: {'candidate_records': 155, 'parsed_records': 155, 'not_captured': 0, 'invalid_records': 0, 'omitted_records': 0}; showing up to 4 nonzero and 6 zero records.
- Missing/ambiguous diagnostics: VERIFIED_FAILED_LOG_WITHOUT_RECOGNIZED_COMPILER_DIAGNOSTIC, MULTIPLE_STAGE_FAILURES_CAUSALITY_UNKNOWN

## Campaign aggregates (source claims)

- No supported aggregate captured; absence from this section does not prove absence from archive.
- Aggregate coverage: {'aggregate_candidates': 0, 'aggregates_captured': 0, 'stage_metadata_captured': 96, 'stage_summaries_retained': 155, 'context_logs_streamed': 8, 'diagnostic_logs_captured': 16, 'diagnostic_log_bytes': 512087, 'oversized_logs': 0, 'budget_omitted_logs': 143, 'aggregates_not_captured': 0}; showing up to 4.

## Representative cases (source verdicts)

- `allprooflogs/cases/sort4-c1-current-recovery`
- Cases: 1; showing up to 4. More references and source claims in evidence-index.json.

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
