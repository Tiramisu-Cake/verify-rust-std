# SmallSort Evidence Brief — 6019f7c5

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit (source claim): `1`; evidence complete: `True`

## Further bounded evidence

- Complete catalogue: 2006 verified members; retained content: 502 files.
- CLI: `smallsort-brief 6019f7c5-1c0a-44a8-87be-3513797fe416 --catalogue`, `--search LITERAL`, `--file ID --pointer /key` (JSON), or `--file ID --start 1` (text). Requires the v0.8 client installed on the caller host.
- Reader: `/builds/6019f7c5-1c0a-44a8-87be-3513797fe416/catalogue?q=literal`, `/search?q=literal`, `/fragment?file_id=ID&start=1` (text) or `&pointer=/key` (JSON). Use the same /builds/UUID prefix for all routes. Search is over sanitized retained data only; inspect coverage and next_offset. No raw fallback or proof inference.

## Failure diagnostics (verified archived sources)

- Diagnostic status: **OBSERVED**; causality: **UNKNOWN**
- COMPILER_ERROR: $HOME differs from euid-obtained home directory: you may be using sudo
  - Source: `full-stderr.log` line 3; SHA-256 `1421ef97c119a9ee9833afe3bb5a77e9a23a5731747d0291a3ae891cf5a453ff`
- COMPILER_ERROR: $HOME directory: /builder/home
  - Source: `full-stderr.log` line 4; SHA-256 `1421ef97c119a9ee9833afe3bb5a77e9a23a5731747d0291a3ae891cf5a453ff`
- COMPILER_ERROR: euid-obtained home directory: /root
  - Source: `full-stderr.log` line 5; SHA-256 `1421ef97c119a9ee9833afe3bb5a77e9a23a5731747d0291a3ae891cf5a453ff`

## Bounded diagnostic context (untrusted observations)

- AVAILABLE; parser=SUPPORTED_OBSERVATIONS; selection=FIRST_GENERIC_MARKER
  - Source: `full-stderr.log` line UNKNOWN; SHA-256 `1421ef97c119a9ee9833afe3bb5a77e9a23a5731747d0291a3ae891cf5a453ff`
> L1: debconf: delaying package configuration, since apt-utils is not installed
> L2: debconf: delaying package configuration, since apt-utils is not installed
> L3: error: $HOME differs from euid-obtained home directory: you may be using sudo
> L4: error: $HOME directory: /builder/home
> L5: error: euid-obtained home directory: /root
> L6: info: profile set to 'minimal'
> L7: info: default host triple is x86_64-unknown-linux-gnu
> L8: info: skipping toolchain installation
  - Scanned 1110/1110 bytes; scan limit reached=False; lines shown=8/12.
