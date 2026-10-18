# SmallSort Evidence Brief — e3252f3a

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit (source claim): `1`; evidence complete: `True`

## Failure diagnostics (verified archived sources)

- Diagnostic status: **OBSERVED**; causality: **UNKNOWN**

## Stage observations (exit codes are not proof verdicts)

- Record counts: EXIT_NONZERO=24, UNKNOWN=72; order=NOT_ESTABLISHED; last completed stage=UNKNOWN
- `verifast`: exit=`1`; linkage=`PAIRED_FILENAME_ONLY`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/helper-control/cases/after_call_current_false/verifast-exit-code.txt` line UNKNOWN; SHA-256 `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865`
- `verifast`: exit=`1`; linkage=`PAIRED_FILENAME_ONLY`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/helper-control/cases/caller_entry_false/verifast-exit-code.txt` line UNKNOWN; SHA-256 `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865`
- `verifast`: exit=`1`; linkage=`PAIRED_FILENAME_ONLY`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/helper-control/cases/receiver_origin_probe/verifast-exit-code.txt` line UNKNOWN; SHA-256 `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865`
- `official-refinement`: exit=`1`; linkage=`PAIRED_FILENAME_ONLY`; diagnostic=`NO_SUPPORTED_DIAGNOSTIC`
  - Source: `allprooflogs/checked-minimal-bridge/onecell-selected-drop/admission-controls/missing_caller_generated_reference/sources/official-refinement-exit-code.txt` line UNKNOWN; SHA-256 `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865`
- Coverage: {'candidate_records': 250, 'parsed_records': 96, 'not_captured': 154, 'invalid_records': 0, 'omitted_records': 32}; showing up to 4 nonzero and 6 zero records.
- Source assertions: {'proof_attempted': True, 'compiler_classification': 'PASS'}
  - Source: `proof-audit.json` line UNKNOWN; SHA-256 `367bc27fc664d5c007d04dd7dc49e878e64e90b1ee2145b94f6cb2caeeec353b`
- Missing/ambiguous diagnostics: FULL_STDERR_TOO_LARGE_OR_UNAVAILABLE, VERIFIED_FAILED_LOG_WITHOUT_RECOGNIZED_COMPILER_DIAGNOSTIC, STAGE_COVERAGE_INCOMPLETE_SEE_INDEX, MULTIPLE_STAGE_FAILURES_CAUSALITY_UNKNOWN

## Campaign aggregates (source claims)

- `allprooflogs/cases/selected-drop-minimal/aggregate.json`: classification=INCONCLUSIVE; accepted=False; cases: {'UNKNOWN': 7} (total=7)
  - Source: `allprooflogs/cases/selected-drop-minimal/aggregate.json` line UNKNOWN; SHA-256 `b9b2bd403292a45a4ec5f703c8896477a01fc05562d385e76475926ffe9ee28c`
- `allprooflogs/checked-minimal-bridge/aggregate.json`: classification=INCONCLUSIVE; accepted=False; cases: {'UNKNOWN': 7} (total=7)
  - Source: `allprooflogs/checked-minimal-bridge/aggregate.json` line UNKNOWN; SHA-256 `06f570ca28ac2a55a878393b5f07bebb775e55fb1dd357c0c2bc434f386e3a3f`
- `allprooflogs/checked-minimal-bridge/combined-profile-smoke/aggregate.json`: verdict UNKNOWN; cases: {'PASS': 1} (total=1)
  - Source: `allprooflogs/checked-minimal-bridge/combined-profile-smoke/aggregate.json` line UNKNOWN; SHA-256 `c65a1ccef15479ba92d1f9a9439f2657b2cc343656e36921285a065d630ec078`
- `allprooflogs/checked-minimal-bridge/helper-control/aggregate.json`: accepted=False; cases: {'UNKNOWN': 4} (total=4)
  - Source: `allprooflogs/checked-minimal-bridge/helper-control/aggregate.json` line UNKNOWN; SHA-256 `832c86c816cadc70f3b1385fb7914f15658a333e5813da05d5c119a3e1372f57`
- Aggregate coverage: {'aggregate_candidates': 7, 'aggregates_captured': 7, 'stage_metadata_captured': 96, 'diagnostic_logs_captured': 16, 'diagnostic_log_bytes': 383106, 'oversized_logs': 0, 'budget_omitted_logs': 132, 'aggregates_not_captured': 0}; showing up to 4.

## Representative cases (source verdicts)

- `allprooflogs/checked-minimal-bridge/helper-control/cases/after_call_current_false`; classification.json: classification=EXPECTED_AFTER_CALL_CURRENT_REJECTION; accepted=False; observed error: verified/lib.rs(163,20-25): error: Assertion might not hold. (Cannot prove false.)
- `allprooflogs/checked-minimal-bridge/helper-control/cases/caller_entry_false`; classification.json: classification=EXPECTED_CALLER_ENTRY_REJECTION; accepted=False; observed error: verified/lib.rs(159,20-25): error: Assertion might not hold. (Cannot prove false.)
- `allprooflogs/checked-minimal-bridge/helper-control/cases/receiver_origin_probe`; classification.json: classification=EXPECTED_RECEIVER_ORIGIN_REJECTION; accepted=False; observed error: verified/lib.rs(159,42-44): error: Assertion might not hold. (Cannot prove ref_origin(gap_guard_addr) = gap_guard_addr.)
- `allprooflogs/checked-minimal-bridge/onecell-selected-drop/cases/after_natural_drop_false`; classification.json: classification=EXPECTED_REJECTION; accepted=False; observed error: verified/lib.rs(196,20-25): error: Assertion might not hold. (Cannot prove false.)
- Cases: 17; showing up to 4. More references and source claims in evidence-index.json.

## Boundaries

Source verdicts are claims; no PASS is inferred from exit 0. Stage order and first/last causal stage remain UNKNOWN without explicit evidence. No verifier is run by this processor. Remote text chunk bytes are not checked.
