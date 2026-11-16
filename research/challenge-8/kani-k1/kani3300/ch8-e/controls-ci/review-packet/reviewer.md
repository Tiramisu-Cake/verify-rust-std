# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `0aac16ef62da9e9d5645782d458593e5d78143ba`
- Candidate: `97d7592df3249cd6b697d2e3bcbe36153f80a0e7`
- Candidate tree: `2153f7adee907d6e2c0ab95557f459a4d06edcb2`
- Diff SHA256: `90fc89cd1c147a3fa4c5b4b87aec9f99eeacdc07863505d0b1c3e03cf46ca083`

## Defect

Prepare independent E-Q/E-S/E-H single-file controls and strict bounded CI observation runner; no std builds.

## Applicability

TASK-CH8-E-CONTROLS-W15.md, input g0 7d8ddd22f40a64053de7de13fb23a3f3303bc07a. Design/controls in g0 ch8-e. Prepare only, one stage.

## Invariants
- No tool/model/production Rust change, no push/CI/publication/ledger/local cargo/rustc/Kani/CBMC. Sole control parent upstream0aac, changes only workflow and ch8-e-control, stock workflows removed, skip-ci commit.
- One push-only dispatch, bucket E item1 attempt1; two exact tool pins in matrix, ON/OFF companions default checks intact, independent roots isolate compile errors.
- E-Q must bind exact diagnostic or named false invariant base; E-S no constant CAP or loop mixing, read before loops; E-H actual live-byte writes, inside initialized witness/hole, outside false bit and initialized sentinel, real write/copy without unchecked shadow summaries.
- Exact source/tool/request/selection/config identities, cwd normalization and sibling control/tool layout; runner context step env only, fetch depth>=2.
- 600s harness,660s invocation,6GiB process group,75min phase/pin,120min job/pin,one build/pin,no retries. Retain original exit/exception/signal and partial export/head+tail, do not count unrelated failure as negative.
- UNKNOWN/NOT_RUN preserved for setup/missing/null/wrong-type/timeout/resource/partial/mismatch; covers IDs need source runtime correlation, no proof credit; fallback preserves original receipts and excludes target artifacts.

## Required controls
- Synthetic success/error/timeout/partial/missing/null/wrong-type/explicit NOT_RUN/source-stage-target mismatch, original exits/exception preservation, cover/named negative binding, host/ref/attempt/pin/hash guards, YAML/actionlint.

## Declared dependencies
- `.github/actions/setup/action.yml` → `dependencies/0000.bin` (mode 100644, SHA256 6ee9af29eb091ce92cb819deb205f1f07895e8bbdb02d0c5e510de85025dc307)
- `scripts/kani` → `dependencies/0001.bin` (mode 100755, SHA256 28a81c48fd72627ed2449993730636bc830abeffeaea4d85d9297b2ec4393af2)
- `scripts/validate_json_export.py` → `dependencies/0002.bin` (mode 100755, SHA256 af2a207bafbe4fd66254d40a0c022bfa4b51a76a426aedfc9f27ed14388e8b7d)
- `tests/json-handler/schema-validation/kani_json_schema.json` → `dependencies/0003.bin` (mode 100644, SHA256 e687c3af91544431c84071e1b5105682ae4f93c0dc191d03e8a545e375807670)
- `kani-driver/src/frontend/schema_utils.rs` → `dependencies/0004.bin` (mode 100644, SHA256 6cf7b1311b3ebfd6ec1ce61efb1875b33d067fc2a89d2e7d1ccf8bf6995b1a64)
- `kani-driver/src/call_single_file.rs` → `dependencies/0005.bin` (mode 100644, SHA256 3fc27b10a1db7705b514e7689e9c6e6b2f20516066664ad799b32f4adc23c996)
- `library/kani/src/arbitrary.rs` → `dependencies/0006.bin` (mode 100644, SHA256 f74cec2acfdf62dd5300f2d0d92d8ffeb11d6053cc270de41e4aeacc68ac03c9)
- `kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs` → `dependencies/0007.bin` (mode 100644, SHA256 ad73c82580f8f9ba3528ce9b6b371c6a4f717443e31a86b1fad6bad0a2c80d64)
- `tests/ui/quantifier-safety-checks/exists_ptr_add_uninit.expected` → `dependencies/0008.bin` (mode 100644, SHA256 6a5bcf766b585fa097640ada5f1fdd3234417f106b8207b6408a25f30fc9b03a)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No runtime proof/compiler outcome measured, all40 invocations NOT_RUN, old STOP E remains. Exact generated check/cover/runtime binding and actual core storage bridge remain unestablished.
- SEL1 tool source is separately pinned14bc57fdb99960240c4944845a3d985c8af4dcf7/tree1efb6e4dfa69d346df8e23741d11839b1932403d. Export schema_utils/validator/template are byte-identical to upstream.
- Full worst-case sweep not guaranteed: phase envelope stops unstarted rows as NOT_RUN. Solver/MIR option precise stage and per-process timing not independently bound.

Do not execute source or evidence from this packet. Do not claim new proof credit.
