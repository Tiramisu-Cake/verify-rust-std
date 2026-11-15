# B3 T1 request — preparation only

Status: prepared locally, not pushed or run. Independent B3 T1 stage; not C2.
Coordinator alone authorizes and launches the future run. No phase/slot/budget
registration or dispatch has been performed by preparing this package.

- Kani CI candidate: `1c9940c320f6a6e5c2c84f4068cb99a1c52ee64d`, direct parent upstream A
  `0aac16ef62da9e9d5645782d458593e5d78143ba`; diff only `.github/`.
- B compiler source: `3d9a1809388f74c62ea9fb7320e123db0b8b37fa`.
- Research task base: `e43468e6560de65ca0cc7292d56cec515076c7a4`.
- Prepared worktree: `/root/kani-b3-t1`; bundle `.github/b3-t1/`.
- Future trigger: push exact reviewed candidate to `uninit-ci/b3-t1**`;
  `.github/workflows/b3-t1.yml`, one ubuntu-24.04 job, 240 min, no retry.
- Request identity: `TASK-B3-T1.md`, auditor `AUDIT-REPORT-B3-PERF-RU.md`, and
  DESIGN.md in this directory. No SAT, memory experiment or old-base build.

The workload is the original kani-perf.sh release/overlay/compiletest path;
DESIGN §2 proves its 15-row selectors/features equivalence from compiletest
source. No general `cargo kani --tests` replacement is used. The only Kani
addition is retention via --keep-temps. CBMC receives its normal argv and final
instrumented model at the shim boundary, which saves them and exits 86 without
solving. Kani exit 1 and compiletest exit 101 remain recorded.

Before launch, coordinator checks exact remote candidate identity and normal
lane/ownership controls. This request does not itself authorize push or CI.
On completion download the uploaded Actions artifact through the authorized
coordinator workflow, inspect complete indexes and comparison/RESULT.json.
Exit 3 is deliberately pending structural control review, not a success status.
Confirm control A1=A2≠B1 only in the expected zero-width wrapper, then apply the
RESULT-template interpretation. Any incomplete census, lock/tool drift, missing
artifact or A/A difference blocks B3 conclusions. No automatic retry.

Local validation is Python/static only. See VALIDATION.md for exact checks and
independent review record. No compiler execution or CI evidence exists yet.
