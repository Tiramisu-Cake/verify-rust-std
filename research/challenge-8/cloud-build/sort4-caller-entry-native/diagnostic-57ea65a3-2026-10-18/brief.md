# SmallSort Evidence Brief — 57ea65a3

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit code (source claim): `0`
- Evidence complete (source claim): `True`
- Archive SHA-256: `02901f734338f175…` (verified archived bytes)
- Inventory files: 356 SHA-256 verified; metadata exceptions: 2 cross-checked
- Text-index entries: 272; chunks: 272 (remote chunk bytes not checked)


## Failure diagnostics (verified archived sources)

- Diagnostic status: **CORROBORATED**; causality: **CORROBORATED_SOURCE_REPORT**
- Runner-reported causal stage: `tool-reconstruction` (source assertion)
- Runner-reported blocker: `tool-reconstruction` / `adapter_error`
- Runner-reported detail (not independently causal): RuntimeError: A1-TOOL: R-only native reference build
- Audit provenance: `proof-audit.json` SHA-256 `88a0e0838b3eb6172156be9d9ab8057e90ec3b99ea85b55b8573d1dc2c56d068`
- Stage receipt: `a1-R-only-native-reference-build` state=`TERMINAL` exit=`2` timeout budget=`541`
- Stage provenance: `allprooflogs/cases/sort4-c1-current-recovery/a1-tool/a1-R-only-native-reference-build-stage.json` SHA-256 `ddc330bc8f67e0aa0a068ced23a8a8d2e3e201df9293a100b9858712dc80d563`
- RUST_UNUSED_MUT: Rust unused_mut: variable does not need to be mutable at `src/lib.rs:843:17`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-tool/a1-R-only-native-reference-build.log` line 68; SHA-256 `fce1d5e4658d815703b38bb15a7517818224d25ce3515480b9c4f138bdcef4ee`
- RUST_UNUSED_MUT: Rust unused_mut: variable does not need to be mutable at `src/lib.rs:906:60`
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-tool/a1-R-only-native-reference-build.log` line 83; SHA-256 `fce1d5e4658d815703b38bb15a7517818224d25ce3515480b9c4f138bdcef4ee`
- COMPILER_ERROR: could not compile ?vf_mir_exporter? (lib) due to 2 previous errors
  - Source: `allprooflogs/cases/sort4-c1-current-recovery/a1-tool/a1-R-only-native-reference-build.log` line 91; SHA-256 `fce1d5e4658d815703b38bb15a7517818224d25ce3515480b9c4f138bdcef4ee`
- Runner-reported cases: 26; NOT_RUN=26

## Campaign aggregates (source claims)

- No campaign aggregate found in archived evidence

## Representative cases (source verdicts, not inferred proof)

### `allprooflogs/cases/sort4-c1-current-recovery`

## Boundaries

- Raw verifier errors are observations, not independently proven causal blockers.
- Original classifying records are *reported* verdicts for this exact build/profile; no PASS is inferred from exit code 0.
- Archived bytes and file inventory were checked; remote text-log chunks were indexed but not downloaded/hashed individually.
- This processor does not run a verifier, change proof acceptance, or review the agent session.
