# SmallSort Evidence Brief — 980fbc61

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit (source claim): `0`; evidence complete: `True`

## Further bounded evidence

- Complete catalogue: 819 verified members; retained content: 655 files.
- CLI: `smallsort-brief 980fbc61-2d4c-43f3-9cac-c68db0b34c63 --catalogue`, `--search LITERAL`, `--file ID --pointer /key` (JSON), or `--file ID --start 1` (text). Requires the v0.8 client installed on the caller host.
- Reader: `/builds/980fbc61-2d4c-43f3-9cac-c68db0b34c63/catalogue?q=literal`, `/search?q=literal`, `/fragment?file_id=ID&start=1` (text) or `&pointer=/key` (JSON). Use the same /builds/UUID prefix for all routes. Search is over sanitized retained data only; inspect coverage and next_offset. No raw fallback or proof inference.

## Failure diagnostics (verified archived sources)

- Diagnostic status: **OBSERVED**; causality: **UNKNOWN**

## Bounded diagnostic context (untrusted observations)

- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/actual-sort4/stage/body-verification.log` line UNKNOWN; SHA-256 `31f257428097cb6cb431cacce0d868709e5edd3e15cfb9a947603efe7eccd264`
> L3822: 0.194204s: verified/lib.rs(164,1-30): Executing statement
> L3823: EXEC 2 verified/lib.rs(164,1-30)
> L3824: 0.194216s: verified/lib.rs(164,1-30): Executing statement
> L3825: verified/lib.rs(164,1-30): error: Strict lifetime binding has unresolved inference in entry outer type
> L3826: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
> L3827: ? ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  - Scanned 283103/283103 bytes; scan limit reached=False; lines shown=6/6.
- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/c1-opt-in-off-negative/stage/body-verification.log` line UNKNOWN; SHA-256 `735c54a1003a95bfc79f0c99d9dbf1c63e6263d79264abff89cf42e0384214af`
> L107: 0.012906s: Entering Redux.assume_with_implications(sizeof(void_ptr_typeid) = 8)
> L108: 0.012916s: Exiting Redux.assume_with_implications
> L109: 0.012923s: Exiting Redux.assert_term: 0.000017 seconds
> L110: Fatal error: exception Failure("CALLBACK-UNWIND: source/MIR certificate mismatch: exact callback fixture requires one marker; other bodies forbid it")
> L111: Raised at Stdlib.failwith in file "stdlib.ml", line 29, characters 17-33
> L112: Called from Vf_mir_translator.Make.TrBody.State.fail_callback_unwind in file "?REDACTED_LONG_VALUE?.ml" (inlined), line 3262, characters 8-77
  - Scanned 9794/9794 bytes; scan limit reached=False; lines shown=6/12.
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

- Record counts: EXIT_NONZERO=13, EXIT_ZERO=191; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- `body-verification`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/actual-sort4/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `43d0e62044adceb96ae3bf13f14e8484199c970b83be3b2fa690a93b863538e7`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 0}
- `body-verification`: exit=`2`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/c1-opt-in-off-negative/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `5d1158386242f6733fd3a2fd4118d635bfe75876c91757e0cf6d0144eb44daa0`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 1}
- `body-verification`: exit=`2`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/c1-wrong-first-call-line-negative/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `888b8c7deb15000957e34ab228308fec316421f18b1d4225e9857ecacb4b716c`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 2}
- `body-verification`: exit=`2`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/c1-wrong-source-sha-negative/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `25a4e38fa149d99e33822dca58fa26af70ff6a6e55499fdebddd876df8d5ca24`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 3}
- Expected-control nonzero records (source-classified): 0; details in evidence-index.json.
- Exit 0 observed: `console-build`, `lemma-verification`, `lemma-verification`, `lemma-verification`, `lemma-verification`, `normal-decode`; references in evidence-index.json.
- Coverage: {'candidate_records': 204, 'parsed_records': 204, 'not_captured': 0, 'invalid_records': 0, 'omitted_records': 0}; showing up to 4 nonzero and 6 zero records.
- Missing/ambiguous diagnostics: VERIFIED_FAILED_LOG_WITHOUT_RECOGNIZED_COMPILER_DIAGNOSTIC, MULTIPLE_STAGE_FAILURES_CAUSALITY_UNKNOWN

## Campaign aggregates (source claims)

- No supported aggregate captured; absence from this section does not prove absence from archive.
- Aggregate coverage: {'aggregate_candidates': 0, 'aggregates_captured': 0, 'stage_metadata_captured': 96, 'stage_summaries_retained': 204, 'context_logs_streamed': 8, 'diagnostic_logs_captured': 16, 'diagnostic_log_bytes': 1636573, 'oversized_logs': 2, 'budget_omitted_logs': 190, 'aggregates_not_captured': 0}; showing up to 4.

## Representative cases (source verdicts)

- `allprooflogs/cases/sort4-c1-current-recovery`
- Cases: 1; showing up to 4. More references and source claims in evidence-index.json.

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
