# Step 3 — live v4 switch: exact commands (NOT PERFORMED)

Run each command once. Stop at the first error. Never force-push. Before you start, confirm again that nothing is happening: no `control.py` process, `requests/` empty, `active.json` reservations `[]`, no dirty staged files in either client.

```bash
SRC=/root/verify-rust-std-networks/research/challenge-8/network/cloud-readiness/client/coordination.py   # sha256 2fa7affd…bc3
P=research/challenge-8/cloud-build/coordination.py

# Select (only this path; foreign dirty files stay)
cd /root/verify-rust-std-select-night && git rev-parse HEAD   # baseline: b96f16bef8c9fe1bb0ac761f3094fd3b618c9b30
cp "$SRC" "$P" && git add -- "$P" && git commit -m "coordinator v4 adoption: shared coordination.py" -- "$P"
git push origin research/night-select-sort4-cloud-2026-10-09

# Merge (push includes its 15 local R19 commits, owner decision 2026-10-22)
cd /root/verify-rust-std-merge-origin && git rev-parse HEAD   # baseline: 0c0b48f219bcaefb14e356fac2d21817ccd9ab44
cp "$SRC" "$P" && git add -- "$P" && git commit -m "coordinator v4 adoption: shared coordination.py" -- "$P"
git push origin merge/incoming-origin-20261009
```

Network is already committed and published: baseline `b55a9e59abb6f07f49d93f9c5afc77dede2493b3`, adoption `4876c66f42edb9e95d7c9f4de6cb322a05d09c6a`.

ACKs go in this directory, one per owner: `{owner, branch, coordination_sha256, control_sha256 (sha256 of installed cloud-build/control.py), infra_commit (adoption commit), baseline_control_commit}`. Then run the transition from the prepared client directory, so that `HERE/coordination.py` is the candidate:

```bash
cd /root/verify-rust-std-networks/research/challenge-8/network/cloud-readiness/client
A=../../coordinator-v4-adoption-20261022
cp /root/smallsort-ci-coordination/active.json $A/before.json
ARGS="--client select-sort4=/root/verify-rust-std-select-night --client merge=/root/verify-rust-std-merge-origin --client network=/root/verify-rust-std-networks --ack select-sort4=$A/select-sort4-ack.json --ack merge=$A/merge-ack.json --ack network=$A/network-ack.json"
python3 -B coordination-v4-transition.py audit $ARGS
python3 -B coordination-v4-transition.py migrate $ARGS > $A/MIGRATE.json   # one read-only `gcloud builds list --ongoing` under the lock
cp /root/smallsort-ci-coordination/active.json $A/after.json              # expect {4,3,[]}
```

Readback for each client: import that client's own `cloud-build/coordination.py` and, under `locked()`, check `protocol() == (4, 3)` and `reservations() == []`. Write the result to `READBACK.json`. Do not run `control.py status` without an owner and ledger: it uses a default ledger and state directory and may write to them.

Rollback, only while there is no network reservation or request:

```bash
python3 -B coordination-v4-transition.py rollback
```
