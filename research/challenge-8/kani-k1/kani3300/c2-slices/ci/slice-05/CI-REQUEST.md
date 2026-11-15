# Slice05 CLOSURE — coordinator CI request

**READY_LOCAL_ONLY; native checks, deferred integration receipts and sensitivity4/4 NOT_RUN.**
Exact source `96f5d5dc8dedd369c6986a4f1dd5e698b6167f0f`, tree
`445fe95f622016728286e2b820c52b626809923b`, parent accepted4
`345cedfd67df679e326474385308349d609fc43d` / run43710024495.
Overlay `ce56d3d467dd9aeec0fc7abc6a2444ee066e85f6`, tree `5af225d7acb261064e63d41aa7bd2a516edea01a`;
one CI-only commit directly on the source. Branch `uninit-ci/c2-slices-05-w15`, worktree `/root/kani-fix-3300-c2-slices-w15`.
Input g0 `7551f71dc20e3b2c464bbb5818df5ee29eb51d1c`.
[Worker15 read-only review](../../reviews/slice-05.md): PASS_STATIC_ONLY, no source edits.

Reuse accepted4 overlay `4f00e47d81da1e8849551e748ed378edbf868be1` / run43710024495.
Only `.github/c2-slices/` and `.github/workflows/` change; stock workflows are removed
inside the overlay. ubuntu-24.04, RUST_TEST_THREADS=2, fmt → build-dev → workspace/tests
clippy -D warnings → units → cumulative suites → four sensitivity mutations.
Job120min, per-fixture2400s, no auto retries. Keep original flags, checks, solver,
object-bits and goldens; no global object-bits or ignores. Source and uploads run always.

| Selection | Discovery | Passed if green | Existing ignored |
| --- | ---: | ---: | ---: |
| kani/kani |53|50|3|
| expected/expected |368|362|6|
| ui/expected |17|17|0|
| script-based-pre/exec |3|3|0|
| json-handler/exec |17|17|0|
| std-checks/cargo-kani |2|2|0|

460 selectors =451 passes +9 existing ignores if green. All413 accepted4 selectors remain
byte-identical;47 complete exact-F pairs join. Full compiler unit selection is68 exact
native names on this source (F's76 minus8 F7 units). Also execute the inherited explicit
ActiveCalls9, immutable9, argument_size1, marker_category1 filters (20, included in68).
Missing names, zero selection, count drift, new ignore and timeout fail the runner.

All47 target input/golden identities and expected verdict/N are in [CI-REQUEST.json](CI-REQUEST.json).
Every currently present expected/uninit source is selected, including all8 strong oracles,
7 modes and7 roots, all closure/capture cases and generated-modifies-no-shadow. Full
FunctionContracts/function-contract and upstream/B1 regression selectors remain included
with their original flags. Require per-fixture completed useful SUCCESS and exact intended
negatives; unexpected layout/protocol/Unsupported is STOP, never a golden update.
Recursive ordinary/check keep their explicit cycle boundary while simple-check is legal.
Replace selects only the caller; local required PFC companions do not imply their execution.

The request embeds [CLOSURE-OBLIGATIONS](../../slice-05/CLOSURE-OBLIGATIONS.json) and hashes
of owner1/4 source parts. Every deferred-on5 item, including ordinary-slots/positive,
points-to-cycles/capture-free, contract/strong/mode/root paths and generated-modifies,
closes only after its explicit result on this cumulative head. Preserve prior historical
head1/4 qualification and say “integration-tested on head5”. Aggregate exit0 and static
review cannot close obligations. Accepted4 obligations remain as recorded.

S5 sensitivity must detect4/4 original independent test-only mutations after the clean
expected suite passes. Verify input/patch hashes, unique output directories and
--exact --force-rerun --no-fail-fast --timeout2400. Reuse the same built tools; no rebuild.
Restore original source/golden bytes and modes after EACH variant, including exceptions.
Require exact selected compiletest FAILED with exit1, completed native Kani verdict/N,
and the intended golden mismatch. Extra-failure must retain the original outside-assigns
FAILURE; repaired-write must reach SUCCESS; positive deletion must lose the intended
useful assertion; inverted golden is sanity only. Compilation, timeout, early Unsupported
or an arbitrary nonzero exit never counts. Any parser/output ambiguity fails qualification.

Always upload c2-slices-05-evidence/: pinned inputs and manifest, full source before/after,
original stage argv/exits/termination reasons/stdout/stderr, six native suite logs and
per-fixture build-tests outputs, all four mutation records and native .out/.err,
mutation patch and mutated bytes, per-variant restoration snapshots and summary.
Unstarted stages remain NOT_RUN/null exit/NOT_STARTED. Coordinator reviews all47 explicit
results and four intended mismatch records; mutation exit1 is expected only within the
sensitivity validator and does not turn an ordinary suite failure into success.

[Source validation](SOURCE-VALIDATION.json):95 paths,2 owner5 parts,47 exact-F pairs,
897 manifest identities, all201 present uninit selectors, no6/7 imported.
[Seam validation](SEAM-VALIDATION.json): independent bounded static PASS over48 changed
Rust files and reviewed API contracts. [Fixture review](FIXTURE-REVIEW.json): no static6/7
prerequisite. [Static validation](STATIC-VALIDATION.json) records runner/checker synthetic
checks and exact-source snapshot. [overlay.patch](overlay.patch) is the exact CI-only delta;
two upstream deleted lines retain trailing spaces, so g0 whitespace check excludes this
nested patch only. No source whitespace exemption.

Local native fmt/build/clippy/units/tests/Kani, push and dispatch NOT_RUN; Cloud $0.
Coordinator alone may push/dispatch. This is intermediate Quick regression and targeted
qualification, not Gate A or independent formal proof credit. B3 T1b is a separate task.
