# Worker14 — F7 CI overlay review

PASS bounded static CI review; no open findings. Final overlay
`8288537e7c57b04d2462ff0c5bf1af38ab9d4451`, tree
`19688715fe7d088c681c7b4093dbc8d62b935442`, directly on F7 source
`8e299aa6243bc5f06a29c51e98aafa9564478220`. Source remains exact F tree
`9829702c1aa0ecb73c860fc0ad5451757917d6cb`. Only `.github/c2-slices/` and
`.github/workflows/` differ. Source review remains `f7-worker14.json` at c04f1bdc72.

One concrete reporting finding was returned to the writer and resolved: the full
compiler native list/runtime gate already required76, but current metadata still
said68, with relevant/absent counts20/8. Final fields are76/28/0/76; the note explains
inherited20 plus F7 journal6/scope2. The inherited test manifest retains its20-unit
field; the effective runner configuration explicitly requires28 relevant and76 full
compiler units. Native zero/substituted/duplicate/new-ignore results fail strict
name and count checks. `should panic` labels are parsed without changing identities.

Structural preparation covers seven fresh singleton invocations and four mixed
selections:11 processes,18 exact comparisons. The mixed Rust input is byte-identical
to accepted S4; no bound inventory or old runner is installed. The observer's
observation body changes only the source path. Normalization, JSON loading and
regular parsing helpers are inherited; inventory/selection/root comparison
functions preserve exact complete-row comparison. Removing bound single/pair
checks is explicit: this compares fresh mixed captures against their own fresh
isolated captures. Cumulative semantic expected tests remain a separate required
gate. No old T1b additions allowance is present.

Each invocation uses exact selectors, jobs1, a unique fresh target/export directory
and180s timeout. Receipts preserve original argv/environment/exit/termination reason
and input/output hashes. Incomplete/missing/malformed JSON, wrong roots/targets,
stale timestamps/outputs, invalid configurations, duplicate IDs, nonterminal checks,
counter drift, mismatched failure/Unsupported metadata and inventory additions or
removals fail. Comparisons retain successful/unreachable checks and covers as well
as failures. Timeout/launch/exception paths preserve native failure data and cannot
become a structural PASS. Environment restoration and aggregate reporting use
`finally`. `structural/result.json` now records in-process aggregation separately
from original child exits. CLI selector order remains ORDER_UNCONTROLLED; producer
order credit is NOT_ESTABLISHED and captures remain NOT_CHECKED_CAPTURE.

The sensitivity runner differs from accepted head6 overlay ece902 only in its exact
SOURCE_SHA pin to F7. Four mutation patches and their detection rules are unchanged.
The cumulative471 selectors,462 expected passes and9 existing ignores remain intact.
Workflow adds6+2 filters/full76 units and an affected cprover+llbc feature build after
default-backend controls. Existing source guards, per-fixture2400s,120min job cap,
RUST_TEST_THREADS=2, native failure retention and always-upload behavior remain.
Structural object-bits12 is confined to the inherited structural input; no global
check/profile weakening is introduced. LLBC compilation is requested, not observed.

Independent Python-only synthetic checks passed: runner24 and structural15. Tests
ran during preparation; the final delta to behavior-reviewed ed2612 contains only
the corrected metadata and trailing blank removal. Final overlay objects, source
binding, manifest hashes and prepared payload identities were checked explicitly.

Native builds/fmt/clippy/units/Kani/CBMC/LLBC, push and CI dispatch: NOT_RUN. No runtime,
producer-order or independent proof acceptance is claimed. Only this report and
its JSON sibling were written; writer-owned package and source paths were untouched.
