# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `628ba7fd9b8d1f66d5ccd220ce6ea84bc4626027`
- Candidate: `84c98513b526a7cc58d2248158f92fe4b8d512f3`
- Candidate tree: `c07b5aded52231540eab49e2a173a57ed7b903c9`
- Diff SHA256: `5c18044497782be3e97aa3bca95d0f03d6dc4fe4ef7443b604e6013a383fb371`

## Defect

E-01 E-S has invalid namespace; H loop shadow assigns observation confounded by MaybeUninit on upstream. Prepare only E-02 calibration with exact diagnostic oracle and static checkout path preflight.

## Applicability

TASK-CH8-E02-W15.md g0 f04b83e085: one stage, bucket E item1, single-file no std, same upstream0aac/SEL1 pins and ch8-e-control template. Prior package reviewed; current review is bounded delta plus dependencies.

## Invariants
- No push/CI/publication/ledger or local cargo/rustc/Kani/CBMC; no tool/shadow/havoc model changes. Control preparation must be skip-ci sole-parent upstream0aac; reviewed candidate has old control as parent, final control must have identical tree.
- Six independent roots ON/OFF at both pins: E-S positive and false value, primitive H raw-write/no-write/no-loop, byte-exact issue MaybeUninit MRE. Original E-01 fixtures remain; old obligations stay open.
- No CAP, symbolic usize length through existing alloc-enabled namespace; false property exact source/message/line and cover inventory. Assumes limited to existing generated storage/read index premises, no assume instead of invariant.
- Primitive no-write has no assert17 since loop frame havocs payload. Positive returns/body/value checks distinct; no uninitialized negative claimed for initialized primitive.
- MRE SEL1 ON ASSIGNS_FAILURE requires all failures exact class/message/library:120, body cover, complete check counts; unreachable follow-on checks allowed only diagnostic outcome. Never count diagnostic as positive proof. Upstream desired SUCCESS remains UNKNOWN on known unsupported union; do not call it assigns reproduction.
- Keep default checks, uninit ON/OFF, exact pins/request/source/schema/stage gates, original exits/exceptions, bounded snapshots and NOT_RUN. 600s/660s/6GiB/75min phase/120min job unchanged.
- Explicit check_package.py control --repo .. from control/ch8-e-control must resolve to checkout control; static workflow path preflight from Profiles fix1. Same-tree activation only by separate coordinator.

## Required controls
- 40 isolated Python synthetic tests, including baseline error/timeout/partial/missing/null/wrong-type/NOT_RUN/mismatch and new path/assigns/pin/message/line/mixed-failure/inventory regressions; YAML/actionlint/diff check. Review these tests and scope without executing any compiler.

## Declared dependencies
- `.github/actions/setup/action.yml` → `dependencies/0000.bin` (mode 100644, SHA256 6ee9af29eb091ce92cb819deb205f1f07895e8bbdb02d0c5e510de85025dc307)
- `scripts/validate_json_export.py` → `dependencies/0001.bin` (mode 100755, SHA256 af2a207bafbe4fd66254d40a0c022bfa4b51a76a426aedfc9f27ed14388e8b7d)
- `tests/json-handler/schema-validation/kani_json_schema.json` → `dependencies/0002.bin` (mode 100644, SHA256 e687c3af91544431c84071e1b5105682ae4f93c0dc191d03e8a545e375807670)
- `library/kani/src/arbitrary.rs` → `dependencies/0003.bin` (mode 100644, SHA256 f74cec2acfdf62dd5300f2d0d92d8ffeb11d6053cc270de41e4aeacc68ac03c9)
- `library/kani_core/src/mem_init.rs` → `dependencies/0004.bin` (mode 100644, SHA256 88f260ddc5b315a32e64b0f6f396451373d2fb54f1a4898233508ebd81cd993c)
- `kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs` → `dependencies/0005.bin` (mode 100644, SHA256 ad73c82580f8f9ba3528ce9b6b371c6a4f717443e31a86b1fad6bad0a2c80d64)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- ALL_NOT_RUN, proof credit NONE. No claims of compile success, initialized symbolic storage validity, GOTO causal binding, full E or generic theorem. Covers need runtime source correlation. Historical E-01 unchanged.
- Expected assertion/assigns messages frozen from pinned source and existing observed diagnostics; new roots never compiled. Worst-case 12*660s exceeds phase4500s, same bounded phase policy materializes remaining NOT_RUN.

Do not execute source or evidence from this packet. Do not claim new proof credit.
