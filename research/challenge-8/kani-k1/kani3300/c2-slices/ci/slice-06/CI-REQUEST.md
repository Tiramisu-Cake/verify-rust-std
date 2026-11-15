# Slice06 E1 — coordinator CI request

READY_LOCAL_ONLY. Native compilation, Quick, unit results and mutation4/4 on head6
are NOT_RUN; no push or dispatch. [Read-only review](../../reviews/slice-06.md):
PASS_STATIC_ONLY, no blocking findings.

Source `3f5242bb1539fb88196d7e503b722f0905f2b46c`, tree
`fc4c2d802e8c8c61ce7fcf27c405f7dc14c9d369`, sole parent accepted5
`96f5d5dc8dedd369c6986a4f1dd5e698b6167f0f` / run43715788377.
Overlay `ece902633e72af24dcd1157ee7b457d27840027c`, tree
`d8881ffa7a61d95b7096103ce52cb668bbcf5125`, directly on this source.
Branch `uninit-ci/c2-slices-06-w15`, worktree `/root/kani-fix-3300-c2-slices-w15`.
Input g0 `75c4267aa8` (full identity in JSON). Only `.github/c2-slices/` and
`.github/workflows/` change; stock workflows removed only in this CI overlay.

Recipe: accepted5 overlay `ce56d3d467dd9aeec0fc7abc6a2444ee066e85f6`, run43715788377.
Runner bytes are identical to accepted5. ubuntu-24.04, RUST_TEST_THREADS=2;
fmt → build-dev → workspace/tests clippy -D warnings → explicit units → full
compiler units → cumulative suites → S5 sensitivity. Job120min, per-test2400s,
no retries. All original flags/solver/checks/goldens retained; no global object-bits.

| Suite | Discovery | Passed if green | Existing ignored |
| --- | ---: | ---: | ---: |
| kani |53|50|3|
| expected |379|373|6|
| ui |17|17|0|
| script-based-pre |3|3|0|
| json-handler |17|17|0|
| std-checks |2|2|0|

471 selectors =462 passes +9 existing ignores if green. All460 accepted5 selectors
are unchanged;11 E1 join. All212 current expected/uninit inputs are selected.
All compiler units:68 exact names (no F7 units yet); also explicit ActiveCalls9,
immutable9, argument_size1, marker_category1. Zero selection, substituted names,
new ignore, timeout or count drift fails the runner. Full FunctionContracts,
function-contract, upstream/B1 uninit/delayed-UB and common Quick remain selected.

[CI-REQUEST.json](CI-REQUEST.json) records every selector, argv and unit name,
all11 E1 pairs plus inherited head5/strong/mode/root and part1-composition oracle
hashes and exact golden lines. Require all E1 outcomes:4 legal SUCCESS,
5 intended uninitialized reads,2 explicit by-value DST size refusals. Useful layout
and payload assertions remain; an extra Unsupported is not a substitute for an
intended read failure. E1 goldens intentionally retain F's literal precision,
without inventing exact failed-property counts. Review native per-fixture outputs.
Inherited composition/strong/mode oracles retain exact N/required failures/useful
SUCCESS. Replace local PFC companions only execute when selected; simple-check
remains separate. Accepted4/5 integration receipts keep their historical provenance.

S5 mutations: rerun all4 independent accepted patches on exact head6 after the clean
expected suite passes. Input/patch hashes checked; same built tools, no rebuild;
unique --exact --force-rerun --no-fail-fast --timeout2400 output directories.
Require compiletest exit1, exactly the selected FAILED record and intended golden
mismatch, completed native verdict/N and one-harness completion. Repaired write
requires SUCCESS/N0; its permitted write can be var_7 after removal of outside's
write (previously var_8). Concrete native local numbering is not an identity gate.
The mismatch must still identify the original golden outside-assigns FAILURE.
Extra-failure must preserve the original failure and the added reached failure;
golden inversion is sanity only. Compilation/setup/timeout/early Unsupported or
unrelated nonzero exit is not detection. Restore original bytes/modes after each
variant, including exceptions; before/after source snapshots verify restoration.

Always upload c2-slices-06-evidence/: inputs/manifest; full protected source identities
before/after; original per-stage argv, environment, exits, termination reasons,
stdout/stderr; all six native suite logs and build-tests per-fixture outputs;
all4 mutation records, patches/mutated bytes, native .out/.err, snapshots and
summary; runner-errors when present. Unstarted stages: NOT_RUN/null/NOT_STARTED.
No source-oracle change is authorized in response to failure.

[Static validation](STATIC-VALIDATION.json): runner synthetic23, sensitivity13 and
seam synthetic10 PASS; generator reproduces exact overlay;4201 protected source
entries verified. [Source validation](SOURCE-VALIDATION.json): all25 paths exact F,
zero production delta; exact14-hunk/5-file F7 residual and alternate-index F tree.
[Seam audit](SEAM-VALIDATION.json) plus cumulative audit: PASS_STATIC_ONLY.
[overlay.patch](overlay.patch) and accepted mutation patch retain original whitespace
as data; source/runner whitespace checks have no exemption.

Coordinator alone may publish/dispatch. Local native builds/tests/push/dispatch
NOT_RUN; Cloud $0. This Quick is intermediate regression/targeted qualification,
not Gate A or proof credit. F7 extraction remains a separately authorized stage7.
