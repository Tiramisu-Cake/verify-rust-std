# Reproduce standalone candidate L

Base `0a83dba42db7ce0b445034ece5298afe980e57dc`; candidate `095ef553e92deaae063b3684ea3172128e666785`, tree `54e80209593942d1381283f71fa916c02fa4ac57`. Tool compiler/spec/exporter/refiner are from that clean base+one binding+tests; no C3/native/ZST/FRAME patches. Rust nightly-2026-09-25, expected compiler commit f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f. Exact dependency URLs/digests/environment are in the runner and Cloud receipt.

Executed Cloud command from own proof worktree:

```sh
python3 research/challenge-8/cloud-build/control.py \
  --state-dir .verifast-slice-upstream-l-state \
  --phase-id VERIFAST-SLICE-UPSTREAM-CLOUD-2026-10-11-L \
  --ledger research/challenge-8/cloud-build/verifast-slice-upstream-l/BUDGET.json \
  --owner verifast submit \
  --infra-sha 6c663c1d44bc679e0c43635ef5868cf41370141d \
  --proof-sha 6c663c1d44bc679e0c43635ef5868cf41370141d \
  --lane verifast-slice-upstream --timeout 1740
```

This session ledger must stay CLOSED after completion. A future Cloud execution needs its own authorization/account/phase registration; do not reopen this historical ledger. Source transport delivers the exact base-prerequisite tool bundle and verifies head/tree/files before building. Dependency/toolchain installations and all builds/proofs run only in Cloud.

Focused commands in the prepared Cloud candidate, from tests/rust/safe_abstraction:

```sh
../../../bin/verifast -dump_ast_with_locs positive.ast slice_as_mut_ptr.rs
../../../bin/verifast slice_as_mut_ptr_no_init.rs  # diagnostic: expected exit1/read VC line8
```

Normal upstream Linux suite, including tests/rust/testsuite.mysh:

```sh
cd src
make test NUMCPU=4
```

Baseline control rebuilds exactly the base translator with unchanged candidate test bytes, invokes the positive, retains error and binary digest, restores the exact candidate translator and checks tracked diff empty before candidate build. Baseline diagnostic credit requires the raw missing method error. Negative credit requires the raw initialized-read heap-chunk diagnostic at line8; exit1 alone is insufficient. The POSIX case registration enforces that expectation without allow_should_fail or allow_dead_code.

No Challenge8 proof suite is executed or pins changed. No upstream PR/public fork/upstream publication performed. Separately authorized infrastructure PR8 was merged only in the proof fork. Other platforms and optional Rocq/Java-server/private assignment suites remain subject to the explicit receipts.
