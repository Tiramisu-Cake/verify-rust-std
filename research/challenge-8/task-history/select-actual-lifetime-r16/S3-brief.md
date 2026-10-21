# SmallSort Evidence Brief — fa548e23

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit (source claim): `0`; evidence complete: `True`

## Further bounded evidence

- Complete catalogue: 825 verified members; retained content: 673 files.
- CLI: `smallsort-brief fa548e23-b533-4e27-adce-7a9736e072da --catalogue`, `--search LITERAL`, `--file ID --pointer /key` (JSON), or `--file ID --start 1` (text). Requires the v0.8 client installed on the caller host.
- Reader: `/builds/fa548e23-b533-4e27-adce-7a9736e072da/catalogue?q=literal`, `/search?q=literal`, `/fragment?file_id=ID&start=1` (text) or `&pointer=/key` (JSON). Use the same /builds/UUID prefix for all routes. Search is over sanitized retained data only; inspect coverage and next_offset. No raw fallback or proof inference.

## Failure diagnostics (verified archived sources)

- Diagnostic status: **OBSERVED**; causality: **UNKNOWN**

## Bounded diagnostic context (untrusted observations)

- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/actual-sort4/stage/checked-interior_pointer_limits/lemma-verification.log` line UNKNOWN; SHA-256 `bf777f51587c7e6da77a928e4e0eff93c8efce25284036dad5b587adcf746258`
> L201: (type)
> L202: (type)
> L203: 
> L204: verified/lib.rs(131,1-135,2): error: R16 full-body scope relocation refused: address-taken target local: $_38
> L205: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
> L206: ? ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
> L207: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
> L208: ? ^^^^^^^^^^^^^^^^^^^^^
  - Scanned 10534/10534 bytes; scan limit reached=False; lines shown=8/12.
- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/c1-opt-in-off-negative/stage/body-verification.log` line UNKNOWN; SHA-256 `8288781fbcb2a6c990d825e0db27890882dc4d8601994b864facb3511aa26299`
> L107: 0.008071s: Entering Redux.assume_with_implications(sizeof(void_ptr_typeid) = 8)
> L108: 0.008078s: Exiting Redux.assume_with_implications
> L109: 0.008084s: Exiting Redux.assert_term: 0.000013 seconds
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

- Record counts: EXIT_NONZERO=14, EXIT_ZERO=192; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- `lemma-verification`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/actual-sort4/stage/checked-interior_pointer_limits/lemma-verification-stage.json` line UNKNOWN; SHA-256 `8755b3c0beb5d2479f56a889e370ba5f0df149d4d09446bd609b4d5856b496a8`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 0}
- `body-verification`: exit=`2`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/c1-opt-in-off-negative/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `b4aa8c8310e5101a77353c05ebd4183854efe047fe513144d443108e602e1f62`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 1}
- `body-verification`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/c1-scope-opt-in-off-negative/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `f1ab349587597d021c7d254ae6b766bddbf5aab6997604312bb0bb3571bf89e4`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 2}
- `body-verification`: exit=`2`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/c1-wrong-first-call-line-negative/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `b61f828af21e745efcb588a11a2600d51ce0dc97a86125926d74394d281b7bf5`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 3}
- Expected-control nonzero records (source-classified): 0; details in evidence-index.json.
- Exit 0 observed: `console-build`, `normal-decode`, `normal-export`, `readonly-decode`, `readonly-export`, `refinement`; references in evidence-index.json.
- Coverage: {'candidate_records': 206, 'parsed_records': 206, 'not_captured': 0, 'invalid_records': 0, 'omitted_records': 0}; showing up to 4 nonzero and 6 zero records.
- Missing/ambiguous diagnostics: VERIFIED_FAILED_LOG_WITHOUT_RECOGNIZED_COMPILER_DIAGNOSTIC, MULTIPLE_STAGE_FAILURES_CAUSALITY_UNKNOWN

## Campaign aggregates (source claims)

- No supported aggregate captured; absence from this section does not prove absence from archive.
- Aggregate coverage: {'aggregate_candidates': 0, 'aggregates_captured': 0, 'stage_metadata_captured': 96, 'stage_summaries_retained': 206, 'context_logs_streamed': 8, 'diagnostic_logs_captured': 16, 'diagnostic_log_bytes': 1364464, 'oversized_logs': 2, 'budget_omitted_logs': 192, 'aggregates_not_captured': 0}; showing up to 4.

## Representative cases (source verdicts)

- `allprooflogs/cases/sort4-c1-current-recovery`
- Cases: 1; showing up to 4. More references and source claims in evidence-index.json.

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
