# SmallSort Evidence Brief — 7c26b389

- Processing: **VERIFIED_ARCHIVE_AND_INVENTORY**
- Build proof verdict (source claim): **NOT_ACCEPTED_AS_REPORTED**
- Run exit code (source claim): `0`
- Evidence complete (source claim): `True`
- Archive SHA-256: `4da91b4e0f81a852…` (verified archived bytes)
- Inventory files: 356 SHA-256 verified; metadata exceptions: 2 cross-checked
- Text-index entries: 272; chunks: 272 (remote chunk bytes not checked)


## Failure diagnostics (verified archived sources)

- Diagnostic status: **CORROBORATED**; causality: **CORROBORATED_SOURCE_REPORT**
- Runner-reported causal stage: `tool-reconstruction` (source assertion)
- Runner-reported blocker: `tool-reconstruction` / `adapter_error`
- Runner-reported detail (not independently causal): RuntimeError: A1-TOOL: R-only native reference build
- Audit provenance: `proof-audit.json` SHA-256 `216c3a8ce72b1e6a0bdff71e0a67f25e9eac0e9fba6930212e3a82789de593f4`
- Stage receipt: `a1-R-only-native-reference-build` state=`TERMINAL` exit=`2` timeout budget=`491`
- Stage provenance: `allprooflogs/cases/sort4-c1-current-recovery/a1-tool/a1-R-only-native-reference-build-stage.json` SHA-256 `66620752e728d7b7f66dfe0a20704d714845afd825a1f3fe1f18123e3b0e1e90`
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
