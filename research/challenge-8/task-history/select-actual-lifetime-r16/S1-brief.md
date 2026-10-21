# SmallSort Evidence Brief — 3a973f8c

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit (source claim): `0`; evidence complete: `True`

## Further bounded evidence

- Complete catalogue: 833 verified members; retained content: 665 files.
- CLI: `smallsort-brief 3a973f8c-b4c0-461b-8a2a-908b46c7ee35 --catalogue`, `--search LITERAL`, `--file ID --pointer /key` (JSON), or `--file ID --start 1` (text). Requires the v0.8 client installed on the caller host.
- Reader: `/builds/3a973f8c-b4c0-461b-8a2a-908b46c7ee35/catalogue?q=literal`, `/search?q=literal`, `/fragment?file_id=ID&start=1` (text) or `&pointer=/key` (JSON). Use the same /builds/UUID prefix for all routes. Search is over sanitized retained data only; inspect coverage and next_offset. No raw fallback or proof inference.

## Failure diagnostics (verified archived sources)

- Diagnostic status: **OBSERVED**; causality: **UNKNOWN**

## Bounded diagnostic context (untrusted observations)

- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/actual-sort4/stage/body-verification.log` line UNKNOWN; SHA-256 `25424e5e04a425dc502a39fefb13f0ed1a23a6e3827d99d35c25b14adb482da1`
> L4050: STRICT-CUT-ENTRY name=T_typeid type=*_
> L4051: STRICT-CUT-ENTRY name=F_typeid type=*_
> L4052: STRICT-CUT-ENTRY name='__16_typeid type=*_
> L4053: verified/lib.rs(167,1-30): error: Strict lifetime binding has unresolved inference in entry outer type
> L4054: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
> L4055: ? ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  - Scanned 294217/294217 bytes; scan limit reached=False; lines shown=6/6.
- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/c1-opt-in-off-negative/stage/body-verification.log` line UNKNOWN; SHA-256 `72b55533782fdb720c4b5d617011e4cf8a65fbd555b4c3d15daae2ca762b3ffb`
> L107: 0.012523s: Entering Redux.assume_with_implications(sizeof(void_ptr_typeid) = 8)
> L108: 0.012532s: Exiting Redux.assume_with_implications
> L109: 0.012538s: Exiting Redux.assert_term: 0.000015 seconds
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

- Record counts: EXIT_NONZERO=13, EXIT_ZERO=195; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- `body-verification`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/actual-sort4/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `07d98a2eb0e3a3df249b3336b99f25e493d0d45f4fbf01a300eca79a43c31f6e`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 0}
- `body-verification`: exit=`2`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/c1-opt-in-off-negative/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `0fbe9b10cec8362259414c2c8ded84021bc886753523b00f3624665adabb3de6`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 1}
- `body-verification`: exit=`2`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/c1-wrong-first-call-line-negative/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `7b535c32a01c3bc43bd06ee80006de0232cb33fca12e6cd51edb33e44ea6d54f`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 2}
- `body-verification`: exit=`2`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-actual-body/c1-wrong-source-sha-negative/stage/body-verification-stage.json` line UNKNOWN; SHA-256 `3783e0a02df7a82fd9ef1cd8cd9453a2165c878195919eb06bc0f9829f1cc9ca`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 3}
- Expected-control nonzero records (source-classified): 0; details in evidence-index.json.
- Exit 0 observed: `console-build`, `lemma-verification`, `lemma-verification`, `lemma-verification`, `lemma-verification`, `normal-decode`; references in evidence-index.json.
- Coverage: {'candidate_records': 208, 'parsed_records': 208, 'not_captured': 0, 'invalid_records': 0, 'omitted_records': 0}; showing up to 4 nonzero and 6 zero records.
- Missing/ambiguous diagnostics: VERIFIED_FAILED_LOG_WITHOUT_RECOGNIZED_COMPILER_DIAGNOSTIC, MULTIPLE_STAGE_FAILURES_CAUSALITY_UNKNOWN

## Campaign aggregates (source claims)

- No supported aggregate captured; absence from this section does not prove absence from archive.
- Aggregate coverage: {'aggregate_candidates': 0, 'aggregates_captured': 0, 'stage_metadata_captured': 96, 'stage_summaries_retained': 208, 'context_logs_streamed': 8, 'diagnostic_logs_captured': 16, 'diagnostic_log_bytes': 1647687, 'oversized_logs': 2, 'budget_omitted_logs': 194, 'aggregates_not_captured': 0}; showing up to 4.

## Representative cases (source verdicts)

- `allprooflogs/cases/sort4-c1-current-recovery`
- Cases: 1; showing up to 4. More references and source claims in evidence-index.json.

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
