# B3 T1: CI-only deterministic model comparison

2026-11-15. Separate B3 T1 stage, not C2. Preparation only; no local toolchain execution,
push, CI, PR or issue. Task base t0 `e43468e6560de65ca0cc7292d56cec515076c7a4`.
The task's nine requirements override the auditor's earlier `--only-codegen` proposal
and stronger resource/harmlessness interpretations. Nothing here establishes proof credit.

## 1. One runner and three fresh arms

One `ubuntu-24.04` job. Checkout has full Git history in `$GITHUB_WORKSPACE/source`.
Before switching revisions, copy `.github/b3-t1` to `$RUNNER_TEMP/b3-t1`. Both runner
and comparator run there. A1/B1/A2 check out, respectively:

- A: `0aac16ef62da9e9d5645782d458593e5d78143ba`.
- B: `3d9a1809388f74c62ea9fb7320e123db0b8b37fa`; assert parent = A.
- A again, rebuilt from scratch.

Source absolute path is constant. For each arm delete source `target/`, `build/`
and `t1-control/`, including the compiler, sysroot, build-tools and per-row Kani
caches. Registry/download caches remain dependencies, not generated models.
Stock compiletest additionally cleans each per-row target. Paths differ between
rows exactly as stock perf specifies, and are identical for each row across arms.
No A1 output is reused as A2 output. Evidence copies live outside source.

## 2. Exact workload, selectors and features

Each arm runs **unmodified `bash scripts/kani-perf.sh`**: release
`cargo build-dev -- --release`, overlay copy, then
`cargo run -p compiletest -- --suite perf --mode cargo-kani-test --no-fail-fast --timeout 2400`.
`RUST_TEST_THREADS=1`, as the upstream perf job. No filter or feature override.
Only A1 has an initial release bootstrap to resolve/download build-std dependencies;
the subsequent stock-script release invocation uses those same binaries/flags.
B1/A2 build from a deleted target. No other Kani source changes are applied.

Source justification (all references at A; these sources are identical at B):

- `scripts/kani-perf.sh:11-43`: release, overlays, suite, mode and timeout.
- `tools/compiletest/src/main.rs:376-435`: a Cargo manifest plus `expected` or
  `*.expected` creates a row. Manifest directories terminate recursion.
- `tools/compiletest/src/runtest.rs:323-344`: `cargo kani --target-dir <clean-row-target>
  --tests`, package working directory as selector. All 15 files are literally
  `expected`, so **no `--harness` selector** is added.
- This mode forwards `config.extra_args`, not `.rs` header flags. Stock extra args
  are empty. `hashset` activates stubbing through package metadata in Cargo.toml.
  Cargo package defaults, `cfg(kani)`, test selection and s2n source solver/unwind
  attributes are preserved by executing that exact path. Three expected overlays
  plus the checksum source overlay are copied by the stock script.
- `tests/perf/string/expected` has no manifest; `kani-lib/arbitrary` has no expected
  file. Neither is a row. Replacing the suite by arbitrary `cargo kani --tests`
  commands would lose this contract and is not done.

The exact row set is checked against `common.PERF_ROWS` at capture and comparison:

| Package selector under tests/perf | Harness selector | Extra feature/CLI flags |
|---|---|---|
| btreeset/insert_any | all generated test/proof harnesses | stock defaults |
| btreeset/insert_multi | all | stock defaults |
| btreeset/insert_same | all | stock defaults |
| format | all | stock defaults |
| hashset | all | package metadata: unstable stubbing |
| misc/array_fold | all | stock defaults |
| misc/display_trait | all | stock defaults |
| misc/struct_defs | all | stock defaults |
| smol_str | all | stock defaults; dependency =0.2.2 |
| vec/box_dyn | all | stock defaults |
| vec/string | all | stock defaults |
| vec/vec | all | stock defaults |
| s2n-quic/common/s2n-codec | all | original package/cfg/attributes |
| s2n-quic/quic/s2n-quic-core | all | original package/cfg/attributes |
| s2n-quic/quic/s2n-quic-platform | all | original package/cfg/attributes |

Names/counts are collected from generated `*.kani-metadata.json`, not guessed from
`#[kani::proof]` source text. Every metadata harness must have exactly one final
capture, bound through `goto_file` and `ArtifactType::SymTabGoto -> Goto`.
The complete per-row pretty-name census, raw metadata, actual argv and exits are
artifacts. Missing, duplicate, ambiguous or partial census is invalid.

Pinned unchanged blobs: perf tree `30fb619478d5086f383b7148772290007c2582ce`;
perf script `d2bb43fb97bb2c8b90601c05586e8f998543f9c7`;
toolchain `4edc84573b03d2b923d584f5df144274c435f693`;
dependency versions `177eb685db5011ad9066f5891b74146d38d40a72`;
s2n gitlink `be829a473881163369f7df4c739232ebbd1e7d27`.

## 3. Actual CBMC input, without SAT

`kani-driver/src/main.rs` returns on `only_codegen` before `check_all_harnesses`.
`harness_runner.rs` instruments each linked model (including contracts/DFCC) before
`check_harness`; `call_cbmc.rs::run_cbmc` finally invokes PATH `cbmc` with that model.
The CBMC shim snapshots the exact model **at that invocation**, including actual
argv/cwd and SHA256. It never delegates to real CBMC. Kissat is also blocked.
The real backend versions/hashes are collected before installing PATH shims.

