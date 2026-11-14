# SEL1 inputs — 2026-11-14

Exact source base and tree, g0 task pin, SEL0/R4 authority and inherited std/recipe bindings are recorded in INPUTS.json. Initial read-only source was clean; destination was absent and cloned locally, then switched to fix/kani-3300-sel1. No latest C2-S2 state was imported. Existing g0 c2-s2 research was preserved.

Authority: TASK-KANI3300-SEL1.md at g0 38ed07ba0a94bd5a845cfec3bf95b44f0b9c46fa. Read CORE/RUNTIME-CODEX, task, draft R4, audit F8/answer3, SEL0 DESIGN and actual base fallback/visitor/points-to. This preparation has no phase, ledger or Build registration. No build/watch session was opened. The task's explicit preparation-only constraints govern execution.

Gate B′ source report: run43600834435, C1 merge SUCCESS 0/570 and0/1028, sort4 one select Unsupported; outcome field UNKNOWN. These are prior bounded evidence and motivation only. No credit carries to the SEL1 production delta.

Frozen std is70ba5befc617627073738e26cb1466bd4fb76e41; B′ package01d75b8e839c751e7ab679fdaaa5fba6384983b6/overlay933b20a2375bd7529243510728b1eb48adf34e5d. Their immutable trees, patch and per-file hashes were checked in the separate std clone; original package metadata remains unchanged. New std test overlay identities are in STD-OVERLAY.json.

All research here is uncommitted for the owner. Source commits use git -c user.name=Tiramisu-Cake -c user.email=igkharin@gmail.com; exact author/committer were checked. All new executable outcomes are NOT_RUN.
