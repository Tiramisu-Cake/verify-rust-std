# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `14bc57fdb99960240c4944845a3d985c8af4dcf7`
- Candidate: `d569db0c1f98e26573d0d15d022e9ac0c6d877fb`
- Candidate tree: `660633a37fb527dae4bdc2d9c845bd65ca578cdb`
- Diff SHA256: `62b13fcbfcd120faca8e8aadeb967c0bd55b361e8a22756eabd5b575975001d1`

## Defect

Assigned preparation of Profiles ON qualification using accepted OFF runner with SEL1 exact fork tool pin and uninit checks; no CI execution in this stage.

## Applicability

Review one committed CI-only candidate against SEL1 parent; compare behavior to accepted OFF control112fcc9ada in /root/kani-ch8-prof-off-w11. Full patch includes sole workflow + CI package and removal of unrelated workflows, as in OFF. Source unchanged9fa2f7f977. Required task at g0 research/challenge-8/kani-k1/TASK-CH8-PROF-ON-W15.md. Focus semantic delta after mechanical OFF-to-ON renaming, exact frozen manifest/oracles/bounds/caps, actual fork tool checkout/build and classification reuse without OFF admissions.

## Invariants
- No push, CI, publications, ledger, cargo/rustc/Kani/CBMC, raw evidence download/read, or nested delegation. Git/static Python/small synthetic tests only.
- Keep all62 rows, sourceP-prime9fa2f7f977, manifest byte equality,9 negative oracle descriptions and frame pending binding; no check weakening.
- Tool14bc57fdb99960240c4944845a3d985c8af4dcf7 from Tiramisu-Cake/kani nightly-2026-10-23; -Z uninit-checks ON and valid-value OFF; all other OFF flags/cfg/source unwind preserved.
- Keep two cfg batches53+9, per-row bindings, regular stdout receipts, source/tool/target/stage guards, original exits/exceptions, timeout/partial/missing/NOT_RUN handling.
- Static preparation NOT_RUN; proof credit NONE. Existing accept-v4 code reuse requires fresh ON bindings; never reuse historical OFF ACCEPT rows.

## Required controls
- Check workflow repo path --repo .. and old ../.. rejection; checkout/build exact fork SEL1 source outside control.
- Run46 runner/profile/batch/path/ON synthetic tests; inspect success/error/timeout/partial/missing/null/wrong-type/NOT_RUN and source-stage-target mismatch coverage.
- Independently inspect static call reachability of general-scratch PolymorphicIter and networkN32 risk by row; RISKS.json/md are claimed static analysis to verify, not proof.
- Assess accept-v4 functions/source-chain applicability and fresh exact symbol/role/property/cover/frame/leaf constraints; new uninit properties cannot inherit OFF admission.
- Review ON export/request feature mismatch guards and budgets; inspect patch reconstruction/static-audit identity checks.
- Recheck prior finding delta in review-fix.patch: exact exported unstable-feature set (including requested unstable-options), reject unknown extras/duplicates/ghost-state/missing unstable-options. Trace SEL1 schema_utils.rs:95-101 and call_single_file.rs:161-166: ghost-state is added only to compiler flags, not the exported driver feature set. Confirm from source.

## Declared dependencies
- `ch8-prof-on-control/CI-REQUEST.json` → `dependencies/0000.bin` (mode 100644, SHA256 eb18c312eb0cd5d3c41e0d7252fd453b85c63fe3a417a3b3a8c37c0da81968ba)
- `ch8-prof-on-control/manifest.json` → `dependencies/0001.bin` (mode 100644, SHA256 c10f4e49ec65143534bebafec35d59fb7bc1db39f08bfac3d298101b216e1273)
- `ch8-prof-on-control/runner.py` → `dependencies/0002.bin` (mode 100644, SHA256 d1ce6261a7426d76f2525b28a15fa1db456ee05426efcc2fcd28924c1659ce3c)
- `ch8-prof-on-control/check_package.py` → `dependencies/0003.bin` (mode 100644, SHA256 6712a13bde9b46bfda19e3946de6ee91b9fe0b94f98c688471bb4db948b12b52)
- `rust-toolchain.toml` → `dependencies/0004.bin` (mode 100644, SHA256 8ae6767838d7384b2b764bda9262793d4861a798e49e57dc965fe37ead8e65df)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No actual compile/proof/CI qualification. Source reachability does not predict verifier outcome.
- Post-CI fresh evidence/admission is a separate stage. Historical accept-v4 replay is OFF-bound, not an ON command.
- G0 auxiliary files at /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-profiles/on-ci; use supplied paths as static data only.

Do not execute source or evidence from this packet. Do not claim new proof credit.
