# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `242ca631743080daa98850d9d385a8079fbe581f`
- Candidate: `2ed50d63e09619470b53c1702f6ae987f4454b78`
- Candidate tree: `452b26330b97fc9b9816c28c64240bd667b2d4c0`
- Diff SHA256: `3c01c89b2408471b182c764d4c54864b149258b339543f09126030fad8a72587`

## Defect

Profiles OFF workflow resolved --repo ../.. from control/ch8-prof-off-control to workspace root; validate failed before proof. Fix to .. and add static path regression.

## Applicability

Review only delta from prior control 242ca631743080daa98850d9d385a8079fbe581f. Packet requires ancestor baseline, so review-only commit 2ed50d63e09619470b53c1702f6ae987f4454b78 has prior control as parent. Actual deliverable 741b7183b4d6e9d752c0b7951206d7257f69f951 has exact same tree 452b26330b97fc9b9816c28c64240bd667b2d4c0 and sole stock0aac parent. Verify tree equality and exact delta; no full stock diff review.

## Invariants
- No push, CI, ledger, local cargo/rustc/Kani/CBMC or nested delegation.
- Source/tool pins, 62 manifest rows, selectors, oracles, resource caps, budgets and runner.py unchanged.
- Offline static check resolves literal --repo relative to effective workflow/job/step working-directory and requires one preceding checkout path: control. Missing/ambiguous/unresolved explicit paths cannot pass.
- Common checker supports explicit check_package.py control --repo workflows; B/E implicit roots are not claimed covered.
- Preserve historical packages/reviews. Static preparation only; qualification NOT_RUN and proof_credit NONE.

## Required controls
- Fixed actual workflow passes; old ../.. must fail standalone path check and check_package.check_yaml.
- Synthetic nested paths for S1/B/C/E-shaped packages; cwd default precedence; --repo= and line continuation.
- Missing/null/wrong-type/NOT_RUN/duplicate args, wrong paths/checkouts/late checkout and second bad validation step fail.
- All existing Python synthetic runner/profile/batch tests continue to pass.

## Declared dependencies
- `ch8-prof-off-control/manifest.json` → `dependencies/0000.bin` (mode 100644, SHA256 c10f4e49ec65143534bebafec35d59fb7bc1db39f08bfac3d298101b216e1273)
- `ch8-prof-off-control/runner.py` → `dependencies/0001.bin` (mode 100644, SHA256 e866a565788f1f41e4cfb26e9880a44a9cd09713d82b323de3508032bca066be)
- `ch8-prof-off-control/test_profiles.py` → `dependencies/0002.bin` (mode 100644, SHA256 9726fad1363cdb75628d4560426271125b2dd5e3928ca525571b1e079633a972)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No compiler/verifier/CI execution or proof credit.
- Static checker accepts direct Python commands with literal relative --repo paths; implicit roots, shell cd or dynamic expressions are not resolved.

Do not execute source or evidence from this packet. Do not claim new proof credit.
