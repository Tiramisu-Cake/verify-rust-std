# C3 prefix Cloud session

Owner `select-sort4`; assigned worktree `/root/verify-rust-std-select-night`.
This session continues the actual sort4 mission within the bounded C3 step
described in [the C3 design gate](../sort4-c2-bound-prefix/NEXT-STEP.md).

Start **2026-10-10 10:20:59 UTC**, main deadline **12:20:59**, absolute
deadline **12:50:59**. The account is a fresh 3600 Cloud-build-second ceiling
with zero spent at registration. The extension is only for finishing the
current step, evidence, accounting and checkpoint. The authorized lane is
`o26-sort4-c1-current-recovery`; any second-direction caller-entry lane must
be added only if the session assignment requires it.

## Scope

Extend the completed C1+C2 prefix first through actual C3 normal completion,
strict lifetime exit, CURRENT pair recovery and four-cell join. After a full C3
verdict continue C4 and C5/select/copy within the remaining session and budget,
with a separate scope/path/CURRENT-recovery rationale for each extended prefix.
Preserve the actual source domain and full normal/unwind posts inherited from
the prior prefix. C1/C2 direct unwind skips C3; C3 direct unwind restores the
current resources and reaches the unchanged original unwind post and leak.
Keep the original std generic signature and unit return. Any distinct internal
helper returning the comparison result needs its own source-version-matched
proof and contract.

The first gate is to derive the selected `(c, a)` owners and complementary
frame for all four `c1`/`c2` boolean cases, including source-linked boolean
casts, in-bounds distinct addresses, provenance, permissions and CURRENT
values. Numerical pointer equality alone does not provide permission. The C3
callback temporaries need their own checked named binding and compiler-derived
`Output=bool` registration. Preserve all admissible boolean executions and
the existing default-off C1/C2 and unbound-refusal gates.

New verifier changes require the source/MIR/pre-AST certificate, semantic
rationale, and independent exact-delta review described in the design gate.
Do not infer execution of C4/C5, selects, or the whole sort4 contract from this
prefix. Do not add a caller-guard premise, MU inverse, or ZST/layout
implementation.

## Session start state

Read [WORK-POLICY](../../WORK-POLICY.md), policy commit
`c7ca8c467aecf10a4b53039372ee97714f854ee3` (blob
`61d4cd336a26df4925bd42d2846f9bc771263fde`). No Build is registered yet; no
proof result is implied by this session account or phase registration.
