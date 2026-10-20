# SmallSort Evidence Brief — e8d17588

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit (source claim): `1`; evidence complete: `True`

## Further bounded evidence

- Complete catalogue: 1898 verified members; retained content: 489 files.
- CLI: `smallsort-brief e8d17588-c7c6-439d-aa39-7703ce8a275c --catalogue`, `--search LITERAL`, `--file ID --pointer /key` (JSON), or `--file ID --start 1` (text). Requires the v0.8 client installed on the caller host.
- Reader: `/builds/e8d17588-c7c6-439d-aa39-7703ce8a275c/catalogue?q=literal`, `/search?q=literal`, `/fragment?file_id=ID&start=1` (text) or `&pointer=/key` (JSON). Use the same /builds/UUID prefix for all routes. Search is over sanitized retained data only; inspect coverage and next_offset. No raw fallback or proof inference.

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
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/full_body/cases/actual_three_current_full_posts/verifast.log` line UNKNOWN; SHA-256 `11d047d814ccf32c2d045c24d585f2e2803f3692a3bd28963d57b2d8c4d95867`
> L1350: 0.438634s: ?REDACTED_LONG_VALUE?.rsspec(121,6-13): Producing auto-closed chunk
> L1351: 0.438640s: verified/lib.rs(89,14-15): Consuming chunk (retry)
> L1352: 0.438721s: verified/lib.rs(93,48-50): Consuming expression
> L1353: verified/lib.rs(93,48-50): error: Cannot prove condition. (Cannot prove %(get_pointer_address(get_CopyOnDrop_src(mk_CopyOnDrop(fn_outcome_result(outcome5), ptr_add_(tail0, (0 - 1), uint64_t_typeid), 1))), alignof(uint64_t_typeid)) = 0.)
> L1354: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
> L1355: ? ^^
  - Scanned 118084/118084 bytes; scan limit reached=False; lines shown=6/12.
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

- Coverage: SOURCE_RECORDS_PROJECTED; projected=32; omitted=0; scan_truncated=False; showing up to 6 records
- Source claim `/actual_insert_tail_b2`: {'classification': 'DIAGNOSTIC_ONLY_UNTIL_ALL_GATES_MATCH', 'prefix_current_normal_unwind_proved': False, 'b2_achieved': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `5ebe2a39ef2820845b8bc58e7d88d59506db83e0e514a97f9ea8604c12886732`
- Source claim `/actual_insert_tail_b2/results/full_body`: {'classification': 'INCONCLUSIVE', 'prefix': False, 'current_false_true_panic_proved': False, 'intended_negative': False, 'full_insert_tail_proved': False, 'b2_achieved': False, 'proof_credit': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `5ebe2a39ef2820845b8bc58e7d88d59506db83e0e514a97f9ea8604c12886732`
- Source claim `/actual_insert_tail_b2/results/prefix`: {'classification': 'INCONCLUSIVE', 'prefix': True, 'current_false_true_panic_proved': False, 'intended_negative': False, 'full_insert_tail_proved': False, 'b2_achieved': False, 'proof_credit': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `5ebe2a39ef2820845b8bc58e7d88d59506db83e0e514a97f9ea8604c12886732`
- Source claim `/actual_insert_tail_b2/results/admission_controls`: {'classification': 'NOT_RUN_PREFIX_PREREQUISITE_FAILED', 'proof_credit': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `5ebe2a39ef2820845b8bc58e7d88d59506db83e0e514a97f9ea8604c12886732`
- Source claim `/actual_insert_tail_b2/results/guard_array_controls`: {'classification': 'INCONCLUSIVE', 'proof_credit': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `5ebe2a39ef2820845b8bc58e7d88d59506db83e0e514a97f9ea8604c12886732`
- Source claim `/actual_insert_tail_b2/results/lost_cell_owner`: {'classification': 'NOT_RUN_PREFIX_PREREQUISITE_FAILED', 'intended_negative': False, 'proof_credit': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `5ebe2a39ef2820845b8bc58e7d88d59506db83e0e514a97f9ea8604c12886732`
- A joint false/true/panic claim does not provide separate per-branch receipts; absent records do not establish NOT_RUN.

## Stage observations (exit codes are not proof verdicts)

- Record counts: EXIT_NONZERO=85, EXIT_ZERO=423; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- `verifast`: exit=`1`; linkage=`PAIRED_FILENAME_ONLY`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/full_body/cases/actual_three_current_full_posts/verifast-exit-code.txt` line UNKNOWN; SHA-256 `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 1}
- `verifast`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/full_body/cases/actual_three_current_full_posts/verifast-stage.json` line UNKNOWN; SHA-256 `5f25546b1af0c084ae3ab21f1423cd1d863932edb17966f9bf121377fd461716`
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
  - Source: `proof-audit.json` line UNKNOWN; SHA-256 `f38975cbafd812a7475e2c933ebf7d1fae3846e23c7a55b39c4bb451fbb2717d`
- Missing/ambiguous diagnostics: VERIFIED_FAILED_LOG_WITHOUT_RECOGNIZED_COMPILER_DIAGNOSTIC, MULTIPLE_STAGE_FAILURES_CAUSALITY_UNKNOWN

## Campaign aggregates (source claims)

- `allprooflogs/cases/selected-drop-minimal/aggregate.json`: classification=INCONCLUSIVE; accepted=False; cases: {'EXPECTED_CONTROL': 6, 'SOURCE_CLASSIFIED': 1} (total=7)
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `5ebe2a39ef2820845b8bc58e7d88d59506db83e0e514a97f9ea8604c12886732`
- `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/aggregate.json`: classification=DIAGNOSTIC_ONLY_UNTIL_ALL_GATES_MATCH; accepted=False; results: {'INCONCLUSIVE': 3, 'NOT_RUN': 5, 'SOURCE_CLASSIFIED': 1} (total=9)
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/aggregate.json` line UNKNOWN; SHA-256 `673fdaa1da774e41719b02d95c9698196777d4cdb49238794ece7b21cba6585a`
- `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/guard-array-controls/aggregate.json`: classification=INCONCLUSIVE; accepted=False; proof_credit=False; cases: {'INCONCLUSIVE': 4} (total=4)
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/guard-array-controls/aggregate.json` line UNKNOWN; SHA-256 `b5a82b249d5515857392b32acef1870324eefcfb4555d9cd0e0eefde5106f9ed`
- `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/share-representation-controls/aggregate.json`: classification=DIAGNOSTIC_CONTROLS_CLASSIFIED; accepted=False; proof_credit=False; cases: {'EXPECTED_CONTROL': 4, 'SOURCE_CLASSIFIED': 1} (total=5)
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/share-representation-controls/aggregate.json` line UNKNOWN; SHA-256 `51b75c627c1d524b78473521a68ec97a8ca6fe5787c3c426cd8e1146fbb63f8d`

## Representative cases (source verdicts)

- `allprooflogs/checked-minimal-bridge/combined-profile-smoke/cases/ordinary_call_normal_unwind`; classification.json: classification=PASS
- Cases: 21; showing up to 4. More references and source claims in evidence-index.json.

[Additional detail omitted; consult evidence-index.json.]

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
