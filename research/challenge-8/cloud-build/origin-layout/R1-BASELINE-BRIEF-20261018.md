# SmallSort Evidence Brief — e3252f3a

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
- EMPTY_LOG; parser=NO_SUPPORTED_PARSER_CLASSIFICATION; selection=TAIL_OF_SCANNED_PREFIX_NO_MARKER
  - Source: `allprooflogs/checked-minimal-bridge/onecell-selected-drop/admission-controls/missing_caller_generated_reference/sources/official-refinement.log` line UNKNOWN; SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
  - Scanned 0/0 bytes; scan limit reached=False; lines shown=0/0.
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

- Coverage: NO_SUPPORTED_SOURCE_RECORD_OR_NAMED_ARTIFACT; projected=0; omitted=0; scan_truncated=False; showing up to 6 records
- A joint false/true/panic claim does not provide separate per-branch receipts; absent records do not establish NOT_RUN.

## Stage observations (exit codes are not proof verdicts)

- Record counts: EXIT_NONZERO=47, EXIT_ZERO=203; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- `official-refinement`: exit=`1`; linkage=`PAIRED_FILENAME_ONLY`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/onecell-selected-drop/admission-controls/missing_caller_generated_reference/sources/official-refinement-exit-code.txt` line UNKNOWN; SHA-256 `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865`
  - Context availability: {'status': 'EMPTY_LOG', 'context_id': 1}
- `official-refinement`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/onecell-selected-drop/admission-controls/missing_caller_generated_reference/sources/official-refinement-stage.json` line UNKNOWN; SHA-256 `e47443e9dc4fa1fa948d7dcaed5aa500ce2f0a8c58c620cd0616c4da5447af35`
  - Context availability: {'status': 'EMPTY_LOG', 'context_id': 1}
- `official-refinement`: exit=`1`; linkage=`PAIRED_FILENAME_ONLY`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/onecell-selected-drop/admission-controls/missing_generated_enabled/sources/official-refinement-exit-code.txt` line UNKNOWN; SHA-256 `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865`
  - Context availability: {'status': 'EMPTY_LOG', 'context_id': 2}
- `official-refinement`: exit=`1`; linkage=`RECEIPT`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/onecell-selected-drop/admission-controls/missing_generated_enabled/sources/official-refinement-stage.json` line UNKNOWN; SHA-256 `4215d313e832c82293eaddd13bdb6dc553ced4011d3fbfe65bb191bfe8d07d69`
  - Context availability: {'status': 'EMPTY_LOG', 'context_id': 2}
- Expected-control nonzero records (source-classified): 26; details in evidence-index.json.
- Exit 0 observed: `console-build`, `console-build`, `decoder-build`, `exporter-build`, `refiner-build`, `translator-build`; references in evidence-index.json.
- Coverage: {'candidate_records': 250, 'parsed_records': 250, 'not_captured': 0, 'invalid_records': 0, 'omitted_records': 0}; showing up to 4 nonzero and 6 zero records.
- Source assertions: {'proof_attempted': True, 'compiler_classification': 'PASS'}
  - Source: `proof-audit.json` line UNKNOWN; SHA-256 `367bc27fc664d5c007d04dd7dc49e878e64e90b1ee2145b94f6cb2caeeec353b`
- Missing/ambiguous diagnostics: VERIFIED_FAILED_LOG_WITHOUT_RECOGNIZED_COMPILER_DIAGNOSTIC, MULTIPLE_STAGE_FAILURES_CAUSALITY_UNKNOWN

## Campaign aggregates (source claims)

- `allprooflogs/cases/selected-drop-minimal/aggregate.json`: classification=INCONCLUSIVE; accepted=False; cases: {'EXPECTED_CONTROL': 6, 'SOURCE_CLASSIFIED': 1} (total=7)
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `b9b2bd403292a45a4ec5f703c8896477a01fc05562d385e76475926ffe9ee28c`
- `allprooflogs/checked-minimal-bridge/aggregate.json`: classification=INCONCLUSIVE; accepted=False; cases: {'EXPECTED_CONTROL': 6, 'SOURCE_CLASSIFIED': 1} (total=7)
  - Source: `allprooflogs/checked-minimal-bridge/aggregate.json` line UNKNOWN; SHA-256 `06f570ca28ac2a55a878393b5f07bebb775e55fb1dd357c0c2bc434f386e3a3f`
- `allprooflogs/checked-minimal-bridge/combined-profile-smoke/aggregate.json`: verdict UNKNOWN; cases: {'PASS': 1} (total=1)
  - Source: `allprooflogs/checked-minimal-bridge/combined-profile-smoke/aggregate.json` line UNKNOWN; SHA-256 `c65a1ccef15479ba92d1f9a9439f2657b2cc343656e36921285a065d630ec078`
- `allprooflogs/checked-minimal-bridge/helper-control/aggregate.json`: accepted=False; cases: {'EXPECTED_CONTROL': 3, 'SOURCE_CLASSIFIED': 1} (total=4)
  - Source: `allprooflogs/checked-minimal-bridge/helper-control/aggregate.json` line UNKNOWN; SHA-256 `832c86c816cadc70f3b1385fb7914f15658a333e5813da05d5c119a3e1372f57`
- Aggregate coverage: {'aggregate_candidates': 7, 'aggregates_captured': 7, 'stage_metadata_captured': 96, 'stage_summaries_retained': 250, 'context_logs_streamed': 8, 'diagnostic_logs_captured': 16, 'diagnostic_log_bytes': 406577, 'oversized_logs': 0, 'budget_omitted_logs': 132, 'aggregates_not_captured': 0}; showing up to 4.

## Representative cases (source verdicts)

- `allprooflogs/checked-minimal-bridge/combined-profile-smoke/cases/ordinary_call_normal_unwind`; classification.json: classification=PASS
- `allprooflogs/checked-minimal-bridge/helper-control/cases/positive`; classification.json: classification=BOUNDED_NORMAL_COMPOSITION_PASS_FRAGMENT_ONLY; accepted=False
- `allprooflogs/checked-minimal-bridge/onecell-selected-drop/cases/positive`; classification.json: classification=NATURAL_DROP_CALLER_AND_EFFECT_PASS_FRAGMENT_ONLY; accepted=False
- `allprooflogs/checked-profile-smoke/cases/ordinary_call_normal_unwind`; classification.json: classification=PASS
- Cases: 17; showing up to 4. More references and source claims in evidence-index.json.

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