The shim emits valid JSON containing an ERROR message, no result/prover status,
and exits **86**. Kani records a failure and continues its default all-harness loop;
stock perf does not request fail-fast. Kani exit **1** and compiletest/script exit
**101** are expected capture-only outcomes, explicitly journaled, never changed to
success. Any other exit or incomplete census is invalid. No fake verified property
or successful proof is emitted. No `|| true`; orchestration has no pipelines.
Stock helper text pipelines do not carry model/backend commands; those commands
are independently journaled by the wrappers with their original exits.

The cargo wrapper preserves all original Kani arguments and only appends
`--keep-temps`, which changes deletion in `KaniSession::drop`, not model generation.
Stock compiletest prepends scripts/debug to PATH, but neither shadows `cargo` or
the backend shims. `cargo-kani` still dispatches to the original driver script.
The cargo alias is expanded exactly to permit Cargo's own `--locked` placement.

The goto-cc wrapper delegates to the real binary and records original exits. After
successful linking, before per-harness specialization/instrumentation mutates the
`.out`, it copies linked `*.out` and input `*.symtab.out`. Specialization calls
(`--function`) are not mislabeled as linked inputs. goto-instrument calls also
pass through with argv/exit journaling. SHA256 is recomputed from every captured
file before comparison; coordinates alone are not used as binding evidence.

## 4. Locks and provenance

A1 alone may resolve/download dependencies. Its initial release build materializes
the workspace/build-std dependency set; each of the 12 standalone perf roots and
the shared s2n workspace is then resolved once if its lock is absent, and fetched
with `--locked`. Preserve the existing root and compiler locks. Freeze all 15 lock
paths (workspace, compiler, 12 perf roots, shared s2n root), including gitignored
s2n Cargo.lock. Save bytes and SHA256 outside the source tree.

All measured arms, including A1 after bootstrap, run with `CARGO_NET_OFFLINE=true`
(Cargo's environment equivalent of `--offline`) and `--locked` on actual PATH
Cargo build/run/rustc/metadata/fetch calls. Kani's metadata library can invoke its
compile-time absolute Cargo path; it still inherits offline mode and is covered
by lock byte/hash checks before/after the workload. B1/A2 restore the frozen A1
locks after checkout and must match exactly. Any lock drift invalidates the arm.
Rust-src locks are saved separately and must remain unchanged across all arms.

Artifacts record paths and SHA256 for rustc, actual toolchain Cargo, kani-driver,
kani-compiler, cbmc, goto-instrument, goto-cc and kissat; rustc -Vv for each arm,
real cbmc --version, Rust sysroot locks, runner ImageOS/ImageVersion, OS/kernel,
MemTotal (meminfo), nproc and df. Cadical/minisat are embedded in CBMC, so their
binary identity is the recorded CBMC SHA256. No memory-performance inference.

## 5–6. Comparison and A/A precedence

Compare logical names, not artifact copy filenames. First A1/A2 indexes, actual
bytes, inventories, argv/cwd, locks and tool identities; only then A1/B1. For B,
compiler/driver binary hashes may differ, backend identities may not. All changed
common model records produce symbol-table dumps followed by function dumps using
the recorded real goto-instrument, and unified diffs in artifacts. These are
display operations and do not solve SAT. Missing names and provenance differences
are reported as invalid, never silently intersected.

A/A mismatch is INCONCLUSIVE_AA: classify names, hashes, provenance and text dumps;
no B3 conclusion. There is **no normalizer**. Any later normalization requires a
separate explained field policy, zero A/A differences after normalization and a
still-sensitive control. No byte/path stripping is silently introduced.

## 7. Positive control and mandatory structural gate

`.github/b3-t1/reproducer.rs` is byte-identical to B's
`tests/expected/zst-union-arm/main.rs`. Copy the same bytes to the same absolute
`source/t1-control/main.rs` in all arms and run stock single-file Kani selecting
`array_typed_copy`, with keep-temps. It uses the same linker/backend shims,
metadata binding, hashes and symbol/function diff comparator as perf.

The expected result is A1=A2≠B1, specifically the `ArrayUnion::zst_array`
`tag-<union>::<arm>` zero-width wrapper payload type `[(); 2] -> Unit`.
If no control model differs, INVALID_CONTROL. A detected hash difference alone
does not establish that shape: the comparator deliberately returns exit **3**,
CONTROL_WRAPPER_REVIEW_REQUIRED, until the coordinator/auditor examines the
saved symbol and function diffs and confirms that exact change. This is a
required result-admission gate; a red capture job with complete artifacts is
not proof failure or successful T1. Off-wrapper control changes invalidate T1.
No old-base compiler is built, and no control is accepted merely because it differs.

## 8. Interpretation

See RESULT-template.md. Equality means only no model differences in this precise
perf profile, after positive-control admission. Zero-width-wrapper-only changes
are a census for the coordinator; they affect byte operations and are not
automatically harmless. Other changes contradict auditor §3: do not submit PR.
No claims about resource regressions, runner loss, B1/B2 proof or SAT outcomes.

## 9. Caps and partial evidence

240-minute job cap, 225-minute capture step including installation, no retry.
Run attempts other than 1 are rejected. `always()` upload includes setup, per-arm
logs, command-start/exit/exception events, real argv, model bytes/hashes, metadata,
locks, binary identities, symbol/function diffs and RESULT.json/INCOMPLETE.json.
Console output is bounded stage/status text; large logs and dumps go to files.
Timeout/missing artifacts/runner loss remain INCOMPLETE; never infer NOT_RUN from
absence of text. The recorded shim events explicitly establish SAT NOT_RUN for
captured invocations. Synthetic Python tests cover normal capture, wrong binding,
missing/null/wrong-type/partial/duplicate inventory, original errors/exceptions,
comparison drift, no-sensitive-control, and dump failure/timeout.
