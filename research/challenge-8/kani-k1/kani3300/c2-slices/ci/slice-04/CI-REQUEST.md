# Slice04 STORAGE/protocol+F6 — coordinator CI request

**READY_LOCAL_ONLY; native qualification NOT_RUN.**
Overlay `4f00e47d81da1e8849551e748ed378edbf868be1`, exact parent/source
`345cedfd67df679e326474385308349d609fc43d`, source tree
`e13784fc67ec6bb1b15f30dc851ef7460738e3eb`, source parent accepted03
`5ca51679e3f433718807a2e44add0d5abac128e7` / run43706759714. Input g0 `7655cf9542`.
Branch `uninit-ci/c2-slices-04-w15`, worktree `/root/kani-fix-3300-c2-slices-w15`.
[Independent worker15 review](../../reviews/slice-04.md): PASS_STATIC_ONLY; no source edits.

Recipe is accepted03 overlay `34b8008f12ac909d53803ddb1a4da956c498c19f` / run43706759714.
Only CI paths differ from the candidate. Stock workflows are removed only inside this overlay.
Prior runner behavior is unchanged; add argument_size and marker_category commands with exact
native test names. Workflow changes stage/count/artifact names and adds those two unit steps.
ubuntu-24.04, RUST_TEST_THREADS=2, job120min, per-fixture2400s, no auto retries.
Order: fmt → build-dev → workspace/tests clippy -D warnings → units → six cumulative suites.
Original fixture flags/goldens/solver/checks and per-fixture object-bits remain unchanged.

| Selection | Discovery | Passed if green | Existing ignored |
| --- | ---: | ---: | ---: |
| kani/kani |53|50|3|
| expected/expected |321|315|6|
| ui/expected |17|17|0|
| script-based-pre/exec |3|3|0|
| json-handler/exec |17|17|0|
| std-checks/cargo-kani |2|2|0|

Total413 selectors =404 passes +9 pre-existing ignores if green;20 additional units:
ActiveCalls9, immutable9, argument_size1, marker_category1. A zero test selection fails.
All318 accepted03 selectors remain;95 complete pairs join, four entry sources change to exact F,
and their inherited goldens remain identical. This includes the full inherited FunctionContracts/
function-contract and upstream/B1 regression selection, plus every present expected/uninit input.
Canonical Quick table counts predate the03 dependency correction; these exact candidate counts govern.
The source manifest's inherited unit scalar18 is superseded by the explicit9+9+1+1 request, without
editing worker14's packet or its byte-identical embedded manifest.

[CI-REQUEST.json](CI-REQUEST.json) contains exact argv, all selector/unit names,99 targeted fixture
input/golden hashes and prescribed N/verdicts. Each suite uses --exact --force-rerun --no-fail-fast
--timeout2400, an external build-base and native logfile. Require useful reached successes and
exact intended failures: unrelated layout/Unsupported/protocol failures do not qualify negatives.
Explicitly inspect Move/Copy/false/padding/stride/return0, both F6 read negatives and reinit, Hook
pairing refusal versus scalar Hook and marked-model controls. Do not accept aggregate exit0 as a
per-fixture integration receipt.

Head4 owner1 seven, owner3 nine and18 moved fixture obligations close only through their explicit
results on this exact head; preserve historical early-head statuses. All47 mapped head5 pairs remain
absent/pending. Seven no-capture closure-syntax fixtures were independently checked against the
actual stage4 guards; no closure5 prerequisite found statically. Unexpected native closure-layout
refusal is STOP, with exact fixture/cause and unchanged golden.

**S5 sensitivity4/4: DEFERRED TO5.** All eight strong oracle fixtures are absent on head4
(list in JSON/FIXTURE-REVIEW). On the first full strong-oracle head, require clean controls first,
then all four independent --force-rerun mutations, completed native verdict/N and intended golden
mismatch; compile error, timeout, early Unsupported or bare nonzero exit does not count.

Always upload c2-slices-04-evidence/: inputs/manifest, source before/after, original per-stage argv,
exit/termination reason, stdout/stderr, suite native logs and actual build-tests/per-fixture outputs.
Unstarted stages are NOT_RUN/null exit/NOT_STARTED. Missing/partial outputs, count/name changes,
new ignores or timeout fail the runner. Source-after and uploader run with always().

Validation: [SOURCE-VALIDATION](SOURCE-VALIDATION.json) covers204 paths,180 owner4 parts,99 exact-F
pairs,803 manifest identities and full present uninit discovery. [SEAM-VALIDATION](SEAM-VALIDATION.json)
is independent bounded static PASS; [FIXTURE-REVIEW](FIXTURE-REVIEW.json) records closure checks.
[STATIC-VALIDATION](STATIC-VALIDATION.json):21 runner synthetic checks and10 seam-checker checks pass,
protected source snapshot clean. [overlay.patch](overlay.patch) is the exact CI-only delta.
That artifact preserves trailing spaces in two deleted upstream workflow lines; the g0 whitespace
check excludes this nested patch only. Source/overlay diff checks and patch byte identity pass.

Push/dispatch and all native checks NOT_RUN; Cloud $0. Coordinator alone may push/dispatch.
Quick is intermediate regression/targeted qualification, not Gate A or independent formal proof credit.
