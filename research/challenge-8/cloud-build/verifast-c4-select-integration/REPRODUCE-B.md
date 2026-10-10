# Recorded Cloud reproduction — session B

Pinned proof/infra: `835f6cb980f2e504e4456b7f559857a19c9b0627`.
Tool: `e2e674f8727259ef08c68e58bb5dae1bd723cf76`.
Profile: `verifast-c4-select-composition-20261010-b2`.

Recorded final invocation of the existing runner:

```sh
python3 research/challenge-8/cloud-build/control.py \
  --state-dir /root/verify-rust-std-verifast-compose2/.verifast-c4-composition-state \
  --phase-id VERIFAST-C4-SELECT-COMPOSITION-CLOUD-2026-10-10-B \
  --ledger research/challenge-8/cloud-build/verifast-c4-select-composition/BUDGET.json \
  --owner verifast submit \
  --infra-sha 835f6cb980f2e504e4456b7f559857a19c9b0627 \
  --proof-sha 835f6cb980f2e504e4456b7f559857a19c9b0627 \
  --lane verifast-c4-select-integration --timeout 1050
```

Build `f7da71e8-de68-4542-ae0a-aadf4936c233`, token
`dispatch-529dbd36a6ac4483be203b02abfed3ef`; config SHA256
`beb659658c97398fef7a5712f491f4c123f0fb2f95b7976c6690bba3c04e2986`.
Submit retry began before main cutoff; Build createTime21:38:01Z occurred while
completing that already-started step. This is a recorded invocation, not
permission to reopen the session. After ledger closure a fresh proof replay
requires owner-authorized phase registration and a new separate ledger;
retain these exact tool/proof/infra/recipe inputs. No automatic session.

Internal packet includes the local VeriFast branch bundle at
`research/verifast-input/e2e674f8727259ef08c68e58bb5dae1bd723cf76/bundle`,
SHA256 `479ffefedc5a8361d0631b7a3e78837349a6778847c3b58e5f23fdf2c70787cc`,
required base `f76012fb518703b1d98e243ac4f487f16877cfcb`.
Git bundle verification passed; no upstream publication/profile adoption.

## Repaired candidate — UNRUN

Proof/infra candidate: `4c2e244767547ac6c4b81bc61135d2f38d0ecadd`.
It restores the complete 30-row module pack and transports exactly two fixed
XZ artifacts. The local non-proof payload precheck is 529391 bytes / 177 parts
of 3990 bytes (cap191), SHA256
`b24cc5cdfa7a48ed378d0fb0912b56f890b497f5227e41c497b1b7f90d74d78c`.
It has not executed in Cloud and does not upgrade any proof verdict.

For a later explicitly authorized phase, use the existing runner with that
new phase registration and its own new ledger:

```sh
python3 research/challenge-8/cloud-build/control.py \
  --state-dir /root/verify-rust-std-verifast-compose2/.verifast-c4-composition-state \
  --phase-id "$NEW_AUTHORIZED_PHASE" --ledger "$NEW_LEDGER" \
  --owner verifast submit \
  --infra-sha 4c2e244767547ac6c4b81bc61135d2f38d0ecadd \
  --proof-sha 4c2e244767547ac6c4b81bc61135d2f38d0ecadd \
  --lane verifast-c4-select-integration --timeout 1050
```

The old B ledger is CLOSED. These placeholders express the necessary new
registration; they do not authorize a new session or reopen the old ledger.
The final packet metadata commit includes the candidate, reviews, tool bundle,
manifest, closed accounting and checkpoint; use the exact candidate above for
proof reproduction so documentation-only changes cannot alter its inputs.
