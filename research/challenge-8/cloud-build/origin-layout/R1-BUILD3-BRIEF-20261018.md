# SmallSort Evidence Brief — e7b74165

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit (source claim): `1`; evidence complete: `True`

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
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/full_body/cases/actual_three_current_full_posts/verifast.log` line UNKNOWN; SHA-256 `f210c13e302b0a05b0a5a03e4beaa9563f1bf54daee72da6af02378d61be96d8`
> L713: 0.233116s: ?REDACTED_LONG_VALUE?.rsspec(178,6-13): Inferring chunk arguments
> L714: 0.233126s: verified/lib.rs(188,432-437): Producing predicate chunk
> L715: 0.233134s: verified/lib.rs(188,487-492): Executing statement
> L716: ?REDACTED_LONG_VALUE?.rsspec(181,32-39): error: No matching heap chunks: foreach?u64?(t3, own0(uint64_t_typeid, t))
> L717: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
> L718: ? ^^^^^^^
> L719: ?REDACTED_LONG_VALUE?.rsspec(181,32-39): note: Consuming assertion
> L720: [WITHHELD: COMMAND_ENVIRONMENT_OR_ROLE_TEXT]
  - Scanned 71101/71101 bytes; scan limit reached=False; lines shown=8/12.
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

- Coverage: SOURCE_RECORDS_PROJECTED; projected=26; omitted=0; scan_truncated=False; showing up to 6 records
- Source claim `/actual_insert_tail_b2`: {'classification': 'DIAGNOSTIC_ONLY_UNTIL_ALL_GATES_MATCH', 'prefix_current_normal_unwind_proved': False, 'b2_achieved': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `cbd5017f604f76c2c49e2e4250987b73687f82f6ec2cd960f01c628103feb117`
- Source claim `/actual_insert_tail_b2/results/full_body`: {'classification': 'INCONCLUSIVE', 'prefix': False, 'current_false_true_panic_proved': False, 'intended_negative': False, 'full_insert_tail_proved': False, 'b2_achieved': False, 'proof_credit': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `cbd5017f604f76c2c49e2e4250987b73687f82f6ec2cd960f01c628103feb117`
- Source claim `/actual_insert_tail_b2/results/prefix`: {'classification': 'INCONCLUSIVE', 'prefix': True, 'current_false_true_panic_proved': False, 'intended_negative': False, 'full_insert_tail_proved': False, 'b2_achieved': False, 'proof_credit': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `cbd5017f604f76c2c49e2e4250987b73687f82f6ec2cd960f01c628103feb117`
- Source claim `/actual_insert_tail_b2/results/admission_controls`: {'classification': 'NOT_RUN_PREFIX_PREREQUISITE_FAILED', 'proof_credit': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `cbd5017f604f76c2c49e2e4250987b73687f82f6ec2cd960f01c628103feb117`
- Source claim `/actual_insert_tail_b2/results/lost_cell_owner`: {'classification': 'NOT_RUN_PREFIX_PREREQUISITE_FAILED', 'intended_negative': False, 'proof_credit': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `cbd5017f604f76c2c49e2e4250987b73687f82f6ec2cd960f01c628103feb117`
- Source claim `/actual_insert_tail_b2/results/lost_current_f`: {'classification': 'NOT_RUN_PREFIX_PREREQUISITE_FAILED', 'intended_negative': False, 'proof_credit': False}
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `cbd5017f604f76c2c49e2e4250987b73687f82f6ec2cd960f01c628103feb117`
- A joint false/true/panic claim does not provide separate per-branch receipts; absent records do not establish NOT_RUN.

## Stage observations (exit codes are not proof verdicts)

- Record counts: EXIT_NONZERO=61, EXIT_ZERO=231; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- `verifast`: exit=`1`; linkage=`PAIRED_FILENAME_ONLY`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/full_body/cases/actual_three_current_full_posts/verifast-exit-code.txt` line UNKNOWN; SHA-256 `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 1}
- `verifast`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/full_body/cases/actual_three_current_full_posts/verifast-stage.json` line UNKNOWN; SHA-256 `3e88d31512e4def8aead3f02f85ae53a02cf99d5002df8c503ad7046e044c3c5`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 1}
- `verifast`: exit=`1`; linkage=`PAIRED_FILENAME_ONLY`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/prefix/cases/actual_three_current_full_posts/verifast-exit-code.txt` line UNKNOWN; SHA-256 `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 2}
- `verifast`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/prefix/cases/actual_three_current_full_posts/verifast-stage.json` line UNKNOWN; SHA-256 `7e18668c030d8382592b16e664ea520292e0e588d00f3b7dfbd3703ad526fe7f`
  - Context availability: {'status': 'AVAILABLE', 'context_id': 2}
- Expected-control nonzero records (source-classified): 26; details in evidence-index.json.
- Exit 0 observed: `console-build`, `console-build`, `decoder-build`, `exporter-build`, `refiner-build`, `translator-build`; references in evidence-index.json.
- Coverage: {'candidate_records': 292, 'parsed_records': 292, 'not_captured': 0, 'invalid_records': 0, 'omitted_records': 0}; showing up to 4 nonzero and 6 zero records.
- Source assertions: {'proof_attempted': True, 'compiler_classification': 'PASS'}
  - Source: `proof-audit.json` line UNKNOWN; SHA-256 `b9dc3d065bbe7bf8b3d8344eb626db6c526e8fd60eb0d5408818819561473521`
- Missing/ambiguous diagnostics: VERIFIED_FAILED_LOG_WITHOUT_RECOGNIZED_COMPILER_DIAGNOSTIC, MULTIPLE_STAGE_FAILURES_CAUSALITY_UNKNOWN

## Campaign aggregates (source claims)

- `allprooflogs/cases/selected-drop-minimal/aggregate.json`: classification=INCONCLUSIVE; accepted=False; cases: {'EXPECTED_CONTROL': 6, 'SOURCE_CLASSIFIED': 1} (total=7)
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `cbd5017f604f76c2c49e2e4250987b73687f82f6ec2cd960f01c628103feb117`
- `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/aggregate.json`: classification=DIAGNOSTIC_ONLY_UNTIL_ALL_GATES_MATCH; accepted=False; results: {'INCONCLUSIVE': 2, 'NOT_RUN': 5} (total=7)
  - Source: `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/aggregate.json` line UNKNOWN; SHA-256 `332074746419b0a8f3aad12536a1aae80f6115cd7c22ed8245bb8d333876830f`
- `allprooflogs/checked-minimal-bridge/aggregate.json`: classification=INCONCLUSIVE_B2_CAUSAL_DIAGNOSTIC; accepted=False; cases: {'EXPECTED_CONTROL': 6, 'SOURCE_CLASSIFIED': 1} (total=7)
  - Source: `allprooflogs/checked-minimal-bridge/aggregate.json` line UNKNOWN; SHA-256 `0dce3028f17182b514cb65978f5f3247c62dd44f2cf5c32cd7d7f647ffb66474`
- `allprooflogs/checked-minimal-bridge/combined-profile-smoke/aggregate.json`: verdict UNKNOWN; cases: {'PASS': 1} (total=1)
  - Source: `allprooflogs/checked-minimal-bridge/combined-profile-smoke/aggregate.json` line UNKNOWN; SHA-256 `c65a1ccef15479ba92d1f9a9439f2657b2cc343656e36921285a065d630ec078`
- Aggregate coverage: {'aggregate_candidates': 8, 'aggregates_captured': 8, 'stage_metadata_captured': 96, 'stage_summaries_retained': 292, 'context_logs_streamed': 8, 'diagnostic_logs_captured': 16, 'diagnostic_log_bytes': 155850, 'oversized_logs': 0, 'budget_omitted_logs': 153, 'aggregates_not_captured': 0}; showing up to 4.

## Representative cases (source verdicts)

- `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/full_body/cases/actual_three_current_full_posts`; classification.json: classification=INCONCLUSIVE; accepted=False; proof_credit=False; observed error: /workspace/merge-work/runner-temp/challenge8-merge-overnight/verifast-tracked-md-source/bin/rust/list.rsspec(181,32-39): error: No matching heap chunks: foreach
- `allprooflogs/checked-minimal-bridge/actual-insert-tail-b2/prefix/cases/actual_three_current_full_posts`; classification.json: classification=INCONCLUSIVE; accepted=False; proof_credit=False; observed error: /workspace/merge-work/runner-temp/challenge8-merge-overnight/verifast-tracked-md-source/bin/rust/list.rsspec(181,32-39): error: No matching heap chunks: foreach

[Additional detail omitted; consult evidence-index.json.]

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