- AVAILABLE; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=FIRST_GENERIC_MARKER
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/full_body/cases/actual_three_current_full_posts/verifast.log` line UNKNOWN; SHA-256 `56aeb6bad1a33679394cddaca0af62e7e0655f9922a905916a7383045789acb6`
> L1407: 0.400548s: verified/lib.rs(313,640-641): Executing statement
> L1408: 0.400655s: verified/lib.rs(313,640-641): Verifying call
> L1409: 0.401251s: verified/lib.rs(313,659-674): Executing statement
> L1410: verified/lib.rs(313,659-674): error: Only predicate assertions and field-points-to assertions are supported here at this time.
> L1411: [WITHHELD: OVERSIZED_LINE]
> L1412: [WITHHELD: OVERSIZED_LINE]
  - Scanned 99280/99280 bytes; scan limit reached=False; lines shown=6/6.
- Up to 2 short windows shown; complete bounded context and availability counts are in evidence-index.json. Context does not establish causality.

## Tool build milestones (individual observed records)

- `translator-build`: EXIT_ZERO; exit=`0`; records=1; omitted=0
  - Source: `allprooflogs/tracked-md-build/translator-build-exit-code.txt` line UNKNOWN; SHA-256 `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`
- `console-build`: EXIT_ZERO; exit=`0`; records=2; omitted=0
  - Source: `allprooflogs/build/console-build-exit-code.txt` line UNKNOWN; SHA-256 `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`
- `exporter-build`: EXIT_ZERO; exit=`0`; records=1; omitted=0
  - Source: `allprooflogs/tracked-md-build/exporter-build-exit-code.txt` line UNKNOWN; SHA-256 `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`
- `decoder-build`: EXIT_ZERO; exit=`0`; records=1; omitted=0
  - Source: `allprooflogs/tracked-md-build/decoder-build-exit-code.txt` line UNKNOWN; SHA-256 `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`
- `refiner-build`: EXIT_ZERO; exit=`0`; records=1; omitted=0
  - Source: `allprooflogs/tracked-md-build/refiner-build-exit-code.txt` line UNKNOWN; SHA-256 `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`
- `tracked-md-compile`: EXIT_ZERO; exit=`0`; records=1; omitted=0
  - Source: `allprooflogs/tracked-md-compile-exit-code.txt` line UNKNOWN; SHA-256 `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`
- `tracked-md-preparation`: EXIT_ZERO; exit=`0`; records=1; omitted=0
  - Source: `allprooflogs/tracked-md-preparation-exit-code.txt` line UNKNOWN; SHA-256 `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`

## First comparator source results

- Coverage: SOURCE_RECORDS_PROJECTED; projected=32; omitted=3; scan_truncated=False; showing up to 6 records
- Source claim `/actual_insert_tail_b2`: {'classification': 'DIAGNOSTIC_ONLY_UNTIL_ALL_GATES_MATCH', 'prefix_current_normal_unwind_proved': False, 'b2_achieved': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `ccf219a562208dfaac3b02c5a89146a79e7993ab121dc70ee28cc5204b7aa744`
- Source claim `/actual_insert_tail_b2/results/full_body`: {'classification': 'INCONCLUSIVE', 'prefix': False, 'current_false_true_panic_proved': False, 'intended_negative': False, 'full_insert_tail_proved': False, 'b2_achieved': False, 'proof_credit': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `ccf219a562208dfaac3b02c5a89146a79e7993ab121dc70ee28cc5204b7aa744`
- Source claim `/actual_insert_tail_b2/results/prefix`: {'classification': 'INCONCLUSIVE', 'prefix': True, 'current_false_true_panic_proved': False, 'intended_negative': False, 'full_insert_tail_proved': False, 'b2_achieved': False, 'proof_credit': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `ccf219a562208dfaac3b02c5a89146a79e7993ab121dc70ee28cc5204b7aa744`
- Source claim `/actual_insert_tail_b2/results/admission_controls`: {'classification': 'NOT_RUN_PREFIX_PREREQUISITE_FAILED', 'proof_credit': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `ccf219a562208dfaac3b02c5a89146a79e7993ab121dc70ee28cc5204b7aa744`
- Source claim `/actual_insert_tail_b2/results/guard_array_controls`: {'classification': 'DIAGNOSTIC_CONTROLS_CLASSIFIED', 'proof_credit': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `ccf219a562208dfaac3b02c5a89146a79e7993ab121dc70ee28cc5204b7aa744`
- Source claim `/actual_insert_tail_b2/results/late_scope_admission_controls`: {'classification': 'ALL_INTENDED_ADMISSION_REJECTIONS', 'proof_credit': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `ccf219a562208dfaac3b02c5a89146a79e7993ab121dc70ee28cc5204b7aa744`
- A joint false/true/panic claim does not provide separate per-branch receipts; absent records do not establish NOT_RUN.

## Stage observations (exit codes are not proof verdicts)

- Record counts: EXIT_NONZERO=87, EXIT_ZERO=425; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- `verifast`: exit=`1`; linkage=`PAIRED_FILENAME_ONLY`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/full_body/cases/actual_three_current_full_posts/verifast-exit-code.txt` line UNKNOWN; SHA-256 `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 1}
- `verifast`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/full_body/cases/actual_three_current_full_posts/verifast-stage.json` line UNKNOWN; SHA-256 `487eb280c2bbf8f68b84a5f1df4cd568adb99d2bf73891ba132a8384c20848b5`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 1}
- `verifast`: exit=`1`; linkage=`PAIRED_FILENAME_ONLY`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/guard-array-controls/missing_physical_quarter/verifast-exit-code.txt` line UNKNOWN; SHA-256 `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 2}
- `verifast`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/guard-array-controls/missing_physical_quarter/verifast-stage.json` line UNKNOWN; SHA-256 `57fa8e3c22ebb689e8fcba0fe70d6835a5543697faa701ef08c43206161daf1e`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 2}
- Expected-control nonzero records (source-classified): 32; details in evidence-index.json.
- Exit 0 observed: `console-build`, `console-build`, `decoder-build`, `exporter-build`, `refiner-build`, `translator-build`; references in evidence-index.json.
- Coverage: {'candidate_records': 532, 'parsed_records': 512, 'not_captured': 20, 'invalid_records': 0, 'omitted_records': 0}; showing up to 4 nonzero and 6 zero records.
- Source assertions: {'proof_attempted': True, 'compiler_classification': 'PASS'}
  - Source: `proof-audit.json` line UNKNOWN; SHA-256 `e77d5816014cfe8d67aa1dc799b74a28e24974b46cccbfd5b9b13928658bb29e`
- Missing/ambiguous diagnostics: VERIFIED_FAILED_LOG_WITHOUT_RECOGNIZED_COMPILER_DIAGNOSTIC, STAGE_COVERAGE_INCOMPLETE_SEE_INDEX, MULTIPLE_STAGE_FAILURES_CAUSALITY_UNKNOWN

## Campaign aggregates (source claims)

- `allprooflogs/cases/selected-drop-minimal/aggregate.json`: classification=INCONCLUSIVE; accepted=False; cases: {'EXPECTED_CONTROL': 6, 'SOURCE_CLASSIFIED': 1} (total=7)
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `ccf219a562208dfaac3b02c5a89146a79e7993ab121dc70ee28cc5204b7aa744`
- `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/aggregate.json`: classification=DIAGNOSTIC_ONLY_UNTIL_ALL_GATES_MATCH; accepted=False; results: {'INCONCLUSIVE': 2, 'NOT_RUN': 5, 'SOURCE_CLASSIFIED': 3} (total=10)
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/aggregate.json` line UNKNOWN; SHA-256 `984a9bd6161cb9dfb831fab49381fe3032d2bbe84f3790247901986a0a0c73d7`
- `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/guard-array-controls/aggregate.json`: classification=DIAGNOSTIC_CONTROLS_CLASSIFIED; accepted=False; proof_credit=False; cases: {'EXPECTED_CONTROL': 3, 'SOURCE_CLASSIFIED': 1} (total=4)
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/guard-array-controls/aggregate.json` line UNKNOWN; SHA-256 `b5d1429026f040dd4b5a7a7a3781deaf48f2396aaf925cc00aaadc03dcb16d43`
- `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/late-scope-admission-controls/aggregate.json`: classification=ALL_INTENDED_ADMISSION_REJECTIONS; accepted=False; proof_credit=False; cases: {'EXPECTED_CONTROL': 2} (total=2)
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/late-scope-admission-controls/aggregate.json` line UNKNOWN; SHA-256 `b25fc6f5f202704aa7b275fefc83d3ad55cc78e25354aae7180d9c19dde543fc`
- Aggregate coverage: {'aggregate_candidates': 12, 'aggregates_captured': 12, 'stage_metadata_captured': 96, 'stage_summaries_retained': 512, 'context_logs_streamed': 8, 'diagnostic_logs_captured': 16, 'diagnostic_log_bytes': 322408, 'oversized_logs': 0, 'budget_omitted_logs': 273, 'aggregates_not_captured': 0}; showing up to 4.

[Additional detail omitted; consult evidence-index.json.]

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
