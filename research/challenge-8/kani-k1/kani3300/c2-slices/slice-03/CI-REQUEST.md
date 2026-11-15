# Slice03 rewritten-head Quick request — NOT DISPATCHED

Source `5ca51679e3f433718807a2e44add0d5abac128e7`, parent
`932fb8395a58f8c86c0d702ba2cae835823b2962`.
Qualification kind **NO_REGRESSION**. Worker15 review/new CI-only overlay and
coordinator dispatch are pending. This request grants no dispatch authority.
The old overlay a2a533e087/run43704461635 does not qualify this head.

Keep recipe0998b98867:.github/workflows/uninit-quick.yml, ubuntu-24.04,
RUST_TEST_THREADS=2, fmt/build-dev/workspace-and-tests clippy -D warnings and suites.
Job cap120 min, test timeout2400s, no auto retry. Preserve stock checks/solver,
all original flags, existing ignores and useful assertions; no global object-bits.

| Suite | Selectors | Existing ignores | Expected pass if green |
| --- | ---: | ---: | ---: |
| kani | 53 | 3 | 50 |
| expected | 226 | 6 | 220 |
| ui | 17 | 0 | 17 |
| script-based-pre | 3 | 0 | 3 |
| json-handler | 17 | 0 | 17 |
| std-checks | 2 | 0 | 2 |

318 distinct selectors,309 passes plus nine existing ignores if green.
Common expected inventory94 (92+2 ignores). Both active_call_tests9 and
immutable_allocations::tests9 must execute exactly nine tests, with no zero-test
success. Inherited full FunctionContracts/function-contract and upstream/B1
uninit/delayed-UB smoke inventory remains selected; TEST-MANIFEST.json pins it.

ORACLE-DELTA.json selects only immutable-masks/empty, unchanged exact F bytes/flags
and literal SUCCESSFUL golden. It checks zero extent and supplies no nonempty
storage/raw/offset integration credit. All18 relocated fixtures have owner4 and
first executable head4; the nine prior nested Pat/enum/raw-eq-uninit/raw-MU cases
also remain PENDING on4, with complete exact F oracles in DEFERRED-OBLIGATIONS.json.
Do not turn Unsupported into an intended read failure or weaken a golden.
Owner1 integration remains PENDING on4/5; closure-layout qualification belongs5.

The new CI overlay must bind this exact source SHA/tree and change only CI files,
with source before/after identities and always-upload artifacts for failed/NOT_RUN
stages, original argv/exits/termination reasons. No old Part1 JSON suites or T1b
allowances. Quick is intermediate regression; it is not final Gate A or independent
formal proof credit. Rewritten-head native results and local builds/push/CI: NOT_RUN.
