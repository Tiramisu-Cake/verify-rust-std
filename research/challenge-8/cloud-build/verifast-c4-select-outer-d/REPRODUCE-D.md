# Session D — exact corrected runner invocation

Tool `4a34010cc3930eec46fc4e72c1b793ad734fa730`; profile `verifast-c4-select-composition-20261011-c3`; runner source `ca5f54607bf9e36ecbb9a24085cc6cc9e18db98c`. Delivery `84f21b3bf244eb352cb91584fc84a73d6703b117` adds only the new phase/account/registration to checkpointc652. The delivered integration driver/regressions are byte-identical to ca5. Full30-module pack, both bounded XZ, source/MIR/AST pins, ordered3patches and tool bundle are unchanged.

```sh
python3 research/challenge-8/cloud-build/control.py \
  --state-dir /root/verify-rust-std-verifast-compose4/.verifast-c4-outer-d-state \
  --phase-id VERIFAST-C4-SELECT-OUTER-CLOUD-2026-10-11-D \
  --ledger research/challenge-8/cloud-build/verifast-c4-select-outer-d/BUDGET.json \
  --owner verifast submit \
  --infra-sha 84f21b3bf244eb352cb91584fc84a73d6703b117 \
  --proof-sha 84f21b3bf244eb352cb91584fc84a73d6703b117 \
  --lane verifast-c4-select-integration --timeout 1050
```

This records the submitted command. Token/config/Build and result are recorded in ledger/checkpoint, preserving original Cloud summaries. Once the account is CLOSED this command is historical reproducibility, not authority to reopen it; no automatic new session. A later replay requires separately authorized registration/account. Proof outcomes and independent raw review remain distinct from command execution/profile adoption.
