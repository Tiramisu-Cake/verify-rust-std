# KANI3300 B1I — static handoff
- Exact task/research input: `2abd5b1669b64336e6802dac86ba7c5a007d470e`; audit input `124a45e373`; only B1I performed, Cloud $0.
- Kani upstream base `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`; stage parent `a0a2386001a15fecfe2facc2f6cd87f3dee13b60` (clean exact branch at start).
- Production `cdb439b0a4c36e9e595019895ab803230f332941`; test parent is that production commit.
- Test/tip `dc5f5a406749a73f1c3192e0b5338441e79508bb`; tree `085bea5cda2df66a5cb4f72410fe124aa816c90b`; Kani worktree clean, no push.
- Single walk/common flush, local diagnostic owner, shared call classification, fallible seed resolution and no bodyless-callee unwrap; unchanged Item-only A3 pairing/ABI/false transfer/Move/layout/raw_eq policy.
- Standalone B1 commit-by-commit adaptation/non-transfer reasons and boundaries: NOTES.md; 24 new source/golden pairs, 33 unchanged existing harness controls and four compiler input specifications: TEST-MANIFEST.json.
- Static checks: production and complete stage `git diff --check`, staged new-fixture whitespace, permitted rustfmt --check on all changed Rust files PASS; 11/11 pinned API source hashes match.
- Source audit found no new unused import/API mismatch or obvious -D warnings issue; compiler/build/Clippy/Kani/CBMC and all runtime/lowering outcomes NOT_RUN.
- Independent Luna HIGH semantic review: no scoped production blocker; fixture binding/seed corrections re-reviewed; source/golden hashes match. REVIEW.md records caveats, no CI/proof credit.
- Remaining required controls: synthetic direct-shadow Shim argument-only and genuine FnDef resolver Err; source probes/goldens do not prove these branches. Shim kind/body and return-only/entry/read property reachability remain NOT_RUN.
- Known input raw_eq legal failure remains open. Foreign/realloc, unknown-intrinsic/recursive points-to and excluded compound/DST/ordinary-union-constant/backend scope are not repaired or newly claimed supported.
- Handoff to coordinator: exact tip above for existing fork Uninit Quick (fmt/build/clippy, all uninit suites, new controls, singleton/JSON properties and MIR/GOTO order/count/identity checks). Executor dispatches nothing; subsequent CI result analysis/repair is a separate stage.
- Full Part 1 gate remains open. No workflows/Actions/Cloud builds/PRs/issues/comments/raw logs/archives were changed or accessed; research stage/push contains only kani3300/b1i/.
- READY means statically prepared candidate, not CI PASS or publication readiness. Stop after this handoff.
READY dc5f5a406749a73f1c3192e0b5338441e79508bb
