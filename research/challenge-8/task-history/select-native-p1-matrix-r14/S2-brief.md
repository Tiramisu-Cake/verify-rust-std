# SmallSort Evidence Brief — 2b30e563

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit (source claim): `0`; evidence complete: `True`

## Further bounded evidence

- Complete catalogue: 634 verified members; retained content: 547 files.
- CLI: `smallsort-brief 2b30e563-011a-4cfe-a739-187a9e612d07 --catalogue`, `--search LITERAL`, `--file ID --pointer /key` (JSON), or `--file ID --start 1` (text). Requires the v0.8 client installed on the caller host.
- Reader: `/builds/2b30e563-011a-4cfe-a739-187a9e612d07/catalogue?q=literal`, `/search?q=literal`, `/fragment?file_id=ID&start=1` (text) or `&pointer=/key` (JSON). Use the same /builds/UUID prefix for all routes. Search is over sanitized retained data only; inspect coverage and next_offset. No raw fallback or proof inference.

## Failure diagnostics (verified archived sources)

- Diagnostic status: **OBSERVED**; causality: **UNKNOWN**

## Bounded diagnostic context (untrusted observations)

- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-native-reference/P1/r-only-native-reference.log` line UNKNOWN; SHA-256 `0fd042b148adff3bcf4c8d0f288e169c15127b1402ec8b836a16b10f4a757455`
> L25: (type), (type)
> L26: WARNING: fn_specializer: rerouting call of StableSmallSortTypeImpl::small_sort to ?T as StableSmallSortTypeImpl?::small_sort: ignoring clause (type) : std::marker::Sized??
> L27: WARNING: fn_specializer: rerouting call of StableSmallSortTypeImpl::small_sort to ?T as StableSmallSortTypeImpl?::small_sort: ignoring clause (type) : FreezeMarker??
> L28: verified/lib.rs(32,8-28): error: Duplicate function prototype.
> L29: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
> L30: ? ^^^^^^^^^^^^^^^^^^^^
  - Scanned 2071/2071 bytes; scan limit reached=False; lines shown=6/6.
- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-reference-own-probe/negative-generic-erasure/stage/reference-own.log` line UNKNOWN; SHA-256 `f5a22df91fd33a9ecf18da34b845418937514115b4909c2d9d8e1c1f69989844`
> L1128: 0.132878s: Exiting Redux.assume_with_implications
> L1129: 0.132883s: Exiting Redux.query
> L1130: 0.132891s: verified/lib.rs(12,1-2): Leak check.
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

- Record counts: EXIT_NONZERO=6, EXIT_ZERO=141; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- `r-only-native-reference`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-native-reference/P1/r-only-native-reference-stage.json` line UNKNOWN; SHA-256 `5dc7dd85f52d92e386d95b36ee79ffec11718205ac94f1b429e0f256bbf63082`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 0}
- `reference-own`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-reference-own-probe/negative-generic-erasure/stage/reference-own-stage.json` line UNKNOWN; SHA-256 `7f2daac1ac7074ac32bb62d67a205b60e0dd3ef3cf845c6b58208c471118faf1`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 1}
- `reference-own`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-reference-own-probe/negative-lifetime-redirect/stage/reference-own-stage.json` line UNKNOWN; SHA-256 `c12ae15811395514f4cff0ab107ed3902062608bf28c54835511182ece3522af`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 2}
- `reference-own`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-reference-own-probe/negative-mutable-erasure/stage/reference-own-stage.json` line UNKNOWN; SHA-256 `d61c60a3ace34ec7f8caae32e06737b0e3379b3cbbd0a97078f7ad873537145a`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 3}
- Expected-control nonzero records (source-classified): 0; details in evidence-index.json.
- Exit 0 observed: `console-build`, `reference-own`, `reference-own`, `reference-own`, `reference-own`, `synthetic-encode`; references in evidence-index.json.
- Coverage: {'candidate_records': 147, 'parsed_records': 147, 'not_captured': 0, 'invalid_records': 0, 'omitted_records': 0}; showing up to 4 nonzero and 6 zero records.
- Runner-reported cases: 26; INTENDED_CLASSIFIED=7, NOT_RUN=19
- Missing/ambiguous diagnostics: VERIFIED_FAILED_LOG_WITHOUT_RECOGNIZED_COMPILER_DIAGNOSTIC, MULTIPLE_STAGE_FAILURES_CAUSALITY_UNKNOWN

## Campaign aggregates (source claims)

- No supported aggregate captured; absence from this section does not prove absence from archive.
- Aggregate coverage: {'aggregate_candidates': 0, 'aggregates_captured': 0, 'stage_metadata_captured': 96, 'stage_summaries_retained': 147, 'context_logs_streamed': 6, 'diagnostic_logs_captured': 16, 'diagnostic_log_bytes': 688040, 'oversized_logs': 0, 'budget_omitted_logs': 135, 'aggregates_not_captured': 0}; showing up to 4.

## Representative cases (source verdicts)

- `allprooflogs/cases/sort4-c1-current-recovery`
- Cases: 1; showing up to 4. More references and source claims in evidence-index.json.

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
