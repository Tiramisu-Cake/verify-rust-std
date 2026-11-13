# Coordinator handoff — no dispatch authorization

Worker14 prepared source `0beeb6b79efb72b88035e2b747aa889e9b1cb4d4`, tests-only
from exact `ee2695e5a2c4c2d8ead7a511e0f3f6f2a9a95677`, in
`/root/kani-fix-3300-lawful-oracles`, branch `fix/kani-3300-lawful-oracles`.
No push, CI, workflow overlay, coordinator state/budget changes or Cloud spend.
The earlier H1≤10 authorization is not reused. This is a request for coordinator
review/approved execution, not GO or permission to send builds.

1. Review/compose this test-only delta with the separately owned MARKER-MODES
   candidate; worker14 did not read/integrate its unfinished branch. Record the
   composed source and CI tree/commit, compiler/toolchain/sysroot/CBMC/target,
   source hashes, recipe, wrapper, actual argv/env, resource caps and exits.
2. Existing fmt/build checks first, then Python checker tests:
   `python3 tests/json-handler/uninit-contract-oracles/test_checker.py`.
   Build failure leaves semantic stages NOT_RUN. No new runner or interceptor.
3. Run precisely the eight input/root pairs in CONTROL-MAP/ORACLES, separately
   at b12, singleton solver/jobs1. Proposed per-root300s/6GiB; actual caps, outer
   exec timeout (eight roots plus setup) and total build budget require separate
   coordinator approval. Reuse the existing process/RSS/timeout capture; never
   interpret a timeout, signal or partial/missing JSON as expected failure.
4. Explicitly select the new existing-runner scenario (coordinator CI only):
   `cargo run -p compiletest --quiet -- --suite json-handler --mode exec uninit-contract-oracles`.
   Quick does not automatically select this gate. A green expected suite without
   this exec gate leaves the strong gate NOT_RUN. Do not set exit_code:2 or mask
   its nonzero result. UNKNOWN/FAIL are not negative PASS.
5. After composition use one coherent Quick plus the selected new gates on the
   same identities. Report actual stage counts; do not guess a new total. Full
   platform/M3/SmallSort gates remain outside this task.

The scenario uses existing source files without copying Rust bodies. Each process
has a unique tempfile/export/target directory, exact harness filter, and regular
output beside export.json and invocation.json. Capture the printed artifact
parent through the current CI evidence mechanism, preserving original exits,
input hashes before/after and complete receipts. The command is:

```
RUSTFLAGS='--edition 2021 -D warnings' kani ABSOLUTE_EXISTING_INPUT \
  -Z uninit-checks -Z function-contracts -Z export-json -Z unstable-options \
  --harness ROOT --exact --jobs 1 --target-dir UNIQUE/target --keep-temps \
  --export-json UNIQUE/export.json --output-format=regular \
  --cbmc-args --object-bits 12
```

All flags are before the final backend arguments. Preserve normal checks,
solver/slicing and global defaults. Existing .expected files retain compatibility;
qualification is the structural gate, never substring matching.

Initial inventory capture intentionally ends UNKNOWN/BINDING_PENDING even if
all outcomes happen to match. Retain every failure identity, not only .expected
matches. Review the actual selected regular/GOTO fields, then populate reviewed
bindings and rerun `checker.py --case CASE --directory RETAINED_CASE_DIRECTORY`
against the same invocation. Do not silently auto-enrol observations as oracles.
A subsequent fresh invocation also needs matching same-invocation selected binding
evidence; reference hashes/coordinates alone do not prove causality.

Required selected evidence per root, through current bounded CI capture:

- Complete Run/harness outcome/selection/counters, full failed PropertyExport
  fields (id/class/exact description including type/file/line/status), checks
  partitions, and complete regular property inventory. JSON has no separate
  failed function field; use existing id plus source and regular location.
- P1: callback result returns to the useful outer ensures; exact assertion
  status SUCCESS. Ordinary/PFC legal-pair: useful scalar/array/result/out
  assertions and their selected source/function identities, separately per root.
- Lawful: reached result29/out29/outside41/ensures assertions; source *out write
  and all private main/buffer assignments mapped to their proper frame. No
  source-only private-write admission. Reached nonzero closure Unsupported:
  preserve exact operation/type and STOP, no broadened upvar-layout repair.
- P2: both local Check and delayed CheckRef on the same ensures u8 read, with
  exact IDs/types/core source/callback callsite; reject any third failure.
  Postcondition-hole: independently inspect its own two layers/full inventory,
  not copied P2 IDs/count. Outer negative assertion may be UNREACHABLE.
- Frame: emitted target/property/source mapping of the user *outside write at
  unchanged line22 and successful initialized read/prefix/private writes. The
  historical var_7 is not authority. Clause: requires clause_helper u16 read
  through relay/choose at line22, all generated checks enumerated and no extra
  frame/protocol/Unsupported/validity failure.

Every source/GOTO target and useful-success binding is currently pending.
Artifact integrity/process success/source-reported verdicts are not independent
proof credit; preserve NOT_RUN/UNKNOWN and source-reported distinctions.
