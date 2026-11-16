# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `4d7e34383a3af504a261228fdee59e6c7093e633`
- Candidate: `99dbb2157bdb4f0322bcb3677f4ee51991de2f28`
- Candidate tree: `10421f334c1a90b723dde5378678b0439f862125`
- Diff SHA256: `15b7377bdc1511efd265ee745dd1d6b0413b4382556d18d8f1904952c17a6903`

## Defect

Per-root selection changes Cargo fingerprints and recompiles std. Review single equal-flag batch invocation, per-root binding/verdict, separate compile/preparation cap/receipt, resource/unknown semantics.

## Applicability

Direct user preparation-only B batch stage; g0 input82cc48368e. No nested delegation; no push/CI/ledger/local cargo/rustc/Kani/CBMC.

## Invariants
- Frozen roots.json235 selectors, manifest/oracles/classes unchanged; pristine tool0aac16ef and P-prime stdc5ff36ff.
- All235 roots one group; repeated exact selectors, Kani jobs1/harness timeout600s, one export. No per-root/warmup invocations.
- Group cap2100+235*600; sample group RSS<=min(12GiB,avail-2GiB); per-root RSS UNKNOWN.
- Only structured bound per-harness outcomes assign row classes. Unknown/missing/duplicate/wrong type/timeout and source/target mismatches do not pass; preserve failures/covers/original exits.

## Required controls
- 17 isolated Python synthetic tests; static_check.py; /tmp/kani3300-d0-ci-tools/actionlint -shellcheck= workflow; git diff --check. Reviewer may run static/synthetic only.

## Declared dependencies

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Actual proof/compiler NOT_RUN, no independent credit.
- Existing210min host-job ceiling may interrupt theoretical143100s group budget; produces PARTIAL.
- Compile marker boundary sampled after preparation; not independent compiler-internal timing.
- B contract structure retained as source metadata, no expected target oracle in frozen manifest.

Do not execute source or evidence from this packet. Do not claim new proof credit.
