# SmallSort Evidence Brief — f580a235

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit (source claim): `1`; evidence complete: `True`

## Further bounded evidence

- Complete catalogue: 1899 verified members; retained content: 490 files.
- CLI: `smallsort-brief f580a235-3a7c-47e4-8567-568d0b73579c --catalogue`, `--search LITERAL`, `--file ID --pointer /key` (JSON), or `--file ID --start 1` (text). Requires the v0.8 client installed on the caller host.
- Reader: `/builds/f580a235-3a7c-47e4-8567-568d0b73579c/catalogue?q=literal`, `/search?q=literal`, `/fragment?file_id=ID&start=1` (text) or `&pointer=/key` (JSON). Use the same /builds/UUID prefix for all routes. Search is over sanitized retained data only; inspect coverage and next_offset. No raw fallback or proof inference.

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
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/full_body/cases/actual_three_current_full_posts/verifast.log` line UNKNOWN; SHA-256 `5d468361bdc63e1e42eac47fa7b30488aa761f28ac5dbc9be41fba0e976d4b97`
> L93: 
> L94: 
> L95: 
> L96: Fatal error: exception Not_found
> L97: Raised at Stdlib__List.find in file "list.ml", line 224, characters 10-25
> L98: Called from Vf_mir_translator.Make.TrBody.translate_fn_call.(fun) in file "?REDACTED_LONG_VALUE?.ml", line 3229, characters 14-266
> L99: Called from Rocq_writer.rocq_indent in file "frontend/rocq_writer.ml", line 75, characters 15-22
> L100: Called from Rocq_writer.rocq_print_big_record.(fun) in file "frontend/rocq_writer.ml", line 147, characters 15-38
  - Scanned 6438/6438 bytes; scan limit reached=False; lines shown=8/12.
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
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `0bd63c33f1e766a14b83e06b1c272be154e4cf97e2bacd2483fdd3ed786afb21`
- Source claim `/actual_insert_tail_b2/results/full_body`: {'classification': 'INCONCLUSIVE', 'prefix': False, 'current_false_true_panic_proved': False, 'intended_negative': False, 'full_insert_tail_proved': False, 'b2_achieved': False, 'proof_credit': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `0bd63c33f1e766a14b83e06b1c272be154e4cf97e2bacd2483fdd3ed786afb21`
- Source claim `/actual_insert_tail_b2/results/prefix`: {'classification': 'INCONCLUSIVE', 'prefix': True, 'current_false_true_panic_proved': False, 'intended_negative': False, 'full_insert_tail_proved': False, 'b2_achieved': False, 'proof_credit': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `0bd63c33f1e766a14b83e06b1c272be154e4cf97e2bacd2483fdd3ed786afb21`
- Source claim `/actual_insert_tail_b2/results/admission_controls`: {'classification': 'NOT_RUN_PREFIX_PREREQUISITE_FAILED', 'proof_credit': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `0bd63c33f1e766a14b83e06b1c272be154e4cf97e2bacd2483fdd3ed786afb21`
- Source claim `/actual_insert_tail_b2/results/guard_array_controls`: {'classification': 'INCONCLUSIVE', 'proof_credit': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `0bd63c33f1e766a14b83e06b1c272be154e4cf97e2bacd2483fdd3ed786afb21`
- Source claim `/actual_insert_tail_b2/results/late_scope_admission_controls`: {'classification': 'INCONCLUSIVE', 'proof_credit': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `0bd63c33f1e766a14b83e06b1c272be154e4cf97e2bacd2483fdd3ed786afb21`
- A joint false/true/panic claim does not provide separate per-branch receipts; absent records do not establish NOT_RUN.

## Stage observations (exit codes are not proof verdicts)

- Record counts: EXIT_NONZERO=83, EXIT_ZERO=425; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- `verifast`: exit=`2`; linkage=`PAIRED_FILENAME_ONLY`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/full_body/cases/actual_three_current_full_posts/verifast-exit-code.txt` line UNKNOWN; SHA-256 `53c234e5e8472b6ac51c1ae1cab3fe06fad053beb8ebfd8977b010655bfdd3c3`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 1}
- `verifast`: exit=`2`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/full_body/cases/actual_three_current_full_posts/verifast-stage.json` line UNKNOWN; SHA-256 `21c36fad80a9ff9b32efce9b90c7d88a7c7fb1ca94a30b4e805588153168c862`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 1}
- `verifast`: exit=`1`; linkage=`PAIRED_FILENAME_ONLY`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/guard-array-controls/missing_physical_quarter/verifast-exit-code.txt` line UNKNOWN; SHA-256 `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 2}
- `verifast`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/guard-array-controls/missing_physical_quarter/verifast-stage.json` line UNKNOWN; SHA-256 `1ae165c2eab99fe6b37f4aaa4a7953ab0bc75e4a0d70324fe405cd137552d329`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 2}
- Expected-control nonzero records (source-classified): 32; details in evidence-index.json.
- Exit 0 observed: `console-build`, `console-build`, `decoder-build`, `exporter-build`, `refiner-build`, `translator-build`; references in evidence-index.json.
- Coverage: {'candidate_records': 508, 'parsed_records': 508, 'not_captured': 0, 'invalid_records': 0, 'omitted_records': 0}; showing up to 4 nonzero and 6 zero records.
- Source assertions: {'proof_attempted': True, 'compiler_classification': 'PASS'}
  - Source: `proof-audit.json` line UNKNOWN; SHA-256 `63ccd4ef6eec80750d0a65919d3d22c82136f048841776cd7f5da5134ea71e46`
