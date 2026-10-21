# SmallSort Evidence Brief — 8d07c434

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit (source claim): `0`; evidence complete: `True`

## Further bounded evidence

- Complete catalogue: 563 verified members; retained content: 520 files.
- CLI: `smallsort-brief 8d07c434-daff-412c-a214-0e91a521fec2 --catalogue`, `--search LITERAL`, `--file ID --pointer /key` (JSON), or `--file ID --start 1` (text). Requires the v0.8 client installed on the caller host.
- Reader: `/builds/8d07c434-daff-412c-a214-0e91a521fec2/catalogue?q=literal`, `/search?q=literal`, `/fragment?file_id=ID&start=1` (text) or `&pointer=/key` (JSON). Use the same /builds/UUID prefix for all routes. Search is over sanitized retained data only; inspect coverage and next_offset. No raw fallback or proof inference.

## Failure diagnostics (verified archived sources)

- Diagnostic status: **OBSERVED**; causality: **UNKNOWN**

## Bounded diagnostic context (untrusted observations)

- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/generic-four-recover_four_missing_fourth_end_token_negative-negative/stage/body-verification.log` line UNKNOWN; SHA-256 `98356f9c7703dbcb3ea5165b3ac4c7b11c6a5e9fd7ecc966fb123118358585ab`
> L1098: 0.143787s: verified/lib.rs(55,5-21): Consuming assertion
> L1099: 0.143810s: Redux: Axiom ptr_add_ triggered
> L1100: 0.143872s: Consuming chunk borrow_end_token(k, @(@(full_borrow_content(T_typeid), t), ptr_add_(base, 3, T_typeid)))
> L1101: verified/lib.rs(55,5-21): error: No matching heap chunks: borrow_end_token(k, @(@(full_borrow_content(T_typeid), t), ptr_add_(base, 3, T_typeid)))
> L1102: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
> L1103: ? ^^^^^^^^^^^^^^^^
> L1104: verified/lib.rs(55,5-21): note: Consuming assertion
> L1105: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
  - Scanned 85253/85253 bytes; scan limit reached=False; lines shown=8/12.
- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-reference-own-probe/negative-generic-erasure/stage/reference-own.log` line UNKNOWN; SHA-256 `c306dbe0869725154e31e7b706e5043d3f996d28b56cb1d85802bbd0ab57fc09`
> L1128: 0.139364s: Exiting Redux.assume_with_implications
> L1129: 0.139370s: Exiting Redux.query
> L1130: 0.139376s: verified/lib.rs(12,1-2): Leak check.
> L1131: verified/lib.rs(12,1-2): error: Function leaks heap chunks: own(T_typeid)(t, 0)
> L1132: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
> L1133: ? ^
> L1134: verified/lib.rs(12,1-2): note: Leak check.
> L1135: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
  - Scanned 84936/84936 bytes; scan limit reached=False; lines shown=8/12.
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

- Record counts: EXIT_NONZERO=6, EXIT_ZERO=142; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- `body-verification`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/generic-four-recover_four_missing_fourth_end_token_negative-negative/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `a1036ec37ff3e9d16b5b9871661ae7c2dea08983d5504520af3b0b7b4df8211b`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 0}
- `reference-own`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-reference-own-probe/negative-generic-erasure/stage/reference-own-stage.json` line UNKNOWN; SHA-256 `57c9ab512d2794bd9cf9996c81404d086e6de00bf65d1b9b1504f15b1fe24833`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 1}
- `reference-own`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-reference-own-probe/negative-lifetime-redirect/stage/reference-own-stage.json` line UNKNOWN; SHA-256 `36d4969374713b7f698e3c47336de400db3f6b6b325fec65097790479c1a53ab`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 2}
- `reference-own`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-reference-own-probe/negative-mutable-erasure/stage/reference-own-stage.json` line UNKNOWN; SHA-256 `5ca8eb0f6aba4b3ef92743ec46940507021925c7d3dd49ff3dc4da068ef3e9a2`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 3}
- Expected-control nonzero records (source-classified): 0; details in evidence-index.json.
- Exit 0 observed: `console-build`, `body-verification`, `normal-decode`, `normal-export`, `readonly-decode`, `readonly-export`; references in evidence-index.json.
- Coverage: {'candidate_records': 148, 'parsed_records': 148, 'not_captured': 0, 'invalid_records': 0, 'omitted_records': 0}; showing up to 4 nonzero and 6 zero records.
- Missing/ambiguous diagnostics: VERIFIED_FAILED_LOG_WITHOUT_RECOGNIZED_COMPILER_DIAGNOSTIC, MULTIPLE_STAGE_FAILURES_CAUSALITY_UNKNOWN

## Campaign aggregates (source claims)

- No supported aggregate captured; absence from this section does not prove absence from archive.
- Aggregate coverage: {'aggregate_candidates': 0, 'aggregates_captured': 0, 'stage_metadata_captured': 96, 'stage_summaries_retained': 148, 'context_logs_streamed': 6, 'diagnostic_logs_captured': 16, 'diagnostic_log_bytes': 797573, 'oversized_logs': 0, 'budget_omitted_logs': 136, 'aggregates_not_captured': 0}; showing up to 4.

## Representative cases (source verdicts)

- `allprooflogs/cases/sort4-c1-current-recovery`
- Cases: 1; showing up to 4. More references and source claims in evidence-index.json.

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
