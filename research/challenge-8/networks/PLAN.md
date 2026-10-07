# Independently authorized networks phase

Owner instruction on 2026-10-07 authorizes this branch independently of stops
in sort4, up to 1800 summed hosted job seconds including preparation, one run on
this branch at a time, up to two across both directions. Start at fixed
bea62488b44f8c557e45e04cb4eb259b0173422f; preserve the other worktree.

1. Specify actual swap_if_less as an effect-aware ownership-preserving primitive.
   Keep unrestricted safety separate from fixed-order functionality.
2. Pin and certify exact sort9/sort13 call order, indices and prefix domains.
3. N9: unchanged official VeriFast 26.09, ghost-only mathematical composition.
   Prove all Boolean inputs, checked threshold transfer to unrestricted integer
   ranks and occurrence permutation; calibrate sorting/permutation negatives.
4. Only after accepted N9, run the same profile/obligations for N13.
5. Preserve full hosted evidence, budget and exact proof SHA. Prepare integration
   proposals; commit/push branch, no automatic merge or public submission.

Tool allowlist: official stock VeriFast 26.09 release, source
809de4596839b739dd999f9e462242c835e3af46, archive SHA256
da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa.
No tool patches, historical profiles, RAPx, kernel/frontend/prelude/refiner changes.
The C ghost engine is the same pure-component route used for sort4; these are
mathematical lemmas, not executable C replacements for Rust or Rust-body proofs.
Source correspondence checker is an independently auditable extraction gate,
not a semantic rewrite of the Rust verifier. Every generated proof is retained
in Actions artifacts. No proof code from other solutions is imported.

Abstract CE on logical occurrences (A,B): with Boolean c, outputs are
`(c ? B : A, c ? A : B)`. For sorting only, there is a fixed total preorder
on preserved keys, c iff key(B)<key(A), and all callbacks return normally.
For arbitrary comparator decisions the permutation theorem still holds.
No stability promise. No Copy/Freeze requirement on T for safety or abstract
identity composition. Integer ranks encode finite ordered key classes; their
representation does not constrain physical Rust layouts or key magnitude.

All checks execute on GitHub-hosted Linux; each proof has a 180s timeout and
each job at most 10 minutes (including cold preparation/upload). Use actual job
timestamps for summed cost; never transfer spend from the other branch.
Before dispatch check existing runs, push and confirm remote full SHA; use only
workflow_dispatch. Inspect that exact run and all artifacts. A source change
needs a NEW run. Setup/parser/timeouts are inconclusive, not intended negatives.
Routine annotation/checker fixes within this unchanged profile are authorized;
new semantics, insufficient Rust ownership bridge or exhausted budget checkpoint.
