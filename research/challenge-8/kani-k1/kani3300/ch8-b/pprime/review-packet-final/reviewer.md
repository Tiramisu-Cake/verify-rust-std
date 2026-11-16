# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `0aac16ef62da9e9d5645782d458593e5d78143ba`
- Candidate: `4d7e34383a3af504a261228fdee59e6c7093e633`
- Candidate tree: `18796b2baeee695aa180c4f8e83da2009f179df6`
- Diff SHA256: `21a591c13ad996a4cb1a70cd2140b97a443a12cce111eac2f5e35404584de1ed`

## Defect

B census used std872d incompatible with stock0aac; rebase to P-prime and isolated kani-host workflow with separate pristine tool checkout. Assess source/manifest binding and absence of global inventory.

## Applicability

One stage TASK-CH8-B-PPRIME-W14; preparation only. Compare previous B candidate 5ee153ec2b22f1f7a0e174a985369b2280d8d296 for delta. No nested delegation. No local cargo/rustc/Kani/CBMC.

## Invariants
- All235 roots byte-identical and historical shards183/52, organizer flags plus valid-value-checks, exact selectors.
- P-prime c5ff36ff source with pristine model-checking/kani0aac; code changes only in host workflow and B scripts.
- Keep600s/root6GiB, existing stage/job caps, strict export classifier and all12 original tests.
- No list phase; directly selected verify-std, no stock run-kani.sh. Receipt/unknown semantics unchanged.

## Required controls
- 13 synthetic tests, static_check.py, actionlint and diff check; no actual compiler. Source audit and unchanged manifest available at /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-b/pprime

## Declared dependencies

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Static package only; runtime235 NOT_RUN; no proof credit.

Do not execute source or evidence from this packet. Do not claim new proof credit.
