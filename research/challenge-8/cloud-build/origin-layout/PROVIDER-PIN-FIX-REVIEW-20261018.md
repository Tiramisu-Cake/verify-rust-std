# Provider base pin correction — source review

Candidate parent3838d91cf491cfd3557f1198891dc2a5f96e86e0. Production adapter
change: only expected run.sh SHA256 a0ddebad721fe49d510f74b52f0eae105bef863a5258f919ab915ab63bc8e279
→ ae0aa063624630f651fc4b466bc2e39c0ad017be75652a43ae2130eea672ca54.
New expected value binds exact Git blob a7db3efdec43759d491d679e0237fbe9734646a9
at proof08b61d8162b1c01c840ed573847622a004232a05, not arbitrary current bytes.
All18 strict checks and validate-before-transform ordering unchanged.

Independent reviewer /root/review_base_pin, GPT-6 Luna High, fork_turns=none:
GO, no findings. Reviewer checked Git hash, all18 guards, recipe same-PROOF_SHA
pairing and absence of configured MERGE_OVERLAY_TOOL overrides; independently
ran all three regression tests and git diff --check: PASS. No nested delegation.
Old same-proof pairings0d16c161/e2d8182f retain all18 matching pins. All six merge
modes share the gate. No dual-version adapter needed for these source contracts.

Main checks: three tests PASS, including18 Git source hashes and18 synthetic
single-byte refusals before transforms/without source mutation; AST/bash syntax
and diff checks PASS. Rechecked2026-10-18 with unchanged inputs: PASS. Synthetic
transforms stop at a mock boundary; no real overlays/proof tools run locally.
Tool/profile/semantics/historical verdicts/ledgers unchanged. These are source
and service checks, not Cloud buildability or proof acceptance.
