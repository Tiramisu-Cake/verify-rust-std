# W0-A1 — coordinator-only R1/R2 request

Runtime NOT_RUN. Prepare-only request; no push, remote branch, non-skip trigger,
workflow dispatch, PR or Cloud build is authorized to this worker. Cloud $0.
Package SHAs/trees and patch/checksum identities are in CI-OVERLAY.json; executable
request is ci/CI-REQUEST.json. Std source package is separate from the CI-only package.

Coordinator reviews the local packages, then creates a **same-tree non-skip child**
of the CI package on a fresh matching fork branch. The package itself has `[skip ci]`.
Push trigger is the accepted mechanism; workflow_dispatch is absent. First attempt
only; both checkouts depth2 and persist-credentials false. No automatic retries.

| Dispatch | Branch prefix | Matrix and sequence | Maximum envelope |
|---|---|---|---|
| R1 | `uninit-ci/ch8-w0-a1-r1-*` | Eight SEL1 ON roots, three N32 first; fail-fast false, max-parallel1/jobs1 | 8 × 60 = 480 runner-min |
| R2 | `uninit-ci/ch8-w0-a1-r2-*` | Baseline then SEL1 jobs, max-parallel1; six separate native invocations serially per pin | 2 × 90 = 180 runner-min |
| R3 | No prepared trigger | Only coordinator decision after R1/R2: one fixture/wiring fix OR one C2 attribution comparison | Reserve unused |

Each invocation has an external600s cap covering driver/codegen/backend and embedded
harness timeout600s. R1 permits at most39min before invocation to retain10min upload reserve.
R2 permits at most19min setup/build to retain60min verifier envelope plus10min upload reserve.
At cap or missing evidence, keep original exits/signals and report the first named blocker.
Prepared independent rows may finish; no new variant/retry is authorized.
Setup failure is counted by the coordinator as a started dispatch, not reclaimed.
A1 cap3 is inside item1 cap18; item2 cap14 is separate, total≤32. Worker changes no ledger.
The coordinator schedules alongside S1/S2; this workflow reserves no CI priority or slots.

The optional single OFF N32 companion is deliberately absent from this first ready package.
After R1 identifies the heaviest complete/capped sample, the coordinator may request a
reviewed exact-delta addition: same fixture/std/root/panic scope/checks/object-bits/unwind,
only the uninit flag removed, one ≤60min job. R2 without this optional job is180min;
with a separately prepared OFF addition its upper envelope would be240min. No arbitrary
choice before R1, solver sweep or hidden flag change.

Control and export are siblings at workspace root. Setup uses frozen export's own
`.github/actions/setup` and `kani_dir: export`; build cwd is export. The wrapper is
loaded from control, but std child cwd is a separate RUNNER_TEMP checkout and `./library`
resolves there; binary is absolute export/scripts/kani. Native cases use separate
isolated input cwd/hash, and never invoke verify-std. No Cargo.toml surrounds either checkout.

Both source pins use their own frozen nightly-2026-10-23/CBMC6.11.0/Kissat4.0.1 setup.
Ubuntu z3 is the distribution package; `Z3_VERSION=5.3.1` is macOS-only and is not an
Ubuntu solver pin. Actual dependency versions/binary/runtime/sysroot hashes must be observed.
No backend/toolchain upgrade or compiler/runtime edit is included.

RSS policy: record available RAM and a2GiB OS reserve once before setup for the entire job; freeze
threshold available-minus-reserve and kill the group at the threshold. Record driver,
backend and process-group simultaneous-current RSS samples separately from wait4 ru_maxrss.
Do not sum distinct peaks as simultaneous usage. TERM→5s grace→KILL bounds the full group.
stdout/stderr each≤32MiB; metadata≤16MiB/job; upload artifacts≤256MiB/job. Truncation is
INCOMPLETE/UNKNOWN; fallback receipts and upload use always(), retention7d. No global RLIMIT_FSIZE.

R2 original source bytes and reported commands are in ISSUE-REPRO-MAP.md/native/MANIFEST.json.
Both pins receive identical fixture/mode/env additions. #4854 preserves original autoharness,
sanities, duplicate uninit flags and edition/cap-lints; its RUSTFLAGS never enters setup/std.
Standalone output/cap/export additions are recorded; no cargo workspace or --target-dir
is invented for native standalone commands. Each case has an independent parser/output.

Acceptance after future CI requires complete per-row events, source/fixture/body binding,
failed properties and useful statuses, return/readback/frames and unwinding checks. Export
JSON object or exit0 alone grants no proof. #5020/#5151 SUCCESS on candidate is MISSED_CHECK/STOP;
#4854 no crash plus Unsupported is diagnostic improvement only. Frozen baseline non-reproduction
is BASELINE_NOT_REPRODUCED; no silent older-pin substitution or C2 attribution. See RESULT.md.
