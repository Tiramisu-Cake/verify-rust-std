# SmallSort Evidence Brief — 90e812ed

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit (source claim): `0`; evidence complete: `True`

## Further bounded evidence

- Complete catalogue: 706 verified members; retained content: 630 files.
- CLI: `smallsort-brief 90e812ed-233d-4a3a-a836-ab544ce36ff5 --catalogue`, `--search LITERAL`, `--file ID --pointer /key` (JSON), or `--file ID --start 1` (text). Requires the v0.8 client installed on the caller host.
- Reader: `/builds/90e812ed-233d-4a3a-a836-ab544ce36ff5/catalogue?q=literal`, `/search?q=literal`, `/fragment?file_id=ID&start=1` (text) or `&pointer=/key` (JSON). Use the same /builds/UUID prefix for all routes. Search is over sanitized retained data only; inspect coverage and next_offset. No raw fallback or proof inference.

## Failure diagnostics (verified archived sources)

- Diagnostic status: **OBSERVED**; causality: **UNKNOWN**

## Bounded diagnostic context (untrusted observations)

- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/actual-sort4/stage/checked-interior_pointer_limits/lemma-verification.log` line UNKNOWN; SHA-256 `702fabfaa1c66bc01756aa384fe28edd44484cc62f347b6fe723b02be1186fe1`
> L138: 
> L139: 
> L140: (type)
> L141: Fatal error: exception Failure("CALLBACK-UNWIND: source/MIR certificate mismatch: next call is not the exact two-argument FnMut::call_mut")
> L142: Raised at Stdlib.failwith in file "stdlib.ml", line 29, characters 17-33
> L143: Called from Vf_mir_translator.Make.TrBody.State.fail_callback_unwind in file "?REDACTED_LONG_VALUE?.ml" (inlined), line 3261, characters 8-77
> L144: Called from Vf_mir_translator.Make.TrBody.translate_fn_call.(fun) in file "?REDACTED_LONG_VALUE?.ml", line 4565, characters 20-82
  - Scanned 13425/13425 bytes; scan limit reached=False; lines shown=7/12.
- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/c1-opt-in-off-negative/stage/body-verification.log` line UNKNOWN; SHA-256 `8ada56ac43a520388e93ecd9de1d80232276b0d9ac9989f8095bcfcaed6a5468`
> L107: 0.013146s: Entering Redux.assume_with_implications(sizeof(void_ptr_typeid) = 8)
> L108: 0.013155s: Exiting Redux.assume_with_implications
> L109: 0.013162s: Exiting Redux.assert_term: 0.000018 seconds
> L110: Fatal error: exception Failure("CALLBACK-UNWIND: source/MIR certificate mismatch: exact callback fixture requires one marker; other bodies forbid it")
> L111: Raised at Stdlib.failwith in file "stdlib.ml", line 29, characters 17-33
> L112: Called from Vf_mir_translator.Make.TrBody.State.fail_callback_unwind in file "?REDACTED_LONG_VALUE?.ml" (inlined), line 3261, characters 8-77
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

- Record counts: EXIT_NONZERO=13, EXIT_ZERO=166; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- `lemma-verification`: exit=`2`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/actual-sort4/stage/checked-interior_pointer_limits/lemma-verification-stage.json` line UNKNOWN; SHA-256 `44cde52851317f61ffe19c1204894c08f50ebaf55d003b50aeb413e51d9633a3`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 0}
- `body-verification`: exit=`2`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/c1-opt-in-off-negative/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `bf4b235b9d3c659d2309a3905281de13b2d0a630b9d0e64f8271d484fb916cdb`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 1}
- `body-verification`: exit=`2`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/c1-wrong-first-call-line-negative/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `7c7a909d5c8271694f07c8742c839138ea853f704455ba1439e12a29357539a5`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 2}
- `body-verification`: exit=`2`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/c1-wrong-source-sha-negative/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `fdbe546d2f92558f875211a3401d6faa94dcd928f09013f433dc255981f4be49`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 3}
- Expected-control nonzero records (source-classified): 0; details in evidence-index.json.
- Exit 0 observed: `console-build`, `normal-decode`, `normal-export`, `readonly-decode`, `readonly-export`, `refinement`; references in evidence-index.json.
- Coverage: {'candidate_records': 179, 'parsed_records': 179, 'not_captured': 0, 'invalid_records': 0, 'omitted_records': 0}; showing up to 4 nonzero and 6 zero records.
- Missing/ambiguous diagnostics: VERIFIED_FAILED_LOG_WITHOUT_RECOGNIZED_COMPILER_DIAGNOSTIC, MULTIPLE_STAGE_FAILURES_CAUSALITY_UNKNOWN

## Campaign aggregates (source claims)

- No supported aggregate captured; absence from this section does not prove absence from archive.
- Aggregate coverage: {'aggregate_candidates': 0, 'aggregates_captured': 0, 'stage_metadata_captured': 96, 'stage_summaries_retained': 179, 'context_logs_streamed': 8, 'diagnostic_logs_captured': 16, 'diagnostic_log_bytes': 945631, 'oversized_logs': 0, 'budget_omitted_logs': 167, 'aggregates_not_captured': 0}; showing up to 4.

## Representative cases (source verdicts)

- `allprooflogs/cases/sort4-c1-current-recovery`
- Cases: 1; showing up to 4. More references and source claims in evidence-index.json.

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
