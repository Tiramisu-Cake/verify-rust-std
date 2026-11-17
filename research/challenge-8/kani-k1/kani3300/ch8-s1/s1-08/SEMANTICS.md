# S1-08: bounded source equivalence and producer contract

Source `99e8456d200fff1299ee5756279cddb23921dc65`, parent
`5be85699b8826e3286c0bf89efb9affefac0acb5`. No source correction was necessary.

`equivalent` compares the entire two files lexically after the one permitted
rewrite of 23 assertion sites: `smoke` 8, `smoke_exact_n` 8, `positive` 7.
Assertion operands and their sequence, branches, assumptions, snapshots,
comparators, construction/geometry, types, cfgs and all cover expressions remain
identical. Strings/comments are tokens, so their contents are not whitespace
normalized. All code outside these three macro definitions, including negative
fixtures and panic paths, is unchanged. This is a bounded static lexical check,
not a Rust AST/compiler or runtime proof.

The original `assert!(cond, literal)` evaluates the Boolean condition once and
panics on false. The replacement evaluates that same Boolean once followed by a
constant string expression with no side effect. At tool `0aac16ef62da9e9d5645782d458593e5d78143ba`:

- `library/kani_core/src/lib.rs:186–200` marks `kani::assert` as `AssertHook`;
  the non-playback empty body is replaced by the hook, not used as a summary.
- `overrides/hooks.rs:163–201` extracts the constant message, creates the
  reachability check and calls `codegen_assert_assume(cond, Assertion, msg)`.
- `codegen/assert.rs:129–151` emits `assert(cond); assume(cond)`.
  The prove-safety-only branch would assume without asserting; the unchanged
  runner does not supply that option and its stock default is false.
- `codegen/assert.rs:214–244` maps the old panic path to
  `assert(false); assume(false)`. Thus the old false branch cannot reach later
  covers either. The new check remains an assertion, and later assertions and
  covers run under exactly the prior checks' successful-path conditions.
  A failing earlier check still prevents acceptance; a later SAT cover cannot
  discharge it. Required covers are not pre-check reachability claims.
- `codegen/operand.rs:317–369` records complete string-literal allocations;
  `utils/utils.rs:32–57` recovers their contents. The standard built-in
  `concat!` and `stringify!` declarations at source
  `library/core/src/macros/mod.rs:1141–1161,1268–1290` describe compile-time
  string expressions. Each substituted `$name` is one concrete identifier;
  there is no formatting, substring, pointer arithmetic or computed const.
- Default assertion reachability checks add internal `[KANI_CHECK_ID_…]`
  prefixes (`codegen/assert.rs:187–212`). The stock driver removes these
  after reachability annotation in `cbmc_property_renderer.rs:540–557,744–750`.
  The exact expected descriptions in ROLE-MAP concern postprocessed regular
  RESULTS, not raw CBMC prefixed strings. UNREACHABLE is not SUCCESS.
- `codegen/span.rs:111–122` maps macro spans toward their caller. Manifest
  coordinates record definition and selected invocation as source expectations,
  not observed property provenance. Unexpected locations remain UNKNOWN for
  the fixture interface; no exception is added to the runner.

The source transformation preserves the logical checks, not the number/order
of compiler-generated properties or a positive harness's panic diagnostics.
No positive harness catches these assertions' panics. Negative fixtures, their
original panic paths, predeclared failure IDs/descriptions and their legal
companions are retained. Only source hashes/line coordinates are refreshed for
the file shifted by the positive macro rewrite.

There are 127 required success obligations: 111 formerly ambiguous roles in
21 selected roots and 16 unchanged exact semantic bindings. The latter retain
historical evidence verbatim, including three complete helper instance sets;
their historical IDs (including closure coordinates) are not future-ID pins.
New labels require a single exact per-root description and SUCCESS in fresh,
compatible evidence, with no ordinal inference. The 16 existing bindings still
require the original semantic source/callsite audit against that fresh evidence.
The label fixture is a synthetic interface check and is not a replacement
acceptance classifier. Runner/collector do not import it. Independent W14 review
and offline admission remain pending.

For each selected entry root, `type_layout` and the two guarded N0/N1 checks
remain supplemental to the original 127 required bindings. ROLE-MAP records
all 54 such sites and applicability: fixed N2/N3 do not require N0/N1 SUCCESS;
symbolic N0..3 retains the corresponding guards. Four historical symbolic roots
are still defined but not inserted into the 35 scheduled rows. Static source
expansion distinguishes every label, including those unscheduled roots.

Compilation, rustfmt, runtime, actual exporter/decoder/verifier, CI and observed
S1-08 messages are NOT_RUN. These static arguments and synthetic fixtures grant
no independent proof credit, B1/B2 credit or general Challenge 8 theorem. Domain
remains the exact initialized N0..3 fixture, not all threshold16/32 inputs.
