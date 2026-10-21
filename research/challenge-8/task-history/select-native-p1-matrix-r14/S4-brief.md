# SmallSort Evidence Brief — 26430454

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit (source claim): `0`; evidence complete: `True`

## Further bounded evidence

- Complete catalogue: 1116 verified members; retained content: 616 files.
- CLI: `smallsort-brief 26430454-03d6-494e-accd-cabea958df74 --catalogue`, `--search LITERAL`, `--file ID --pointer /key` (JSON), or `--file ID --start 1` (text). Requires the v0.8 client installed on the caller host.
- Reader: `/builds/26430454-03d6-494e-accd-cabea958df74/catalogue?q=literal`, `/search?q=literal`, `/fragment?file_id=ID&start=1` (text) or `&pointer=/key` (JSON). Use the same /builds/UUID prefix for all routes. Search is over sanitized retained data only; inspect coverage and next_offset. No raw fallback or proof inference.

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
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-off-observation/proof-ast-diagnostic.log` line UNKNOWN; SHA-256 `961444770a7bf9baa766a2419f9c391d98a31f0115f6fa9ddbd005a9db6aa02b`
> L191: EXEC 48 ?REDACTED_LONG_VALUE?.rsspec(476,9-11)
> L192: EXEC 46 ?REDACTED_LONG_VALUE?.rsspec(477,53-54)
> L193: EXEC 47 ?REDACTED_LONG_VALUE?.rsspec(479,53-54)
> L194: verified/lib.rs(13,8-18): error: Duplicate type parameter ''_'.
> L195: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
> L196: ? ^^^^^^^^^^
  - Scanned 22594/22594 bytes; scan limit reached=False; lines shown=6/6.
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

- Record counts: EXIT_NONZERO=24, EXIT_ZERO=225; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- `r-only-native-reference`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-native-reference/P1/r-only-native-reference-stage.json` line UNKNOWN; SHA-256 `5dc7dd85f52d92e386d95b36ee79ffec11718205ac94f1b429e0f256bbf63082`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 0}
- `proof-ast-diagnostic`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-off-observation/proof-ast-diagnostic-stage.json` line UNKNOWN; SHA-256 `35384a2cf3b75918ba48e8c53562113e3a051ba54851a9e64a550857a5063b37`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 1}
- `verification`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-off-observation/verification-stage.json` line UNKNOWN; SHA-256 `d3f7c6ebb30c8348eae6b939af4cd1c748d07822b83368789b78807b1e2a819c`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 2}
- `reference-own`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-reference-own-probe/negative-generic-erasure/stage/reference-own-stage.json` line UNKNOWN; SHA-256 `9a79e8cff3cce09bf188747bdec01325880fccc2c6d844891ee8962c1bbc110d`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 3}
- Expected-control nonzero records (source-classified): 0; details in evidence-index.json.
- Exit 0 observed: `console-build`, `normal-decode`, `normal-export`, `readonly-decode`, `readonly-export`, `refinement`; references in evidence-index.json.
- Coverage: {'candidate_records': 249, 'parsed_records': 249, 'not_captured': 0, 'invalid_records': 0, 'omitted_records': 0}; showing up to 4 nonzero and 6 zero records.
- Runner-reported cases: 26; INTENDED_CLASSIFIED=26
- Missing/ambiguous diagnostics: VERIFIED_FAILED_LOG_WITHOUT_RECOGNIZED_COMPILER_DIAGNOSTIC, MULTIPLE_STAGE_FAILURES_CAUSALITY_UNKNOWN

## Campaign aggregates (source claims)

- No supported aggregate captured; absence from this section does not prove absence from archive.
- Aggregate coverage: {'aggregate_candidates': 0, 'aggregates_captured': 0, 'stage_metadata_captured': 96, 'stage_summaries_retained': 249, 'context_logs_streamed': 8, 'diagnostic_logs_captured': 16, 'diagnostic_log_bytes': 458951, 'oversized_logs': 0, 'budget_omitted_logs': 237, 'aggregates_not_captured': 0}; showing up to 4.

## Representative cases (source verdicts)

- `allprooflogs/cases/sort4-c1-current-recovery`
- Cases: 1; showing up to 4. More references and source claims in evidence-index.json.

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
