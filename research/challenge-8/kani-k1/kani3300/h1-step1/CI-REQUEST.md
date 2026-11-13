# Coordinator request — H1 STEP1 preparation only

Worker15 does not push or dispatch. Cloud$0. No local compiler/verifier/build was run.
The owner authorized the listed STEP1 experiment; the coordinator must approve final
caps and the exact final CI HEAD before its single push. This file is not a trigger.

Selected matrix is exactly10 normal singleton invocations: C12 P1/P2, D10 P1/P2,
B14 P1/P2, A16 P1, F12 P1 no-slice, H16 P1 arrays-uf-always, E8 P1. Maximum normal
CBMC wall budget is10×300s=3000s=50min; the300s watchdog also covers normal Kani
compilation/setup after tool identity validation, so solver time is no larger.
No repeats, adaptive retries, G16 substitution, historical A16 reuse, P2@8 or other
arms are selected. E8 is included; insufficient capacity is inconclusive, not failure.
A coordinator decision to omit/substitute any arm requires an updated request/matrix
and final reviewed candidate before push; this package makes no automatic substitution.

Build exactly4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c/treeaf28e22ec446b254cfa3a28b2882eafa58d5a458
in a separate clean source checkout, never the CI overlay. One normal release bundle
build uses `cargo bundle -- h1`; no production source/test/golden patch is applied.
Stock CBMC6.11.0 comes from the pinned source's kani-dependencies/install script on
ubuntu-22.04 x86_64, with cadical selected by normal Kani. Version, binary, compiler,
sysroot file hashes and exact source/CI/input identities are retained and checked.
Do not substitute ZST/develop/profiler CBMC or any source fix/initializer skip.

Commands executed by CI only:

```sh
python3 ci-overlay/ci/h1/runner.py phase evidence/build/setup 1500 6291456 bash ci-overlay/ci/h1/setup.sh source
# working directory source:
python3 ../ci-overlay/ci/h1/runner.py phase ../evidence/build/build 6600 6291456 cargo bundle -- h1
# after bundle identity binding and artifact download:
python3 ci-overlay/ci/h1/runner.py case "$CASE_ID" tools/kani-h1 evidence/case
```

Normal command, exact file/root chosen from MATRIX.json:

```sh
RUSTFLAGS='--edition 2021 -D warnings' kani-driver INPUT --harness ROOT --exact --keep-temps \
  -Z uninit-checks -Z function-contracts -Z unstable-options --output-format=regular --verbose \
  [--no-slice-formula] --cbmc-args --object-bits N [--arrays-uf-always]
```

Brackets indicate only the fixed F12/H16 choices, not shell syntax. Two argv tokens
`--object-bits N` suppress Kani's default16. No `--object-bits=N`, duplicates or last-wins.
No-slice is before --cbmc-args; UF is after. Exact backend argv is checked against
4f64 call_cbmc.rs before spawn, including default checks and cadical; drift refuses
rather than changing flags. Unwind/property selection remain normal defaults.
Kani4f64 uses NoMultithreading/default1 for regular output; explicit --jobs1 conflicts
with regular and is deliberately omitted. Workflow max-parallel1/fail-fastfalse and
one exclusive normal.lock per singleton enforce one CBMC at a time. One shared bundle
is reused without solver replay; source/root paths stay constant per root across arms.

Proposed caps (coordinator approval required before push): build job150min; source
setup25min, build110min, remaining15min for checkout/package/capture/upload. Per-case
watchdog300s/RSS6291456KiB, raw2s process-group sampling, TERM then2s KILL/cleanup.
The singleton job proposal is25min, with checkout/download/upload step caps3min,
setup480s (9min outer), normal+capture8min outer. These final proposed caps are
recorded in CI-MANIFEST.json. The hard job envelope is150+10×25=400min, including
reserved setup/artifact time; it is not a grant to consume that time. Read-only
postprocessing has two distinct30s/1GiB goto-instrument projections; no extra solver
is invoked. Missing projection/binding stays UNKNOWN. First-CNF, all numbered rounds,
initial phase events and final status are saved separately; conversion time is only
reported if actually observable, otherwise UNKNOWN.

Capture caps per stream:4MiB prefix plus1MiB independent final tail; full drained
stream byte count/SHA256 and completeness retained. CBMC JSON object cap16MiB,
20000 properties,4096 phase events/rounds,4096 characters per event; caps/truncation
force UNKNOWN. Original CBMC exit/signal, Kani/time-wrapper exit/signal, parser,
watchdog and job statuses remain distinct. time-v maxrss and sampled aggregate RSS
are separate KiB fields. Metadata≤32MiB total/16MiB per file; exact spawn GOTO copied
only if≤128MiB, always hashed. Projection selected contexts≤200 each/2048 bytes per
line plus bounded neighbors. No unbounded formula dump or full-suite run is requested.
Artifacts upload with always(), including build error and normal watchdog kill; root
outcome initializes NOT_RUN even when build/setup prevents the solver stage. Hard
runner loss/job cancellation may prevent artifact completion and must remain UNKNOWN.

Coordinator-only trigger after final caps approval: from /root/kani-fix-3300-h1-ci,
verify CI-MANIFEST HEAD/branch, clean status and exact source parent; push only the
final HEAD to `origin uninit-ci/h1-resource-20261113` in Tiramisu-Cake/kani. That exact
branch-filtered push starts the sole workflow. No workflow_dispatch trigger, inherited
workflow matrix, intermediate push, rerun or GCP build is authorized by this package.
Apply ORACLES.md and Evidence Brief/reporting restrictions after CI; full raw artifact
archives/logs are not an ordinary agent evidence interface. No proof credit is awarded.
