# Exact Cloud invocation — session C

Runner/proof/infra `9ffa34d2c35032cb3bd5c4172b40c95989eb3fa9`.
Tool `4a34010cc3930eec46fc4e72c1b793ad734fa730`.
Profile `verifast-c4-select-composition-20261011-c3`.
Full30 source pack /12trees and two bounded XZ inputs retained; actual Python fixture preparation executes in Cloud before compiler setup. Ordered3patch delivery checked against all6effective sources; C4 kernel unchanged. Tool bundle `research/verifast-input/4a34010cc3930eec46fc4e72c1b793ad734fa730/bundle`, SHA256 `4e49738d4d48d98dcf93f73aa62aa3ce4f96fbe3ec7e77e84643008aeaee23d1`, required base `f76012fb518703b1d98e243ac4f487f16877cfcb`.

The actual submitted command (not permission to repeat after closure):

```sh
python3 research/challenge-8/cloud-build/control.py \
  --state-dir /root/verify-rust-std-verifast-compose3/.verifast-c4-composition-c-state \
  --phase-id VERIFAST-C4-SELECT-COMPOSITION-CLOUD-2026-10-11-C \
  --ledger research/challenge-8/cloud-build/verifast-c4-select-composition-c/BUDGET.json \
  --owner verifast submit \
  --infra-sha 9ffa34d2c35032cb3bd5c4172b40c95989eb3fa9 \
  --proof-sha 9ffa34d2c35032cb3bd5c4172b40c95989eb3fa9 \
  --lane verifast-c4-select-integration --timeout 1050
```

Build `063d90bc-572a-4182-bc04-9528b3a9eea3`; token `dispatch-44d398ca5c584396a845660a40b6ba57`; config SHA256 `bbdc396837b7d33b05468e8027e1bb494877aed984cfa70eb29c1982870c1b72`. Source payload SHA256 `7737246fda4e47efb58a56fe5930116f201c05bcd3e806fe3959115a30ada1e6`.

Proof result and raw review are recorded separately in the final checkpoint/manifest; this invocation alone grants no acceptance. The runner intentionally leaves independent raw review pending rather than treating its own classifiers as review. Original Cloud summaries and archives are immutable. Once this ledger is CLOSED, any later replay requires a separately authorized new registration and ledger with these exact runner/tool/recipe/semantic inputs. Do not reopen old accounting or start automatically.

Final raw verdict: selector/C4/composition PASS on this exact tested delivery, six intended controls raw-reviewed. Top-level run fails before outer proof at the absent infra manifest path; original summary is preserved. Corrected runner `ca5f54607bf9e36ecbb9a24085cc6cc9e18db98c` (includes manifest-path repair5506cde9 and exact source-487 saved-log classifier) is Cloud UNRUN and requires later explicit authorization. Session C ledger is CLOSED; no replay or new session starts automatically.
