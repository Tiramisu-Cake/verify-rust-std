# Slice 03 LAYOUT-RAW — rewritten-head CI request

**READY_LOCAL_ONLY; qualification NO_REGRESSION; integration PENDING on4.**
Overlay `34b8008f12ac909d53803ddb1a4da956c498c19f`, tree
`ce90ae7197834ac216a2e8749ba3a0aa3e7c980a`, exact parent/source
`5ca51679e3f433718807a2e44add0d5abac128e7`, source tree
`689644ab2140794e17948dac6e7beb48bc9ea7bb`.
Source parent remains accepted slice2 `932fb8395a58f8c86c0d702ba2cae835823b2962`,
run43701587141. Input g0 `98e54033950bb0a1b0423d93932f83f7dc0d5288`.

Worktree `/root/kani-fix-3300-c2-slices-w15`, branch
`uninit-ci/c2-slices-03-w15-r2`. [Review addendum](../../reviews/slice-03.md):
PASS_STATIC_DELTA_ONLY. Production/docs unchanged from d0345ddf4f; only18 whole
fixture pairs removed, all absent from the accepted parent. No inherited test or
golden changed. The previous overlay a2a533e087/run43704461635 is superseded;
its fixture-placement failure does not qualify this rewritten head.

## Recipe and selection

Accepted slice2 overlay `536f1d20d127987cdd860bc6367acc9fff90c5cb` /
run43701587141 remains the recipe. Runner is byte-identical to its slice02_ci.py,
renamed slice03_ci.py. Changes are source/manifest pins, no-regression stage
names/count and artifact directory. Stock workflows are removed only in this
CI overlay. All3894 protected source entries retain exact source3 identities.

ubuntu-24.04; RUST_TEST_THREADS=2; job120min; per-fixture2400s; no auto retries.
Order: fmt → build-dev → workspace/tests clippy `-D warnings` → ActiveCalls9 →
immutable9 → six cumulative suites. Preserve original flags, solver, checks,
per-fixture object-bits and goldens; no added uninit flags on stock contracts.

| Suite / mode | Discovery | Passed if green | Existing ignored |
|---|---:|---:|---:|
| kani / kani |53|50|3|
| expected / expected |226|220|6|
| ui / expected |17|17|0|
| script-based-pre / exec |3|3|0|
| json-handler / exec |17|17|0|
| std-checks / cargo-kani |2|2|0|

Total318 selectors:309 passes +9 existing ignores expected, plus units9+9
(each exactly9 passed/0 failed/0 ignored by full native names). These are
expectations, not observations. All317 inherited selectors and identities remain;
only exact-F immutable-masks/empty is added. Common expected inventory94 =92
passes +2 old ignores. Full inherited FunctionContracts/function-contract and
upstream/B1 uninit/delayed-UB selection remains unchanged.

[CI-REQUEST.json](CI-REQUEST.json) contains exact argv, selector/unit names and
hashes. Embedded [TEST-MANIFEST](../../slice-03/TEST-MANIFEST.json) is byte-identical
to the source packet. Each suite uses `--exact --force-rerun --no-fail-fast
--timeout 2400`, external build-base and native logfile. Canonical stage0 Quick
and oracle maps remain historical; [ORACLE-MAP-CORRECTION](../../slice-03/ORACLE-MAP-CORRECTION.json)
is the explicit current dependency override.

## Pending integration and native review

Only immutable-masks/empty remains: literal SUCCESSFUL, zero extent. It supplies
no nonempty storage/layout/raw_eq integration credit. The18 moved pairs belong
to owner4 and first executable head4: promoted direct/helper legal/left/right,
immutable zero-byte legal/hole, u8 mixed raw/eq both orders, immutable static/
relocation/subrange legal/hole. Nine prior nested Pat/enum/raw-eq-uninit/raw-MU
obligations also remain pending4. Full exact F identities/oracles are retained in
[DEFERRED-OBLIGATIONS](../../slice-03/DEFERRED-OBLIGATIONS.json). Owner1 integration
remains pending4/5; closure qualification belongs5.

Coordinator [run43704461635 result](../../slice-03/ci-43704461635/RESULT.md)
reports18 early Unsupported failures caused by missing storage4 support. Those
are not intended read failures; no golden is weakened. Nonempty assertions,
operand checks and distinguishing negative outcomes must be explicitly reviewed
on4, including the known immutable-subrange-legal false positive.

## Artifacts and validation

Always upload c2-slices-03-evidence/, including source before/after identities,
inputs/manifest, original argv/exits/termination reasons, stdout/stderr, suite
native logs and actual compiletest build bases/per-fixture outputs. Unstarted
stages are explicit NOT_RUN/null exit. Partial/missing output, count/name
mismatch, new ignores and fixture timeout fail the runner; successful runner
status still requires review.

[SOURCE-VALIDATION](SOURCE-VALIDATION.json):8 changed paths,22 part hashes,613
manifest identities, unchanged production/docs and inherited tests, exact18-pair
removal, deferred27 absent. [SEAM-VALIDATION](SEAM-VALIDATION.json): bounded
static PASS/errors[]. [STATIC-VALIDATION](STATIC-VALIDATION.json):19 synthetic
runner checks PASS, accepted runner byte identity, clean overlay/source guard.
[overlay.patch](overlay.patch) is the exact CI-only patch.

Rewritten-head native fmt/build/clippy/units/suites, push and dispatch NOT_RUN;
Cloud $0. Coordinator alone may push/dispatch. Quick is intermediate regression,
not Gate A or independent formal proof credit. No stage4–7 work is authorized
by this request.
