# W0-A1 READY — local preparation only

Std test package `65864680a145c90c583dcba7efd1d569475519fc`, parent6075, branch work/ch8-w0-a1-w15.
CI-only package `bf81a1f14f9468c5b25d3ee33f7dafbf2bca131e`, parentSEL1, branch work/ch8-w0-a1-ci-w15.
Both are local [skip ci] commits; no trigger was created. CI package tree `437a32326d9bf6a95120cde1b4f05433c3a055a0`.

Start with [CI-REQUEST.md](CI-REQUEST.md) and [CI-OVERLAY.json](CI-OVERLAY.json).
Executable request is [CI-REQUEST.json](CI-REQUEST.json), identical to the embedded copy;
request SHA-256 `6f49f0dec801a14f4dd33205620d0114a606959a2d2f0ad7c677d6bbd2e26e71`. The CI-only patch and std overlay/combined
patches are preserved locally with exact hashes. Worktrees are clean at package freeze.

Coordinator owns publication, same-tree non-skip trigger creation, R1/R2 scheduling and
common dispatch accounting. Match fresh uninit-ci/ch8-w0-a1-r1-* and r2-* branch prefixes,
exact control/export trees, attempt1, max-parallel1, no retries. This work reserves no
slots or priority over S. R3 remains unused; no compiler/model work is authorized.

15 synthetic methods and nine YAML wiring mutations passed. Independent static review
has no remaining blocker. Compilation/dispatch/proof/results remain NOT_RUN; Cloud $0.
Read RESULT.md before future evidence acceptance. Analysis of coordinator runs is a
separate session; no current CI result is inferred or borrowed from S/replay.
