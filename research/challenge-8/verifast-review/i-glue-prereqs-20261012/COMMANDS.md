# Exact reproduction and evidence commands

Commands are recorded, not authority to dispatch. Compilation/extraction/refiner/
verifier only in the Cloud lane. Local bundle verification and evidence hashing
are permitted. Executed project/infra pins: first1c1be0002fbf91658a6ade6865af1c778685c9a0;
secondfc11cdfc55c29c9d101d24e40c80da65c2721cff. Sources/runner at those exact commits
are immutable, including the first incomplete evidence packaging behavior.

```sh
# Applied only in a disposable Cloud source checkout at f76012fb...:
xz -dc i-base.patch.xz > i-base.patch
git apply --check i-base.patch
git apply i-base.patch
xz -dc tool.patch.xz > tool.patch
git apply --check tool.patch
git apply tool.patch
# run.sh checks full source pins, assembled tree and compiler before building:
cargo build --locked --manifest-path src/rust_frontend/vf_mir_exporter/Cargo.toml
make -C src ../bin/verifast WITHOUT_LABLGTK=yes VERBOSE=yes
# Console fails at the pinned decoder; refiner/proof steps did NOT execute.
```

Run.sh at executed fc11cdfc is authoritative for environment, package/compiler/
decoder pins, exact build flags, assembly and traps. PINS.json hashes that file and
runner.py; fixture-admission.json hashes all exact original/verified sources.

```sh
python3 research/challenge-8/cloud-build/control.py \
  --phase-id VERIFAST-I-GLUE-PREREQS-CLOUD-2026-10-12 \
  --ledger /root/verify-rust-std-i-actual-glue/research/challenge-8/cloud-build/verifast-i-glue-prereqs/BUDGET.json \
  --state-dir /tmp/c8-i-glue-prereqs-20261012/cloud-state --owner verifast \
  submit --infra-sha fc11cdfc55c29c9d101d24e40c80da65c2721cff \
  --proof-sha fc11cdfc55c29c9d101d24e40c80da65c2721cff \
  --lane verifast-i-glue-prereqs --timeout 1000 --source-mode pinned-objects
# Historical command only: closed ledger forbids another submission.
# Run1 used corresponding1c1be000 full SHA and timeout1100.
python3 research/challenge-8/cloud-build/control.py \
  --phase-id VERIFAST-I-GLUE-PREREQS-CLOUD-2026-10-12 \
  --ledger /root/verify-rust-std-i-actual-glue/research/challenge-8/cloud-build/verifast-i-glue-prereqs/BUDGET.json \
  --state-dir /tmp/c8-i-glue-prereqs-20261012/cloud-state --owner verifast \
  download 70085ccc-e0b7-4099-98bb-7d206f2fc635 --output /tmp/c8-i-glue-prereqs-20261012/second-evidence --text-logs
```

The official client reconciled both terminal builds, charged queue/execution,
released reservations, verified downloads and withdrew this owner's request.
Final ledger has active_build=null, unresolved_reservations=[], spendable=0.
Tool bundle contains only additive3commits and requires exact I b6cb276a;
Git apply path additionally supplies full I patch over stock f76012fb. No whole
merge chain is imported. Bundle SHA and executed file hashes are in PINS.json.
