# RESULT-KANI5116-KF3
Kani `upstream-5116-v2`: `a139af7ac47b794eaf7b8bdcae52a7ba0a866fea`.
Base/sole parent: `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`; exactly one commit, required author/title, clean tree.
Research input: `53661a2d46c41120cc67a28180d46837269eec70`.
Production: 3 files +13/−12; tests: 14 files +433/−0 (9 Rust, 5 golden), all against base.
1. Discarded coordinator draft; applied auditor patch unchanged atop `2a3e2ae19cd1dc4a50f53b1283e7bcf215cb81d9`.
Patch SHA-256: `0921813bdd50693e378b71c8ea85a109ab2bcbbec2f1234d97cfbdff1e4ee443`.
Temporary-index apply and byte comparisons: production diff BASE..HEAD = original candidate + exact auditor patch (PASS).
Production diff SHA-256: `25caf4d2a9de599f783d70ef68107a6f01dad0f51a3647b00ff5ab565d32af7f`.
2. Added --no-assert-contracts; retained PFC, stub_verified, check_invalid_caller and exact value != 0 expected failure.
3. Renamed forward/reverse to requires_first/modifies_first throughout; added the second-order stub harness.
4. Removed four redundant comments; retained the generic #4908/#5135 explanation and PFC prerequisite comment.
Static: rustfmt wrapper --check --edition 2024 with repo config (all 12 changed .rs), diff --check, license headers PASS.
Static syn 2.0.119: all ImplItemFn fields/Block consumers compatible; default emitted manually initially and via ToTokens subsequently.
Trait no-body guard, unrelated ItemFn parser, inner-attribute placement unchanged; no broader inner-attribute support claim.
Independent review: Luna HIGH, separate context, no static findings on exact candidate/packet; INDEPENDENT-REVIEW.md.
NOT_RUN: compilation, macro-expansion execution/equivalence, Kani/CBMC/native tests, fork/full CI (coordinator gate).
PR-TESTING-NOTE.md separates historical Linux native 19 selectors on f046b70644/previous patch from pending final CI `<run, SHA>`; lists draft corrections.
No builds/dispatch/Cloud: $0; no Kani push, Actions, PR, issue, or comments. Protected Kani branches unchanged.
Details: STATIC-CHECKS.md; exact review packet and spec retained alongside this result.
