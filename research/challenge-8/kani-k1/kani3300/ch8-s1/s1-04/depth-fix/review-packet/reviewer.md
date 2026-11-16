# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `40b5d9cf48900ff1e227e1fbba24cb5b2edbf8d5`
- Candidate: `205b0e98c771a7e6c6b8ec28414494868bcca4e0`
- Candidate tree: `27692f2145d4faec363ba04faea9feb775cccd5f`
- Diff SHA256: `2ba4d934bc2901903e5f87624929c4aee54e3612ecebb2553a4a903aaea1d1d4`

## Defect

Control HEAD -> parent 40b5d9cf4 -> tool 0aac16ef62; depth 2 excludes tool endpoint of control diff and exits 128.

## Applicability

S1-04 checkout depth/preflight/synthetic regression delta against reviewed sibling 2a532e5913173d6af4490c25d74c587f7bf1a749. No proof/model changes.

## Invariants
- Only four sibling-delta files: workflow, check_package.py, test_package.py, CI-REQUEST.json.
- Only four control checkout depths change 2 -> 3; all export/tool depths remain 2. Other workflow content and request fields except three payload hashes unchanged.
- Candidate sole parent 40b5d9cf48900ff1e227e1fbba24cb5b2edbf8d5; author Tiramisu-Cake <igkharin@gmail.com>; no skip ci in control.
- No push/CI/publication/ledger/compiler/verifier. Proof NOT_RUN; credit NONE.

## Required controls
- Typed YAML policy checks all 12 checkouts; real file:// shallow clones at depths from each job; real control() and verify_source() checks; control depth 2 reproduces diff exit 128; depth 1 rejects HEAD^; existing tests retained.

## Declared dependencies

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Packet uses ancestor common parent; review ONLY git diff 2a532e5913173d6af4490c25d74c587f7bf1a749 205b0e98c771a7e6c6b8ec28414494868bcca4e0 and dependencies needed to assess it.
- Shallow clones use tiny synthetic histories, not full production repository copies. Old g0 preparation validators are not executed by workflow; their sibling comparisons require full local history.

Do not execute source or evidence from this packet. Do not claim new proof credit.
