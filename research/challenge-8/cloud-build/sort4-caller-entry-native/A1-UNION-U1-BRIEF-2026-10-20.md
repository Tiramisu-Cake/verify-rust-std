# SmallSort Evidence Brief — a58c94a8

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit (source claim): `0`; evidence complete: `True`

## Further bounded evidence

- Complete catalogue: 669 verified members; retained content: 592 files.
- CLI: `smallsort-brief a58c94a8-c080-4d41-9833-ac1d77b00bb0 --catalogue`, `--search LITERAL`, `--file ID --pointer /key` (JSON), or `--file ID --start 1` (text). Requires the v0.8 client installed on the caller host.
- Reader: `/builds/a58c94a8-c080-4d41-9833-ac1d77b00bb0/catalogue?q=literal`, `/search?q=literal`, `/fragment?file_id=ID&start=1` (text) or `&pointer=/key` (JSON). Use the same /builds/UUID prefix for all routes. Search is over sanitized retained data only; inspect coverage and next_offset. No raw fallback or proof inference.

## Failure diagnostics (verified archived sources)

- Diagnostic status: **SOURCE_REPORTED**; causality: **UNKNOWN**
- Runner-reported blocker: `P0a` / `adapter_error`; detail: RuntimeError: A1-FOCUS: published A1 profile identity
  - Source: `proof-audit.json` line UNKNOWN; SHA-256 `fed6b2cd98ae5e38e8d0c45d6433ed25241d09a36d8e5a0d7342722fa6584e1c`

## Bounded diagnostic context (untrusted observations)

- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-off-observation/proof-ast-diagnostic.log` line UNKNOWN; SHA-256 `961444770a7bf9baa766a2419f9c391d98a31f0115f6fa9ddbd005a9db6aa02b`
> L191: EXEC 48 ?REDACTED_LONG_VALUE?.rsspec(476,9-11)
> L192: EXEC 46 ?REDACTED_LONG_VALUE?.rsspec(477,53-54)
> L193: EXEC 47 ?REDACTED_LONG_VALUE?.rsspec(479,53-54)
> L194: verified/lib.rs(13,8-18): error: Duplicate type parameter ''_'.
> L195: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
> L196: ? ^^^^^^^^^^
  - Scanned 22594/22594 bytes; scan limit reached=False; lines shown=6/6.
- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-off-observation/verification.log` line UNKNOWN; SHA-256 `6cd41afd67e488d881639bc34fc4af07f758129b1e9d5c240cb92b69fdb5cce4`
> L1591: 0.154827s: Exiting Redux.assert_term: 0.000005 seconds
> L1592: 0.154836s: Entering Redux.assume(true ==? alignof(std::sync::atomic::Atomic_type_info(uintptr_t_typeid)) = 8)
> L1593: 0.154850s: Exiting Redux.assume: 0.000005 seconds
> L1594: verified/lib.rs(13,8-18): error: Duplicate type parameter ''_'.
> L1595: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
> L1596: ? ^^^^^^^^^^
  - Scanned 148892/148892 bytes; scan limit reached=False; lines shown=6/6.
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

- Record counts: EXIT_NONZERO=8, EXIT_ZERO=153; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- `proof-ast-diagnostic`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-off-observation/proof-ast-diagnostic-stage.json` line UNKNOWN; SHA-256 `35384a2cf3b75918ba48e8c53562113e3a051ba54851a9e64a550857a5063b37`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 0}
- `verification`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-off-observation/verification-stage.json` line UNKNOWN; SHA-256 `cceb9bee4b03572c1f065ff139de4e7c000d8c3ee498333e924fe61f088bc2f1`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 1}
- `proof-ast-diagnostic`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/cases/consumer-missing-raw-rights/proof-ast-diagnostic-stage.json` line UNKNOWN; SHA-256 `75772f14765bbc3916251559842288879721dec137df4cb8df8e135980ea8c6e`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 2}
- `verification`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/cases/consumer-missing-raw-rights/verification-stage.json` line UNKNOWN; SHA-256 `319473e02f90aaf035fe38b023bcd14a35ab4d0417aa085e5d88faf386dd33ad`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 3}
- Expected-control nonzero records (source-classified): 0; details in evidence-index.json.
- Exit 0 observed: `console-build`, `normal-decode`, `normal-export`, `readonly-decode`, `readonly-export`, `refinement`; references in evidence-index.json.
- Coverage: {'candidate_records': 161, 'parsed_records': 161, 'not_captured': 0, 'invalid_records': 0, 'omitted_records': 0}; showing up to 4 nonzero and 6 zero records.
- Runner-reported cases: 26; INCONCLUSIVE=5, INTENDED_CLASSIFIED=8, NOT_RUN=13
- Missing/ambiguous diagnostics: VERIFIED_FAILED_LOG_WITHOUT_RECOGNIZED_COMPILER_DIAGNOSTIC, MULTIPLE_STAGE_FAILURES_CAUSALITY_UNKNOWN

## Campaign aggregates (source claims)

- No supported aggregate captured; absence from this section does not prove absence from archive.
- Aggregate coverage: {'aggregate_candidates': 0, 'aggregates_captured': 0, 'stage_metadata_captured': 96, 'stage_summaries_retained': 161, 'context_logs_streamed': 8, 'diagnostic_logs_captured': 16, 'diagnostic_log_bytes': 1437196, 'oversized_logs': 0, 'budget_omitted_logs': 149, 'aggregates_not_captured': 0}; showing up to 4.

## Representative cases (source verdicts)

- `allprooflogs/cases/sort4-c1-current-recovery`
- Cases: 1; showing up to 4. More references and source claims in evidence-index.json.

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
