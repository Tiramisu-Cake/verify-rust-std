# Coordinator handoff — prepared, not dispatched

Source345cedfd67df679e326474385308349d609fc43d, tree e13784fc67ec6bb1b15f30dc851ef7460738e3eb,
parent5ca51679e3f433718807a2e44add0d5abac128e7 (accepted03 run43706759714).
Worker15 prepares/reviews its exact-parent CI-only overlay separately; worker14 has not created,
pushed or dispatched one. This package does not authorize dispatch.

Use accepted recipe0998b98867 on ubuntu-24.04, RUST_TEST_THREADS=2, job cap120min and per-test2400s,
no automatic retry, original solvers/flags/checks and per-fixture object-bits. Required order:
fmt, build-dev, clippy workspace/tests -D warnings, then targeted units and full cumulative manifest.
Unit filters: active_call_tests9, immutable_allocations::tests9, argument_size_tests1,
marker_category_tests1; zero selected tests is not successful qualification.

TEST-MANIFEST.json has413 deduplicated compiletest selectors, nine pre-existing ignores:
all present expected/uninit plus common/ancestor regression suites, full FunctionContracts25 and
function-contract138 retained. Native discovery/counts must match; units are additional.
99 target pairs are exact F sources/goldens in ORACLE-DELTA.json, including both marked-model
controls, Move/Copy/padding/F6, nested Pat/enum/raw-eq-uninit, seven owner1 obligations and18 pairs
moved from03. The seven capture-free closure-syntax controls were source-audited; stage5 closure
layout itself is absent. Generated-modifies-no-shadow remains on5.

Require exact intended failures and useful reached successes per fixture. Preserve native exits,
selector/ignore counts and every failure; unsupported/layout/protocol substitutes do not close an
uninit negative. DEFERRED-OBLIGATIONS.json keeps earlier historical qualification unchanged:
per-fixture runtime results at exact cumulative4/5, not aggregate exit0, close integration.
No native result for this candidate is available yet. F gate evidence is not inherited by this head.
