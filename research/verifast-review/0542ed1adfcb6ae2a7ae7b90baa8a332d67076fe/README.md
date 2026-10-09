# VeriFast review checkpoint 0542ed1adfcb6ae2a7ae7b90baa8a332d67076fe

Verdict: **READY_FOR_CLOUD_VALIDATION**. The exact ManuallyDrop::new identity
lowering advertises a cleanup successor for which it emits no unwind edge.
The unchanged candidate repairs that inventory; genuine call unwind and mandatory
dead-code checks remain. No concrete blocking source-patch defect was found.

- [Review card](docs/challenge8/handoffs/manuallydrop-new-cfg.md)
- [Existing evidence and limits](docs/challenge8/reviews/manuallydrop-new-cfg-20261009/EVIDENCE.md)
- [Cloud checks and minimal delivery plan](docs/challenge8/reviews/manuallydrop-new-cfg-20261009/CLOUD-VALIDATION.md)
- [PR draft — not published](docs/challenge8/reviews/manuallydrop-new-cfg-20261009/PR-DRAFT.md)
- [Prepared tests](tests/rust/purely_unsafe/manuallydrop_new_cfg/README.md)
- [Current AGENTS](AGENTS.md), [WORKFLOW](docs/challenge8/WORKFLOW.md), [STATUS](docs/challenge8/STATUS.md)
- [Provenance manifest](manifest.json)

Proof source `0ecff7ee7e6fd5d88082915252cae5dd2395bf93`, original patch SHA256
593d09405379974ffbc475c2e0b65d648d8a6913f55b765dd0c3bebdc0922781.
Upstream base `f76012fb518703b1d98e243ac4f487f16877cfcb` → unchanged transplant
227dc163117e85d89fb1877bfc1e239a0628e5ab → final tests/tool candidate `1435539475fdaa7810bc2bc780fba0514f765f48`.
Organizational commits324d247c… and this checkpoint are separate from tool history.
The [tool diff](docs/challenge8/reviews/manuallydrop-new-cfg-20261009/tool.diff)
and [incremental tool bundle](docs/challenge8/reviews/manuallydrop-new-cfg-20261009/tool-candidate.bundle)
contain original Git identities and require the exact base. No adaptation or
implementation correction of the original translator patch was made; tests are
new work, not independently executed corrections of the reviewed patch.

O1 artifact11517185187/run37698481357 was retrieved and its API digest verified.
Saved logs show stock forget failure, old candidate success, retained shared
cleanup and intended negative/dead-code rejections. All66 source/MIR comparisons
match. This is reading historical experimental evidence, not a new proof run.
The old broad AST marker and refiner unwind TODOs require function-bound gates.
New builds, five fixtures, upstream suite and actual consumer integration are
**NOT_RUN**; no tool qualification, profile/pin adoption or proof status upgrade.

This package is authorized only on Tiramisu-Cake/verify-rust-std review/verifast.
It appends a new directory and preserves the previous d1d533d… package/history.
No main/peer worktree/index/ledger/coordinator changes, upstream PR or fork.
One next task: separately authorize and implement/service-test the incremental
bundle restore lane; no Build before a verifast phase, budget and admission exist.
