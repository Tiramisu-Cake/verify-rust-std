# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `9fa2f7f97760584f38738909625c064006d8a936`
- Candidate: `166a406e2203bae2fc9246ba00c00b944b364445`
- Candidate tree: `460029c0d95fa7ef04eb7da0115f6fa2792c3b0b`
- Diff SHA256: `876a0bb371353e5aa995c8a788bcf2bac5599a704f887e9bcdec130b58cac434`

## Defect

Prepare the assigned correctness-verification harness workarounds A/B/C and PROF-ON-02 without compiler changes or execution.

## Applicability

One connected semantic candidate; review source, fresh binding adapter and forthcoming paired-lane CI packet together. Treat implementation narrative as claims to verify.

## Invariants
- No compiler/runtime algorithm changes, new trust, narrower input domain, weakened oracle/check/cover, or initialized true output.
- No push, CI, ledger, local Rust/compiler/verifier or raw-artifact reading. Static Git and isolated Python synthetic tests only.
- Original 62 rows retained with the extra exact-length merge4 leaf. Fresh exact row source/property/role/cover/frame binding; zero historical admissions.

## Required controls
- Inspect all changed reachable array constructors and independent generation, including B16 raw u8 any_array override.
- Compare sort4 thin writeset to old slice frame; inspect new merge4 real-body PFC and exact consumer dependency. General merge2..32 must remain unchanged.
- Check comparator factory monomorphization for every matching leaf/consumer, volatile reads and per-call nondeterminism; reject function-item carry-forward.
- Check source coordinates and frame write binding, fresh post/covers, new leaf oracle, retained PolymorphicIter rows and NOT_RUN distinctions.
- Inspect synthetic failure paths; a binding-only function is not an acceptance decision.

## Declared dependencies
- `library/core/src/slice/sort/shared/smallsort.rs` → `dependencies/0000.bin` (mode 100644, SHA256 982449b95d4449807b55f6997f83c8cce6bb167e52a95b6e4342ab816d04ba84)
- `library/core/src/slice/sort/shared/smallsort/verify/forwarding_contracts.rs` → `dependencies/0001.bin` (mode 100644, SHA256 185406a7eab60351f509734b2124f8f1d96d59b0080bb077536ee56ac8497886)
- `library/core/src/array/mod.rs` → `dependencies/0002.bin` (mode 100644, SHA256 62eff35f915bcf6e13befba95dea9d8246b01420ad39af654951c071c8abc4ac)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No runtime compilation, verifier execution or proof credit; actual generated closure rendering/frame variable spelling must bind afresh.

Do not execute source or evidence from this packet. Do not claim new proof credit.
