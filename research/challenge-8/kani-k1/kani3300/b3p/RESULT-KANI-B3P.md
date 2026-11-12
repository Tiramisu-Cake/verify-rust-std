# KANI B3P result

- New local Kani SHA: `83a413f9be2d57389c991d9f5d1250b4e4386203`, branch `fix/zst-union-codegen-v2`.
- One fix-plus-tests commit; sole parent `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`; exact three-file diff.
- Old head `6db3c4dabd4a368314eb8e2b71d21d1eee721593` remains unchanged.
- Both trees: `c9b9bafdeca616fac235574f33dad477c25ad90b`; old..new diff empty; diff check PASS.
- PR draft corrects the reproducer, physical/logical types, test scope, exact historical CI identities/results, issues, and signoff.
- New SHA: NOT_RUN; historical default-selector 7/7 and Linux final-placement results retain their original SHAs.
- Full workflow cancelled; macOS 14/15 Intel have no completed regression result; full matrix unconfirmed.
- Separate uninit-checks panic remains; reduced PANIC-NOTE input NOT_RUN; no G1/MaybeUninit-transfer claim.
- Independent packaging/text review: see REVIEW.md.
- Cloud $0; no compiler/verifier/build/CI runs, Kani push, PR, issue, or comments.
- Stage complete; STOP after the research publication.
