# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `7d90c5e59b7a90a9d126427e70f2187497eff15c`
- Candidate: `bbd75af8cafbeb7906744149aed3832636494c30`
- Candidate tree: `14abf8438f48393bf0201907096483bfa48c911a`
- Diff SHA256: `5cb8db58dd96a99ebfebb7238ca33614c3535095f00907217f2884f82f0d9a30`

## Defect

Prepare the assigned correctness-verification harness workarounds A/B/C and PROF-ON-02 without compiler changes or execution.

## Applicability

Third packet of the single connected semantic review, CI-only delta relative to the exact imported ON package. Independently verify full tool-source equality against pinned SEL1 and preservation of inherited mature runner controls, oracles, cfg and caps. Two serialized jobs ON then OFF, same new source, fresh independent qualification.

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
- Verify baseline imported package7d90 tree equals prior d569db0c package, and complete candidate tool/compiler/library sources unchanged from SEL1.
- Check control checkout depth includes SEL1 ancestor, exact control full diff/payload guards, distinct per-lane tool/std identities/features/receipts/fallback and cross-lane refusal.
- Inspect one dispatch ON→OFF with always dependency, two sequential jobs180min each/maxactive1, per-lane caps preserved and total360 disclosed.
- Synthetic paths must retain success/error/timeout/partial/missing/null/wrong-type/NOT_RUN/source-stage-target mismatch and no historical accept carry-forward. Compare reductions in test count to verify controls are retained.

## Declared dependencies
- `library/kani_core/src/arbitrary.rs` → `dependencies/0000.bin` (mode 100644, SHA256 cdd7aa7e5c4cf7f1e977b965b9551cb2a5fdd2fe340e83051cf8df6a6ad53070)
- `library/kani_core/src/lib.rs` → `dependencies/0001.bin` (mode 100644, SHA256 fd4936db12f998df2419b9e6240f9171643f8287654840596ea2db40cfd76bc0)
- `ch8-prof-on-control/runner.py` → `dependencies/0002.bin` (mode 100644, SHA256 62ac5865a3bde8efbbdd5bda0b76e49b2fc431255d51ac1b13d70e87b2bd36ca)
- `ch8-prof-on-control/check_package.py` → `dependencies/0003.bin` (mode 100644, SHA256 bae459d6cf60399b350df180337ee82b0794cb63650cb26841c3a270ca97633b)
- `ch8-prof-on-control/CI-REQUEST.json` → `dependencies/0004.bin` (mode 100644, SHA256 eaa60eda6289b296ed9b7c0e1afbe6373f946cc6f304b543ad0cb72bcc6f468f)
- `ch8-prof-on-control/off/CI-REQUEST.json` → `dependencies/0005.bin` (mode 100644, SHA256 0d31dc6af520cbb9b9ec25d008acbaa661c6ad41ea55ff6b16ada7ff44775ffb)
- `ch8-prof-on-control/off/runner.py` → `dependencies/0006.bin` (mode 100644, SHA256 b8d24caeda313dd5fdb21da755bc129e958fbf7585076744584064dcbf25cd25)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No runtime compilation, verifier execution or proof credit; actual generated closure rendering/frame variable spelling must bind afresh.

Do not execute source or evidence from this packet. Do not claim new proof credit.
