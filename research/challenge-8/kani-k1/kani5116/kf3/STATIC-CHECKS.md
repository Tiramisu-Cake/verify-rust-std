# KF3 static checks

Candidate: `a139af7ac47b794eaf7b8bdcae52a7ba0a866fea`.
Base: `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`.
Original candidate: `2a3e2ae19cd1dc4a50f53b1283e7bcf215cb81d9`.
Research input: `53661a2d46c41120cc67a28180d46837269eec70`.

Auditor patch `/root/KANI5116-use-ImplItemFn.patch` SHA-256:
`0921813bdd50693e378b71c8ea85a109ab2bcbbec2f1234d97cfbdff1e4ee443`.
Applied unchanged after discarding the three authorized coordinator draft files from upstream-5116-v2.

An isolated temporary Git index was initialized with the original candidate; `git apply --cached --check` and `git apply --cached` applied the exact auditor file.
Each resulting production blob was compared byte for byte with the working tree, and the full binary production diff against main was compared byte for byte: PASS.
Production diff SHA-256 (`git diff --binary BASE -- library/kani_macros/src/sysroot/contracts/{bootstrap,initialize,mod}.rs` order):
`25caf4d2a9de599f783d70ef68107a6f01dad0f51a3647b00ff5ab565d32af7f`.

| File in contracts/ | Exact resulting Git blob |
| --- | --- |
| bootstrap.rs | 400b24cb73541f9b7311ac11e024cfca2cfe2fac |
| initialize.rs | 12c1338a9e7564d99d026a885cf43b695baafa28 |
| mod.rs | 580f670930c46cbae77401804282057ef68b70f9 |

Static invariants: the trait declaration/no-body guard and the proof_for_contract ItemFn parser are byte-identical to the original candidate. No standalone ContractFunction remains (ContractFunctionState remains intentionally).
The initial quote template, including attribute placement and `#vis #defaultness #sig`, is byte-identical. The stacked path clones ImplItemFn, mutates its block statements, and quotes the whole node.

Cargo.lock resolves the macros crate's syn 2 dependency to 2.0.119. In [syn 2.0.119 item.rs](https://github.com/dtolnay/syn/blob/2.0.119/src/item.rs#L711), ImplItemFn has attrs, vis, defaultness, sig and block: Block. Its parser accepts visibility, optional defaultness, Signature and a body; free functions and trait methods with bodies fit this syntax. ItemFn and ImplItemFn parsers preserve inner attributes in attrs; their printers distinguish outer/inner attributes. ImplItemFn printing emits defaultness. The manually assembled initial Kani expansion keeps its previous attribute placement; no broader inner-attribute support claim is made.
All annotated_fn consumers were inspected: initialize reads sig.ident; check uses sig and passes &block to modifies_closure's &Block parameter; replace/assert read sig, and assert reads block.stmts; bootstrap mutates block.stmts and quotes Block/ImplItemFn. Helpers operate on closures/statements/expressions without depending on ItemFn or Box<Block>. These accesses are statically compatible; compilation remains NOT_RUN.

Checks: wrapper `rustfmt.sh --check --edition 2024` with repository config passed on all 12 Rust files changed from base; `git diff --check` passed; all 12 copyright/SPDX headers passed.
Requires fixture: --no-assert-contracts, PFC, stub_verified, check_invalid_caller, probe(0) retained; the specific value != 0 golden is unchanged.
Clauses fixture: all references renamed consistently; both clause orders have PFC and stub_verified harnesses; existing contracts and bodies retained. Four redundant comments removed; generic #4908/#5135 explanation and the comment explaining the required PFC harness retained.
No new dependencies, toolchain, runner, CI, or production edits beyond the exact patch.

NOT_RUN: compilation, macro expansion execution/equivalence, Kani/CBMC verification, native compiletest, fork/full CI. No builds or Cloud calls; stage Cloud cost $0. Historical results are not validation of this candidate.
