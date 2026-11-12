# Coordinator-only D1-P execution request

SOURCE_READY/NOT_COMPILED; this preparation is not dispatch authorization.
Worker Cloud $0, no local builds/verifiers, Kani push0, dispatch0, proof credit0.
Local clone `/root/kani-fix-3300-d1p`; exact CI commits/parents/trees/full-index
patch hashes and production tree identities are in DIAGNOSTIC-MANIFEST.json.
Both commits are neutral and unpushed. Do not stack the patches. Transport and
CI are exclusively coordinator-owned, under existing admission/budget controls.

After admission, publish the two exact CI commits. On one published ref manually
run `.github/workflows/kani3300-d1p.yml`, supplying BOTH full SHA inputs:

```bash
gh workflow run kani3300-d1p.yml --repo Tiramisu-Cake/kani \
  --ref diagnostics/kani-3300-d1p-r1-skip \
  -f r1_ci="<manifest r1-skip CI SHA>" -f r6b_ci="<manifest r6b CI SHA>"
```

The workflow has only workflow_dispatch, a repository-wide D1-P concurrency
lock, serial r1-skip then r6b jobs (second may collect after first failure), and
one actual symex CBMC at a time. No automatic retries. Both exact checkout
parents/trees, fixture hashes and allowlisted diff are checked before setup.
P1 root postcondition_reads_initialized_return, both pins, original fixture
fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b.
P2 is frozen but OFF, with no activation input. Coordinator may only commission
P2 A+B-lite after BOTH P1 captures complete cheaply (no caps/60s/2GiB); no
normal P2 solver belongs to this stage. No source rewrite/covers or root rename.

Actual runtime Kani command is recorded as a JSON array, with RUSTFLAGS
`--edition 2021 -D warnings --emit=mir`, m2br crate, singleton --exact,
`-Z uninit-checks -Z function-contracts --output-format=regular --keep-temps`.
Diagnostic additions only: `-Z unstable-options --cbmc-args --program-only`.
Driver supplies actual checks/solver/target/object-bits/slicing/defaults. CBMC
and goto-instrument must report 6.11.0. Version/hash are saved before wrappers;
wrapper calls the resolved real executable once, keeping its actual JSON argv.
No normal invocation is executed to obtain argv, inventory or a successful tail.
Kani JSON parser may reject plain program-only text; record this as its own
pipeline failure, never rewrite JSON. Missing actual spawn => stop attribution.

Limits: symex 60s, RLIMIT_AS 2097152 KiB and sampled process-tree RSS 2097152 KiB;
one stock --program-only invocation per P1/pin. Case envelope 300s / sampled
2097152 KiB. Read-only goto-instrument symbol/function views: 30s/2097152 KiB
each, separate paths for pre/post/actual. Setup reuses the existing scripts/submodule recipe, captured per subphase
(1200s/12582912 KiB). Build 5400s/12582912 KiB, job120min.
Sampling0.05s; Linux child-subreaper and group cleanup cover owned and orphaned descendant sessions. Shared RSS may
be double counted and short peaks missed; hard CBMC AS ceiling is separate.
Historical cutoff6291456 KiB/2s/300s is context only. RSS/maxrss KiB; GiB divide
by1048576. time-v maxrss UNKNOWN; wait4 and sampled maxima separately labeled.

Caps: stdout/stderr <=8MiB/phase/stream; binary snapshots <=64MiB each (oversize
STOP completeness); failures <=2MiB with explicit cap; projections <=16MiB
(actual selected records <=200 lines, each <=2048 bytes); summary top30 roots,
<=200 lines for curated display. Parser: input8MiB, line65536bytes,
100000records, 200000character-work units, 5s/view, JSON depth64/100000objects.
No VCC/byte-op second view requested. No full-slice/property narrowing/arrays-uf,
DIMACS/solver stats/patch CBMC or unbounded expression traversal.

Artifacts: `d1p-<pin>-<run>-<attempt>` includes identity/build receipts;
`<sourceSHA>/P1/<root>/` contains invocation/tool/version records, per-actual-
spawn receipts and bounded streams, pre/post/exact-input GOTO snapshots and
SHA receipts, snapshot link, stock views/selected projections, ssa-summary,
failures, <=200-line summary.txt, independent first/final milestone records and phase status.
--keep-temps work stays outside the artifact tree; uncapped compiler files are not uploaded. ARTIFACT-MANIFEST.json binds files/bytes/SHA256.
Uploads run at always() after setup/capture failure/kill. Native upload failure
remains visible; separate `d1p-<pin>-upload-status-*` records first-upload outcome.
Manifest covers bounded evidence, not historical raw logs. No old raw/GCS reads.

verification=NOT_RUN; failure inventory=NOT_RUN/UNKNOWN, total failures UNKNOWN.
Diagnostic completion is not verification SUCCESS. Any setup/collector/kill/
timeout/parse/tool/upload error stays failure/incomplete. Parser completeness
and semantic verdict completeness are distinct. Unknown widths/Layout/owner,
source target/write/guard/PC/property and feasibility are not reconstructed from
scalar P1; inspect bounded projections in separately commissioned D1-A. An
unidentified offender is a valid diagnostic result. M3 and full gate remain open.
