# Slice03 exact-head Quick request — NOT DISPATCHED

Source `d0345ddf4f70d10caf5ee34ddca402867264379e`, parent
`932fb8395a58f8c86c0d702ba2cae835823b2962`. Full source tree/patch/map hashes:
SLICE.json, STATIC-VALIDATION.json, SOURCE-PARTS.json. Worker15 independent review and
CI-only overlay preparation are PENDING. This request does not authorize dispatch.

Use the accepted recipe `0998b98867:.github/workflows/uninit-quick.yml`, ubuntu-24.04,
RUST_TEST_THREADS=2, fmt → build-dev → workspace/tests clippy `-D warnings` → units/suites.
Job cap120 minutes, per-test2400 seconds, no auto retry. Retain stock checks/solver and
original per-fixture flags; no global object-bits or disabled UB/assert/contract checks.
Exact selectors, original directives and source/golden identities: TEST-MANIFEST.json.

| Suite | Selectors | Existing ignores | Expected pass if green |
| --- | ---: | ---: | ---: |
| kani | 53 | 3 | 50 |
| expected | 244 | 6 | 238 |
| ui | 17 | 0 | 17 |
| script-based-pre | 3 | 0 | 3 |
| json-handler | 17 | 0 | 17 |
| std-checks | 2 | 0 | 2 |

336 distinct selectors,327 passed +9 pre-existing ignores if green; additional unit
filters active_call_tests9 and immutable_allocations::tests9 must each execute exactly
nine tests. No zero-test success. Full inherited FunctionContracts/function-contract,
upstream/B1 uninit+delayed-UB and ordinary smoke selectors remain; do not exclude any
present test after a failure. Common expected head3 inventory has112 selectors,110
expected passes +2 existing ignores, agreeing with the accepted oracle/Quick map.

Targeted19 complete fixtures are listed in ORACLE-DELTA.json with all intended assertions,
literal oracle blocks and exact-N requirements where present. Require reached useful
SUCCESS for both orders of u8 raw/eq stack/promoted comparisons, legal/zero/empty immutable
operands and direct/helper promoted RawEq. Left-hole and right-hole promoted controls
must fail their respective checked byte extents, with the opposite operand's success
where the golden requires it. Static/subrange/relocation hole controls must match their
intended failure; an extra Unsupported, earlier UB or setup failure is not qualification.
`part1-edges/immutable-subrange-legal` deliberately retains the known legal-subrange
false positive: its exact F golden requires FAILED and the `[u8; 3]` uninitialized-read
diagnostic. Do not count that assertion as a positive SUCCESS or repair its golden.
Preserve full intended golden precision, without treating every literal-only golden
as an exact-N oracle. Record actual checks, raw argv/exits/termination reasons in CI
artifacts for review rather than inferring semantics from aggregate exit0.

Nested Pat/enum, complete raw-eq-uninit and four raw-MU mixed fixtures remain PENDING
until4 with exact closure receipts. No claim of nested offset qualification on3.
Storage/argument_size/marker units belong4, closure layout5, F7 units7.

Overlay must bind exact parent/source SHA/tree and source before/after identities,
modify only CI files, preserve compiler/runtime/tests/docs/pins, and retain always-upload
artifacts including failed/NOT_RUN stages and original exits. No old Part1 JSON suites
or T1b allowances. Quick is intermediate regression/target qualification, not final
three-platform Gate A or independent formal proof credit. Local native results NOT_RUN.
