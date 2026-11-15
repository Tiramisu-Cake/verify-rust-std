# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `872d5a43380752786415bc00d2a12ce0e930cb37`
- Candidate: `75a4d1ea6eb60c63c27c1b18e662740d93bafb08`
- Candidate tree: `6d1b90bc11440762c9b65889fc538ba3071b0d9d`
- Diff SHA256: `9781723d8c5ee047317b0fc63f462a676c24953b0d73815b50390b74d2d377d1`

## Defect

S1 verification-only actual trait sorting contracts, closed model and smoke mechanism on six implementations

## Applicability

Six actual bodies on std872d with exact stock Kani0aac; named u8/Cell/NonCopyByte KeyLess pairs; N0..3 mechanism only. No verifier execution authorized.

## Invariants
- Runtime bodies/signatures/bounds unchanged. Six fully qualified trait threshold requires; Stable Freeze len<2 or scratch>=len+16.
- Conditional semantic ensures on each real body with owned old(snapshot), no comparator calls in checker, no broad generic theorem or verified summaries.
- Independent initialized backing/flat MU scratch, model activation before calls, canaries, N0..3 useful covers; no panic stubs.

## Required controls
- Worker11 12 model/control roots (3 pairs, inactive/invalid/order/count).
- Six PFC smoke roots and two fixed legal PFC activation companions; CI-only false-ensures variants planned separately.

## Declared dependencies
- `library/core/src/slice/sort/shared/mod.rs` → `dependencies/0000.bin` (mode 100644, SHA256 fa9eec2901bafba25c9c1e1684df76dbb1f86e0bbd04f18f3e67cee54dcdfcc8)
- `scripts/run-kani.sh` → `dependencies/0001.bin` (mode 100755, SHA256 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Rust/Kani NOT_RUN, forbidden locally; all qualifications future CI coordinator.
- Frames qualified only for exact named pure ZST comparators; no arbitrary FnMut frame claim or Replace use.
- No S2/full threshold/all internal branches/extra-UB proof.

Do not execute source or evidence from this packet. Do not claim new proof credit.
