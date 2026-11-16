# U-03 handoff

One requested local preparation stage. g0 branch `work/ch8-pr02-reset-u03-codex`
starts exactly at `f3658d28cd`; source and package continue from the retained U-02
worktrees/commits in separate U-03 branches. No existing branch was rewritten.

Source `f7e89f1942fa6f671f20ec45fde98d9d736dc122` is directly on PR02
`932fb8395a58f8c86c0d702ba2cae835823b2962`. Only the two read fixture main.rs
files differ from U-02; the other 26 fixture files and modes are identical.
Compiler diff is byte-identical to U-01/U-02 (SHA256 in COMPATIBILITY.json).

Package `80d0d98529445088db2fd2941fe9370ba6c0eaa6` on U-02
`952ea771be3827a495a9c9f29ad6a015bd796fc7` schedules A only and runs each gate
independently after successful patched build, aggregating failure. The generic
autoharness slice and old-controls now run even if reset fixtures fail.
Receipts retain original exits; always-finalize/upload and all limits remain.

Read CI-REQUEST.json, REVIEW.md and VALIDATION.json. `source.patch` applies to
both retained source pins; `ci-only.patch` applies on the replacement source and
reproduces the exact package tree. Full independent review packet:
`/root/ch8-pr02-reset-u03-review-packet`; its metadata/spec are copied here.
RESULT-U02.md retains the supplied U-02 failures and NOT_RUN gates without
inventing runtime evidence. The prior U-01 result is retained in `../u02/`.

Native U-03 checks and CI remain NOT_RUN. No local cargo/rustc/Kani/CBMC, push,
publication, ledger writes or new proof credit. This handoff grants no dispatch
authority; a coordinator needs separate authorization for the documented
same-tree trigger child.

Independent Luna High review: GO for this preparation/handoff only, no blockers.
The exact candidate and review/packet/spec SHA256 values are bound in
CI-REQUEST.json. Offline/static checks and nine synthetic test methods passed.
