# Independent W8 arithmetic preparation review

Reviewer: independent GPT-6 Luna HIGH, no nested delegation.
Decision: scoped GO for static preparation only; no proof credit and no Build authorization.
Baseline: `5cfb9adb549f093cc3d0e31e64fb1a23c2a895fb`.
Candidate: `040ffa8e857e8483d0712fe8ba94a18ad57a9a60` (tree `d595449f9e72b2311e5fdcbdb5bc129082a64b93`).
Spec SHA256: `4541756ceaaa4601481299033023a5b372e2b0e4d8430b9b257da4f9eb1f8089`.
Packet SHA256: `bd0cbeaba4129a2bcf06fc810a5191b15985b1350a27ed43db6e6243dfca9eff`.
`smallsort-session review check` passed for these exact candidate and spec identities.

No blocker for this preparation candidate. The three definitions are pure integer fixpoints. For region lengths at least one, the selector returns 1 for 1–8, 9 for 9–12, and 13 for 13 and above, so the prefix is in bounds. On the declared 18–32 split domain, `left=floor(len/2)` and `right=len-left` range from 9 through 16 and sum to `len`; the explicit cases give both prefixes 9 for 18–24, prefixes 9/13 for 25, and both 13 for 26–32. The separate endpoint lemma’s six claims also match the selector. Each positive lemma has a body; no axiom, `assume`, `lemma_auto`, or bodyless bridge appears.

The pinned SmallSort source SHA256 and blob match the stated identities. Its inspected branches use the documented `<2` early return, scratch bound 32, `len/2` split at the two-region path, and 13/9/1 prefix selection. The candidate correctly leaves these as static associations: there is no proof that a Rust branch guard supplies the ghost facts, no MIR/parser binding, and no claim about Rust behavior, ownership, termination, or ZST reachability.

The three negative fragments are separate one-target fragments and must be assembled individually after the full positive file; they are not standalone units or summaries. The length-25 and region-8 controls contradict the corresponding candidate facts. The length-33 control is the literal false assertion `33 <= 32`; it can test a target diagnostic but does not establish that the Rust `len > 32` abort route is taken. Keep source-stage-target binding and route controls for a future authorized phase. Each future unit must recheck and inventory all three positive bodies before its one intended negative; any prefix failure remains inconclusive.

`git diff --check` passed, and the source identity was independently checked against both the worktree file and pinned Git object. No local assembler, generator, compiler, or verifier was run. Preparation remains unverified; future W8 integration still needs an authorized phase plus compatible network/insertion/merge evidence and the caller ownership, unwind, initialization, framing, copy-back, and control-flow proofs.
