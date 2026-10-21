# SmallSort Evidence Brief — 4df683dc

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit (source claim): `0`; evidence complete: `True`

## Further bounded evidence

- Complete catalogue: 883 verified members; retained content: 685 files.
- CLI: `smallsort-brief 4df683dc-41cb-4e4d-b1ce-d515e8f96b00 --catalogue`, `--search LITERAL`, `--file ID --pointer /key` (JSON), or `--file ID --start 1` (text). Requires the v0.8 client installed on the caller host.
- Reader: `/builds/4df683dc-41cb-4e4d-b1ce-d515e8f96b00/catalogue?q=literal`, `/search?q=literal`, `/fragment?file_id=ID&start=1` (text) or `&pointer=/key` (JSON). Use the same /builds/UUID prefix for all routes. Search is over sanitized retained data only; inspect coverage and next_offset. No raw fallback or proof inference.

## Failure diagnostics (verified archived sources)

- Diagnostic status: **OBSERVED**; causality: **UNKNOWN**

## Bounded diagnostic context (untrusted observations)

- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/actual-sort4/stage/body-verification.log` line UNKNOWN; SHA-256 `e858862c254c7e3f30d13ceb9022bc21649d2ed229781bfb88936795433db961`
> L6570: 0.215348s: Exiting Redux.assume: 0.000017 seconds
> L6571: 0.215354s: verified/lib.rs(198,18-89): Executing statement
> L6572: EXEC 40 verified/lib.rs(198,18-89)
> L6573: verified/lib.rs(198,18-89): error: Type mismatch. Actual: ?F as std::ops::FnOnce?std_tuple_2_?&'cmp T, &'cmp T???::Output. Expected: bool.
> L6574: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
> L6575: ? ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  - Scanned 472536/472536 bytes; scan limit reached=False; lines shown=6/6.
- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/c1-opt-in-off-negative/stage/body-verification.log` line UNKNOWN; SHA-256 `3f33123c3bb807a249ed5319fcf9602d125036537056e8d17d24735eba3d46f4`
> L107: 0.012418s: Entering Redux.assume_with_implications(sizeof(void_ptr_typeid) = 8)
> L108: 0.012427s: Exiting Redux.assume_with_implications
> L109: 0.012433s: Exiting Redux.assert_term: 0.000015 seconds
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

- Record counts: EXIT_NONZERO=14, EXIT_ZERO=206; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- `body-verification`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/actual-sort4/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `b4cceb5b8e304c430864def3e0df84d211e818b69bf191b97060525b8fefea8a`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 0}
- `body-verification`: exit=`2`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/c1-opt-in-off-negative/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `85ba0f0c67e858786e522d21c27b7b00c28230754959b605c4960deeb465dee6`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 1}
- `body-verification`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/c1-scope-opt-in-off-negative/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `cd3a9bfaabf32a964c084d56821c3ffb62159e90bc3cab6efee84bead1ea125a`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 2}
- `body-verification`: exit=`2`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/c1-wrong-first-call-line-negative/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `8667cb557919e05d83f9c45f5838ff5449adb051a976f21e70f53494c8b7a4cb`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 3}
- Expected-control nonzero records (source-classified): 0; details in evidence-index.json.
- Exit 0 observed: `console-build`, `lemma-verification`, `lemma-verification`, `lemma-verification`, `lemma-verification`, `normal-decode`; references in evidence-index.json.
- Coverage: {'candidate_records': 220, 'parsed_records': 220, 'not_captured': 0, 'invalid_records': 0, 'omitted_records': 0}; showing up to 4 nonzero and 6 zero records.
- Missing/ambiguous diagnostics: VERIFIED_FAILED_LOG_WITHOUT_RECOGNIZED_COMPILER_DIAGNOSTIC, MULTIPLE_STAGE_FAILURES_CAUSALITY_UNKNOWN

## Campaign aggregates (source claims)

- No supported aggregate captured; absence from this section does not prove absence from archive.
- Aggregate coverage: {'aggregate_candidates': 0, 'aggregates_captured': 0, 'stage_metadata_captured': 96, 'stage_summaries_retained': 220, 'context_logs_streamed': 8, 'diagnostic_logs_captured': 16, 'diagnostic_log_bytes': 1986491, 'oversized_logs': 2, 'budget_omitted_logs': 206, 'aggregates_not_captured': 0}; showing up to 4.

## Representative cases (source verdicts)

- `allprooflogs/cases/sort4-c1-current-recovery`
- Cases: 1; showing up to 4. More references and source claims in evidence-index.json.

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
