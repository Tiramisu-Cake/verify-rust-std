# R21 fresh admission and S2d fingerprint

Defect: the branch client and callee runner only admit the closed R20 phase. Applicability: a fresh owner-authorized R21 account on the identical o26-select-callee-r20 lane.

Invariant: retain all R20 historical constants and account bytes, ownership and source certificates, 191-part transport ceiling, pinned-object-only submit, coordinator owner/slot/accounting controls. No tool, model, runtime algorithm, spec, ghost transform or proof-credit change. Accept only the exact R21 phase in the runner marker in addition to historical R20. Each phase uses its exact separate account and window. Foreign tool-worktree modifications are never consumed.

Controls: synthetic injected-clock exact account, owner, lane, timeout, deadline, reserve and source-mode refusals; provider/phase/GitHub/ambient opt-in refusals. Existing callee service tests cover missing/null/wrong-type/NOT_RUN, original failures and snapshots. R21 initially runs the unchanged HANDOFF branch-selected fingerprint (S2d), with baseline location control and MIR export/decode. Fingerprint success grants no proof credit.

Preparation: smallsort-session prepare/check completed with 68 closure entries. Reusing the R19 profile directly was refused because this minimal callee recipe intentionally has no A1 profile input. A generated DRAFT profile is retained here for review only; the original pinned R19 profile remains unchanged and no A1 activation env is sent. The final recipe remains the prior minimal recipe, with no profile or ledger payload because the account is a client input.
