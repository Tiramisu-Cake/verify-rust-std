# Reproduce standalone candidate L

Base `0a83dba42db7ce0b445034ece5298afe980e57dc`; candidate `1ef8474610274bbf9d0652613ac2cabbb1fc476b`, tree `f21bda99968f8dc7fee4de3303768b0ecb4ddf55`. Tool compiler/spec/exporter/refiner are from that clean base+one binding+tests; no C3/native/ZST/FRAME patches. Rust nightly-2026-09-25, expected compiler commit f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f. Exact dependency URLs/digests/environment are in the runner and Cloud receipt.

Executed Cloud command from own proof worktree:

```sh
python3 research/challenge-8/cloud-build/control.py \
  --state-dir .verifast-slice-upstream-l-state \
  --phase-id VERIFAST-SLICE-UPSTREAM-CLOUD-2026-10-11-L \
  --ledger research/challenge-8/cloud-build/verifast-slice-upstream-l/BUDGET.json \
  --owner verifast submit \
  --infra-sha 5ce6304c919cc3aa3f522926b15c4506872926cc \
  --proof-sha 5ce6304c919cc3aa3f522926b15c4506872926cc \
  --lane verifast-slice-upstream --timeout 1740
```

This session ledger must stay CLOSED after completion. A future Cloud execution needs its own authorization/account/phase registration; do not reopen this historical ledger. Source transport delivers the exact base-prerequisite tool bundle and verifies head/tree/files before building. Dependency/toolchain installations and all builds/proofs run only in Cloud.

Focused commands in the prepared Cloud candidate, from tests/rust/safe_abstraction:

```sh
../../../bin/verifast -dump_ast_with_locs positive.ast slice_as_mut_ptr.rs
../../../bin/verifast -allow_should_fail slice_as_mut_ptr_no_init.rs
../../../bin/verifast slice_as_mut_ptr_no_init.rs  # diagnostic: expected exit1/read VC line8
```

Normal upstream Linux suite, including tests/rust/testsuite.mysh:

```sh
cd src
make test NUMCPU=4
```

Baseline control rebuilds exactly the base translator with unchanged candidate test bytes, invokes the positive, retains error and binary digest, restores the exact candidate translator and checks tracked diff empty before candidate build. Baseline diagnostic credit requires the raw missing method error. Negative marked test credit requires the raw diagnostic at the intended dereference; exit1 alone is insufficient.

No Challenge8 proof suite is executed or pins changed. No PR/public fork/upstream publication performed. Other platforms and optional Rocq/Java-server/private assignment suites remain subject to the explicit receipts.
