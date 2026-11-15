# F7 — exact-head coordinator CI request

READY_LOCAL_ONLY; all new native results NOT_RUN. No local builds, push or dispatch.
Source `8e299aa6243bc5f06a29c51e98aafa9564478220`, sole parent accepted6
`3f5242bb1539fb88196d7e503b722f0905f2b46c` / run43720042056. Source tree exactly
`9829702c1aa0ecb73c860fc0ad5451757917d6cb`; full diff against F empty.
Overlay `8288537e7c57b04d2462ff0c5bf1af38ab9d4451`, directly on F7, branch
`uninit-ci/c2-slices-07-w15`. Only `.github/c2-slices/` and `.github/workflows/`
change. Production/tests/docs/dependency pins remain exact F. Stock workflows are
removed only in the overlay. Exact overlay patch and hashes are in this directory.

Accepted recipe: overlay ece902633e / run43720042056. ubuntu-24.04,
RUST_TEST_THREADS=2, job120min, per-fixture2400s, no retries. Order: source guard,
setup, fmt, build-dev, workspace/tests clippy `-D warnings`, inherited units20,
delayed_cache6, delayed_scope2, all compiler76, cumulative Quick, sensitivity4/4,
structural comparisons, affected cprover+llbc build, always source guard/artifacts.
LLBC compilation runs last, after all default-backend controls.

The six suites retain all471 accepted6 selectors unchanged: kani50+3 ignored,
expected373+6 ignored, ui17, script3, json17, std2 =462 passes/9 existing ignores
if green. All212 current expected/uninit inputs, full ordinary FunctionContracts,
function-contract, B1/uninit/delayed-UB and strong/mode/root oracles remain selected.
[CI-REQUEST.json](CI-REQUEST.json) enumerates every selector, original argv, exact
native unit names and expected counts. Zero selection, name substitution, new
ignore, partial output or count drift fails. Libtest's `- should panic` display
suffix is parsed for the two explicitly named misuse tests.

F7 journal6 and actual scope2 test first originals including modified flags,
repeated delayed writes, warm/untouched/new regular retention, absent failed-root
removal, repeated/empty scopes, misuse, normal/early return and unwind reuse.
All eight are exact F and retain their canonical owner7 oracle mapping.
Sensitivity uses unchanged accepted6 patches/checker with only its source pin
updated. Require four intended completed golden mismatches, not arbitrary failures;
original bytes/modes restore on every path. No global object-bits/check suppression.

The new CI-only structural adapter uses byte-identical C2-S4 mixed.rs, relocated
under `.github/c2-slices/`; no deleted JSON suite or bound roots inventory is
restored to the exported source. [Provenance](STRUCTURAL-PROVENANCE.json) pins the
reused full-inventory observation/comparison helpers and the sole source-path
adaptation. Current shared schema/validator are used unchanged.

Run seven isolated roots and four fresh mixed invocations (AB, BA, cycle→legal,
legal→cycle), jobs1, separate target/export dirs, timeout180s each. Preserve
RUSTFLAGS edition2021/-Dwarnings, NO_COLOR, four original unstable features,
per-fixture object-bits12 and all original solver/safety/contract checks. Exact
expected original exits: 0,1,0,0,1,1,0,1,1,1,1. Require complete JSON + regular
selection, modes/PFC targets, terminal inventories/counters, failure and Unsupported
metadata and useful covers. Every mixed root must equal its OWN fresh isolated
root:18 accepted/exact comparisons, no added/removed/status/location changes.
No verdict-only or additions-only acceptance. Original child exits remain in each
result/receipt; aggregate status is separately labeled IN_PROCESS_AGGREGATION.

This compares fresh isolation, without binding absolute isolated inventories.
`binding_status=NOT_CHECKED_CAPTURE`, producer_order=ORDER_UNCONTROLLED,
order_credit=NOT_ESTABLISHED remain explicit. CLI selector order is not observed
producer order. Narrow codegen-unit debug output is retained for later bounded
inspection; no unit/Instance/order binding is inferred. Historical S4 baseline
run43621472749 (6/18 additions, no removals) and candidate43621476331 (18/18 exact)
are reused source-reported controls; neither is rerun or granted new proof credit.
The full cumulative expected suite separately retains per-root semantic oracles.

Always retain original argv/environment/exits/termination reasons/stdout/stderr,
source identities before/after, all suite logs/per-fixture native output, all4
sensitivity receipts and restoration snapshots,11 structural exports/regular
outputs/full inventories/check metadata/receipts,18 diffs, tools SHA-256s, CPU and
toolchain information, LLBC output and runner errors. Unstarted actions stay
NOT_RUN/null/NOT_STARTED. No source/golden change is authorized by a failure.

Static checks passed: source/F tree equality,4202 protected source entries,
CI-only diff, exact generator reproduction, all source/patch/manifest identities,
mutation apply checks, source/runner whitespace, Python parsing, two compile-seam
audits. Synthetic checks: runner24, structural15, sensitivity13, seam10. These
are Git/Python checks; native fmt/build/clippy/units/Quick/structural/LLBC remain
NOT_RUN. Coordinator alone may publish/dispatch. Cloud $0. No new Gate A or proof credit.
