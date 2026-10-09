# Continuation after closed VeriFast phase

Recorded Builds can be inspected without reopening the expired phase:

```sh
cd /root/verify-rust-std-verifast-infra
PYTHONDONTWRITEBYTECODE=1 python3 research/challenge-8/cloud-build/control.py \
  --phase-id VERIFAST-MDNEW-CFG-CLOUD-2026-10-09 \
  --ledger "$PWD/research/challenge-8/cloud-build/verifast-mdnew/BUDGET.json" \
  --state-dir "$PWD/.verifast-cloud-state" --owner verifast \
  status 91e5ba26-9a4e-44e0-8bf3-92dc1e4455bd
PYTHONDONTWRITEBYTECODE=1 python3 research/challenge-8/cloud-build/control.py \
  --phase-id VERIFAST-MDNEW-CFG-CLOUD-2026-10-09 \
  --ledger "$PWD/research/challenge-8/cloud-build/verifast-mdnew/BUDGET.json" \
  --state-dir "$PWD/.verifast-cloud-state" --owner verifast \
  download 91e5ba26-9a4e-44e0-8bf3-92dc1e4455bd \
  --output /tmp/verifast-continued-91e5ba26
```

Do not submit with this closed account. A further paid attempt needs a new
explicitly authorized phase/window/budget, its own ledger/state, exact published
infra/source pin and acceptance through the same coordinator. Preserve these
historical accounts and token receipts. No inherited balance or deadline extension.

Proof owners follow ADOPTION.md and PARALLEL-BUILDS-V3.md for the portable protocol
commit; no later verifast-specific control.py replaces theirs. Three slots remain
inactive until all installed-client acknowledgments and locked migration succeed.

One next assignment: resolve the false-unwind fixture's unmarked closing-brace dead code; if fixture bytes change, create a new original tool/test commit, manifest and bundle; repeat all focused gates with capture-log correction cbfe28393e1e61aacf0957466ee91e9243b25d2f in a new separately authorized Cloud phase. No complete structural unwind acceptance exists yet.
