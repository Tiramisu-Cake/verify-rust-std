# C2 Gate B′ inputs

Task: TASK-KANI3300-C2-GATEB-REPLAY.md, g0 entry 73d5b3ddec3422bef4390ef9e75304dbb4b62a4f.
Exact clean HEAD/tree/branch identities were recorded in INPUTS.json before any edits or worktree creation.
C2 freeze ad499e41dd2db9ccd432f89721638a1f3a0bbd44, tree 9829702c1aa0ecb73c860fc0ad5451757917d6cb.
Coordinator Gate A acceptance: c2-gatea/ACCEPTANCE.md, run 43665002636. This is a supplied regression acceptance, not new formal proof evidence.

C1 replay recipe: 0c1cc8a7d05184044d496b01f5ed41cebfde0cac, tree cbb04807c711a9d1bad2ac2dbe1f77538d5658b0; read through local SEL1 repository Git objects. C2 clone does not contain this object; no fetch/clone was needed.
SEL1 worktree is a read-only rebinding precedent; none of its six-row profile, std patch, or select implementation was imported.
Std package: 01d75b8e839c751e7ab679fdaaa5fba6384983b6; test overlay 933b20a2375bd7529243510728b1eb48adf34e5d, library 86cbdb4d9f8415161657f66bf07e5a0dd1b3e982. Std base 70ba5befc617627073738e26cb1466bd4fb76e41, library 6ea9d3425f6d0478cfc2517cbdd2fb7d7b32a53f.

New worktree created with git worktree add from the existing C2 clone, branch ci/kani3300-c2-gateb-w15, one local CI-only commit on exact freeze. No new clone, build, target copy, push, CI dispatch, external publication, or review. Cloud spend $0.
After identities and source projection checks are in INPUTS.json and VALIDATION.json. The g0 package identity is its containing commit, reported at handoff, avoiding a self-referential SHA.
