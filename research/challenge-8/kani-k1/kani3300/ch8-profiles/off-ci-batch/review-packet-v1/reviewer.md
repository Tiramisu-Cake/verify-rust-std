# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `0aac16ef62da9e9d5645782d458593e5d78143ba`
- Candidate: `cb17a0dc0f235e2992ddfcb9a945f633236f0e00`
- Candidate tree: `9d382acfcf8cebb98190694684f6ce439ee42d16`
- Diff SHA256: `7388be5f5b4679f8752e0c76aba1d11ad6d324f7c3abd5accb522cf82ff23d2b`

## Defect

Global kani list and per-row verify-std recompile std. Batch frozen OFF rows by identical cfg/RUSTFLAGS, bind each row from its exported harness entry.

## Applicability

Profiles OFF P-prime source 9fa2f7f977, stock tool 0aac; no Rust source/tool changes. This candidate is a single-parent sibling of prior control. Compare runner delta to prior control 6269319aecfb3328a2cffe8e2779432dbc346322 when useful; packet baseline is exact stock-tool ancestor.

## Invariants
- No push, CI, ledger or local cargo/rustc/Kani/CBMC. Only Git, static parsing and isolated Python synthetic children. No nested delegation.
- Manifest all62 rows, selectors, source attributes/unwind, cfg flags, expected oracles, per-row600s/6GiB/1MiB stdout/1MiB stderr/8MiB export unchanged; source/tool pins/checks unchanged.
- One verify-std per identical cfg/RUSTFLAGS group (53 positive,9 controls); multiple --harness, --exact, --jobs1, --harness-timeout600s, one export; no global list.
- Std compilation once per group; separate900s pre-harness limit and bounded head/tail receipt; full group wall sum(row caps)+compile limited by original8400s phase.
- Group RSS <=min(12GiB, available-2GiB); active CBMC sampled cap6GiB. Exact per-row RSS UNKNOWN. stdout marker routes output for caps, never establishes proof binding.
- Binding and verdict from unique export harnesses[]; name, contract target, automatic generation flag, checks/covers/failed properties per row; group exit cannot substitute for row verdict.
- Kani source location sorting is admitted; consumers only accepted after matching leaf observation in manifest order; failure/timeout/missing/partial/wrong-type/NOT_RUN preserved. Generated frame identity remains independent review required.
- One workflow, attempt1, pinned sibling checkouts, parent exact stock tool; no automatic proof credit.

## Required controls
- Synthetic mixed positive/negative group exit; all62 with two cfg invocations; leaf failure and post-batch acceptance.
- Success/error/timeout/missing/null/wrong-type/partial/NOT_RUN, root/source/stage/target mismatch, duplicate/missing harness, resource caps, compilation deadline and bounded receipts.
- Manifest/request rows/caps/budgets equality to prior control, exact payload hashes, workflow YAML gates.

## Declared dependencies
- `ch8-prof-off-control/manifest.json` → `dependencies/0000.bin` (mode 100644, SHA256 c10f4e49ec65143534bebafec35d59fb7bc1db39f08bfac3d298101b216e1273)
- `ch8-prof-off-control/kani-version.toml` → `dependencies/0001.bin` (mode 100644, SHA256 57d2640bfcac7029ceaf91bfc9e061f57f34fa9944e5929155a4fae528a8c0be)
- `kani-driver/src/project.rs` → `dependencies/0002.bin` (mode 100644, SHA256 55bc8b60644000ede89bcb1bd43f923a5035659314b57e6f9c56884dd38b0627)
- `kani-driver/src/call_cargo.rs` → `dependencies/0003.bin` (mode 100644, SHA256 6801ea256ab3464b72487c8aacc17e5e79920903304aa82d5f02e23d129c6129)
- `kani-driver/src/harness_runner.rs` → `dependencies/0004.bin` (mode 100644, SHA256 4ddabb49fcbc59990e1cce5b6d2985eae33d12724fe1efe2af2534cc4ba0f480)
- `kani-driver/src/frontend/schema_utils.rs` → `dependencies/0005.bin` (mode 100644, SHA256 6cf7b1311b3ebfd6ec1ce61efb1875b33d067fc2a89d2e7d1ccf8bf6995b1a64)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Compilation boundary is conservative first Checking harness after compile+link+first instrumentation, source-reported marker; actual compiler/proof execution NOT_RUN.
- stderr latest stdout marker exact attribution UNKNOWN due to pipe scheduling. Exact per-row RSS UNKNOWN; group peak and sampled aggregate active CBMC cap reported.
- Original8400s phase can interrupt groups before sum of all row worst-case budgets; results then UNKNOWN/NOT_RUN, never assumed pass.

Do not execute source or evidence from this packet. Do not claim new proof credit.
