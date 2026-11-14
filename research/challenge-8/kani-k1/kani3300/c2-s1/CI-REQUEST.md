# C2-S1 — coordinator CI request (NOT_RUN)

Exact source `ba0e5cfedf31e20d18e95b50ba5dbd6946277d2c`, tree `0fe7f51c1017656ae141f7d223ac737a930d7265`, B1 parent `6fe484b30043b3696b5f1ccc4bea0e42891ad012`, U `0aac16ef62da9e9d5645782d458593e5d78143ba`. See INPUTS.json component hashes and independent-review.md. Local source is committed and clean; **not pushed**. Only coordinator may publish/dispatch; this file does not authorize a new build/lane/budget.

Use existing preflight/CI, unchanged dependencies and per-fixture flags. Suggested order:

1. Existing fmt, compiler/build, clippy and relevant unit checks; resolve compiler/typecheck failures before verifier work. Validate changed source signatures/imports with actual compiler. All are currently NOT_RUN.
2. Existing targeted Uninit/expected checks, including tests/kani/Uninit and tests/expected/uninit. Preserve fixture-specific object-bits 12; no global profile override or skipped checks.
3. Atomic controls: tests/kani/Uninit/atomic_store.rs and tests/expected/uninit/atomic. Check volatile store initializes memory/pointers and does not read old holes; nonvolatile pre-check remains; null and adjacent-hole negatives remain failing; exchange returns old value.
4. Explicit-tail-call boundaries: tests/ui/explicit-tail-calls, tests/ui/explicit-tail-calls-stubbing (original/replacement), tests/script-based-pre/autoharness_explicit_tail_call; preserve tests/kani/TailCall/unreachable.rs. Explicit tail calls must produce intended diagnostics, not compiler panic.
5. All 28 unresolved-call Rust fixtures (FIXTURE-INVENTORY.json), both plain/seeded paths. Bind entry loads → operand checks → Unsupported and common target publication for initialized/partial and pending-ops; preserve seed/edge effects. Verify actual instance/body/MIR and property reachability before interpreting generated-positive controls. Compiler-input specifications without an executor remain NOT_RUN.
6. Ordinary/PFC/closure and cycle controls: ordinary-slots, points-to-cycles, closure-upvars, closure-zst, private-transfer-frame, transfer-qualification, maybe-uninit-call-pairing/call-move; existing contract expected/ui/script controls. Bind RegistrationOverride trampoline and DiscardedClosureOverride selection, readable exact cycle boundary, per-root Err and no partial graph joins; preserve own useful assertions and legal companions.
7. Existing three Part1 JSON suites uninit-contract-oracles, uninit-contract-mode-boundaries, uninit-part1-composition; plus existing upstream JSON-handler schema/export tests and validator. Run existing Python checker success/error-path tests through CI. No new host/path normalization, expected regeneration or weakened inventory acceptance.
8. Existing Linux Quick including required trailing stages on this exact head after targeted checks. Preserve stage counts, exits, failures and NOT_RUN after any infrastructure stop. Record host/tool/dependency identities and source/tree pins.

If JSON inventories drift, capture the exact suite/root/property/status and actual versus expected inventory, localize the source of drift and hand it to S5; do not auto-bless or conceal lost checks. Any other semantic regression requires STOP with source/harness/property map. F5–F8 remain known deferred work, not permission to relabel unrelated failures.

No three-platform full-gate promise in S1; the full C2 Gate A belongs after S2–S6/freeze. Old C1b gate receipts do not qualify this tree. CI evidence must use smallsort-brief; no raw archives/full logs. No execution or proof credit is claimed by this request.