- Missing/ambiguous diagnostics: VERIFIED_FAILED_LOG_WITHOUT_RECOGNIZED_COMPILER_DIAGNOSTIC, MULTIPLE_STAGE_FAILURES_CAUSALITY_UNKNOWN

## Campaign aggregates (source claims)

- `allprooflogs/cases/selected-drop-minimal/aggregate.json`: classification=INCONCLUSIVE; accepted=False; cases: {'EXPECTED_CONTROL': 6, 'SOURCE_CLASSIFIED': 1} (total=7)
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `0bd63c33f1e766a14b83e06b1c272be154e4cf97e2bacd2483fdd3ed786afb21`
- `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/aggregate.json`: classification=DIAGNOSTIC_ONLY_UNTIL_ALL_GATES_MATCH; accepted=False; results: {'INCONCLUSIVE': 4, 'NOT_RUN': 5, 'SOURCE_CLASSIFIED': 1} (total=10)
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/aggregate.json` line UNKNOWN; SHA-256 `79e48f0008462bbaab78596971e490f1896ee513ba6bb5d879c300f4dca851e1`
- `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/guard-array-controls/aggregate.json`: classification=INCONCLUSIVE; accepted=False; proof_credit=False; cases: {'EXPECTED_CONTROL': 2, 'INCONCLUSIVE': 1, 'SOURCE_CLASSIFIED': 1} (total=4)
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/guard-array-controls/aggregate.json` line UNKNOWN; SHA-256 `aef4699fb770e712ae510cde5ac9ea1c057c70ffd8815030f3392f69036de5a4`
- `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/late-scope-admission-controls/aggregate.json`: classification=INCONCLUSIVE; accepted=False; proof_credit=False; cases: {'NOT_RUN': 2} (total=2)
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/late-scope-admission-controls/aggregate.json` line UNKNOWN; SHA-256 `2fd9dbca9c919a0ec67463a45c721e7b2db84dd383bc35d35127c2f924da6125`
- Aggregate coverage: {'aggregate_candidates': 12, 'aggregates_captured': 12, 'stage_metadata_captured': 96, 'stage_summaries_retained': 508, 'context_logs_streamed': 8, 'diagnostic_logs_captured': 16, 'diagnostic_log_bytes': 227555, 'oversized_logs': 0, 'budget_omitted_logs': 261, 'aggregates_not_captured': 0}; showing up to 4.

[Additional detail omitted; consult evidence-index.json.]

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
