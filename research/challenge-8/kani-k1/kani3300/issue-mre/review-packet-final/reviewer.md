# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `0aac16ef62da9e9d5645782d458593e5d78143ba`
- Candidate: `d860e30592bc05cad1e8f10f814397b8dfd36a33`
- Candidate tree: `ba4b7298f099b2273df90b5a0f8e07826e661078`
- Diff SHA256: `0d23185d87f6f267e338d6c0df4e1b391dde92683bca66ba6f33fcd50b4ea9ee`

## Defect

Delta review: RUNNING receipt must preserve exact resolved argv and export path before execute so hard interruption fallback retains invocation identity.

## Applicability

TASK-CH8-ISSUE-MRE-W14.md. One preparation stage only, no push, CI, publication, ledger or local cargo/rustc/Kani/CBMC. Continuation of same review: previous sibling candidate61ffa0b, final candidate preserves sole upstream parent. Inspect git diff61ffa0b..d860e305 for bounded snapshot delta; packet uses common upstream ancestor.

## Invariants
- Sole parent clean upstream0aac, changes only .github/workflows and one control directory, all stock workflows removed; author Tiramisu-Cake <igkharin@gmail.com>, [skip ci]. No SEL1 or tool-model/std-source patch.
- 7 source files /10 exact-harness invocations:3 copy MREs, original slice2, initialized slice2, thin uninitialized2, true uninit read1. Preserve original Rust blocks and exact byte slice MRE; initialized/thin variants change only declared substitutions.
- Copy semantic flags exactly -Z valid-value-checks; slice/control flags exactly -Z function-contracts -Z uninit-checks. Append only JSON export transport. No suppression, timeout/jobs/unwind/solver/cbmc override.
- Freeze SUCCESS or exact FAILURE description/class oracle per row. Capture generated property IDs, all failed records, original exits/exception/snapshots. Distinguish expected diagnostic reproduction from desired correctness. No proof credit.
- RFC0015 schema, identities/source/selection/stage/metadata/features/default checks/summary/status inventory gates. Timeouts, errors, partial/missing/null/wrong-type exports, unbound diagnostics and mismatches remain UNKNOWN/NOT_RUN or unexpected; aggregate must not claim successful sweep.
- One job timeout30min, sum step caps28min, setup4min/build720s/row30s/phase330s; bounded process group RSS6GiB, heads1MiB/tails4096, exports8MiB. Always fallback/upload, preserve original run receipt, materialize missing NOT_RUN and incomplete UNKNOWN. No guarantee all rows finish within caps.
- Runtime authority belongs to separate coordinator stage only, same-tree non-skip sibling sole upstream parent; current upstream comparison in draft remains separately pending.

## Required controls
- New KeyboardInterrupt/fallback regression: saved RUNNING receipt unchanged, recovered UNKNOWN includes exact argv/cwd/export_path and source/request/rows hashes. Other candidate invariants unchanged. No compiler/verifier.

## Declared dependencies
- `.github/actions/setup/action.yml` → `dependencies/0000.bin` (mode 100644, SHA256 6ee9af29eb091ce92cb819deb205f1f07895e8bbdb02d0c5e510de85025dc307)
- `scripts/validate_json_export.py` → `dependencies/0001.bin` (mode 100755, SHA256 af2a207bafbe4fd66254d40a0c022bfa4b51a76a426aedfc9f27ed14388e8b7d)
- `tests/json-handler/schema-validation/kani_json_schema.json` → `dependencies/0002.bin` (mode 100644, SHA256 e687c3af91544431c84071e1b5105682ae4f93c0dc191d03e8a545e375807670)
- `kani-compiler/src/kani_middle/transform/check_values.rs` → `dependencies/0003.bin` (mode 100644, SHA256 94311cc2cead5b0588768e3a6495a700c486459f94b0302e8625251a03d42d50)
- `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` → `dependencies/0004.bin` (mode 100644, SHA256 487138ede144c9cea764b1da8562a90525cfdcab7ba110e044d46a3b75ce502e)
- `kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs` → `dependencies/0005.bin` (mode 100644, SHA256 ad73c82580f8f9ba3528ce9b6b371c6a4f717443e31a86b1fad6bad0a2c80d64)
- `library/kani_core/src/lib.rs` → `dependencies/0006.bin` (mode 100644, SHA256 fd4936db12f998df2419b9e6240f9171643f8287654840596ea2db40cfd76bc0)
- `kani-driver/src/frontend/schema_utils.rs` → `dependencies/0007.bin` (mode 100644, SHA256 6cf7b1311b3ebfd6ec1ce61efb1875b33d067fc2a89d2e7d1ccf8bf6995b1a64)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- All MREs runtime NOT_RUN, source predictions only, exact generated IDs available only after future execution, proof credit NONE. External caps can leave UNKNOWN/NOT_RUN.

Do not execute source or evidence from this packet. Do not claim new proof credit.
