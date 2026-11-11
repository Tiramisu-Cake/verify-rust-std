# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`
- Candidate: `a139af7ac47b794eaf7b8bdcae52a7ba0a866fea`
- Candidate tree: `661997d105b3c6aa565d4e26915c6fa852e97e3a`
- Diff SHA256: `11c981216337d5c4b786bfc9a70ff96439ec9b40a2de560fcfb7febb145fced4`

## Defect

Contract attributes must parse and preserve specialization default fn through initial and stacked expansion.

## Applicability

Kani function contracts on free functions, implementation methods, and trait default bodies; specialization fixtures.

## Invariants
- Production bytes must equal 2a3e2ae19cd1dc4a50f53b1283e7bcf215cb81d9 plus /root/KANI5116-use-ImplItemFn.patch (SHA-256 0921813bdd50693e378b71c8ea85a109ab2bcbbec2f1234d97cfbdff1e4ee443). No additional production changes.
- Keep the no-body trait guard, unrelated ItemFn parsers, and inner attribute placement. Review all annotated_fn consumers for syn 2.0.119 ImplItemFn fields and block: Block compatibility.
- Exactly one commit over baseline; author Tiramisu-Cake <igkharin@gmail.com>; original title; no internal stages, Co-Authored-By, or skip ci marker.
- Preserve PFC, stub_verified, invalid-caller harness name, and specific value != 0 expected failure. No false contracts or unreachable bodies added to distinguish positive tests.
- Remove comments duplicating fixture names; retain generic #4908/#5135 explanation.

## Required controls
- Negative requires fixture must use --no-assert-contracts so the expected precondition failure depends on verified stub routing.
- Both requires_first and modifies_first stacked orders must have PFC and stub_verified harnesses and consistent renamed references.
- Retain all existing positive and expected diagnostic regressions.

## Declared dependencies
- `Cargo.lock` → `dependencies/0000.bin` (mode 100644, SHA256 984ef4cea51f0ad74124311f5cd09fca6d9c8c37bdbb9a8f29dd87cce842fadb)
- `library/kani_macros/Cargo.toml` → `dependencies/0001.bin` (mode 100644, SHA256 788dba9e7dfe46f8d70b6b902978a8f2ae711aa9cc8fb3116775514cf5ada960)
- `library/kani_macros/src/sysroot/contracts/assert.rs` → `dependencies/0002.bin` (mode 100644, SHA256 ec6480d46c29038b58cdac5d96ef962bd004e2d4fd16be6b9b64ee143f9cd5b4)
- `library/kani_macros/src/sysroot/contracts/check.rs` → `dependencies/0003.bin` (mode 100644, SHA256 de97631cb1e6881361a66f5b0e3b633fd8162ea5171d918770315a5d5def951f)
- `library/kani_macros/src/sysroot/contracts/replace.rs` → `dependencies/0004.bin` (mode 100644, SHA256 6bd51d3234c0778c5e0a465d1009d4efdee21dc2565e626b6d309f25c6791f05)
- `library/kani_macros/src/sysroot/contracts/helpers.rs` → `dependencies/0005.bin` (mode 100644, SHA256 710d7ef9ca4ca6e2fc277a56d3f1f1b1008ae7162eaf7d8f3fc0c1826810fd30)
- `library/kani_macros/src/sysroot/contracts/shared.rs` → `dependencies/0006.bin` (mode 100644, SHA256 a8df9244d86742adaf1bdfd991d1b6882962a6797b764d6824306f02024360e7)
- `rustfmt.toml` → `dependencies/0007.bin` (mode 100644, SHA256 d1886a654a790b5f5779d12c770b32c5328e4e4eaa415fc3a024c6ba9df687b1)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Static review only. No builds, cargo/rustc/Kani/CBMC, Cloud, CI, push, PRs, issues, comments, raw logs, archives, credentials, or nested delegation. Compile and behavioral validation remain NOT_RUN.

Do not execute source or evidence from this packet. Do not claim new proof credit.
