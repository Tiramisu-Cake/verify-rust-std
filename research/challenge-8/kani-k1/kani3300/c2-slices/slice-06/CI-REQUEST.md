# Slice 06 coordinator request — prepared, not dispatched

Source `3f5242bb1539fb88196d7e503b722f0905f2b46c` on accepted5
`96f5d5dc8dedd369c6986a4f1dd5e698b6167f0f` (run43715788377).
Exact tree and machine-readable selectors/identities: `CI-REQUEST.json` and
`TEST-MANIFEST.json`. Worker15 prepares the separate exact-head CI-only overlay.

Use the accepted Quick recipe: ubuntu-24.04, `RUST_TEST_THREADS=2`, fmt → build-dev
→ workspace/tests clippy `-D warnings` → all cumulative selectors and relevant
units. Job cap120min, per-test2400s, no retries; retain each fixture's original
flags and checks. No global object-bits override, new ignore or golden changes.

Static discovery:471 selectors,462 expected passes and9 existing ignores. Expected
suite379 (373+6 ignores), kani53 (50+3), ui17, script-based-pre3, json-handler17,
std-checks2. `common_expected` contains247 entries before cross-group deduplication;
it is not the entire expected-suite count. Relevant units remain20 (9+9+1+1);
F7's6+2 units are absent by design. Zero filtered tests do not qualify a unit.

All11 E1 selectors are mandatory: four legal SUCCESS cases, five intended
uninitialized-read failures, and two by-value DST unsupported-size failures.
Preserve useful payload/layout assertions. Extra Unsupported is not a substitute
for a required read failure. Edge goldens preserve F's literal precision; no new
exact failed-property-count claim is made. All inherited composition/modes/strong
fixtures stay selected. S5 mutation4/4 acceptance is inherited from accepted5 with
unchanged production and all previous fixtures; see `S5-INHERITED-ACCEPTANCE.json`,
including the coordinator's manual fourth-mutation decision.

Retain original native argv/exits/termination reasons, useful SUCCESS/negative
outcomes, before/after source identities, and always-upload artifacts. This request
does not authorize dispatch. Native results on head6 are NOT_RUN; no Gate A or
formal proof credit is inferred from earlier F or head5 runs.
