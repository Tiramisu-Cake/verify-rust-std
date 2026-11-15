# S1 worker11 inputs

Task/CURRENT-TASK for this bounded session: `TASK-CH8-S1-W11.md`, g0 entry
`815f97fce4` (shared worktree; later unrelated research commits are possible).
No per-worker CURRENT-TASK/CHECKPOINT existed on std872d. This packet plus
CHECKPOINT.json is the worker11 handoff, not a new lane or budget registration.
CORE v1 and RUNTIME-CODEX (2026-10-22/23), root/project AGENTS and Evidence v0.11 read.
Direct assignment supplies Cloud $0, no local compiler/verifier, no push/CI/publication.
Thread cwd is /root; shell commands use explicit assigned worktree. No watcher or
Cloud lane is armed; the new-session watcher cwd prerequisite is not qualified.

Std base: `872d5a43380752786415bc00d2a12ce0e930cb37`
Tree: `384023c2f80a04d0618aa7ce971b1419494b062b`
Parent: `233f96f66ab3785881cead133817ed5db4c76b09`
Worktree: `/root/verify-rust-std-ch8-s1-w11`
Branch: `work/ch8-s1-model-w11`, created from existing /root/verify-rust-std objects.
Preflight: object/tree correct; destination/branch absent; worktree list checked;
11GiB available before creation. No clone, .git/target copy or toolchain setup.

Kani read-only exact upstream: `0aac16ef62da9e9d5645782d458593e5d78143ba`
Tree: `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`
Parent: `3e095c22a231de1d7acd2410b71f0fc8e6970c19`
Identity read by git show from /root/kani-fix-3300-c2-s6; shared Kani worktree is
created/owned only by13. No Kani modifications, C2 or SEL1 patches.

Local source commit identity:

```
3f469d3ba2e94d7129e66e53ea76df883ff9c946
08c51f3cbe8c2e0d053001ca9ed9e5a67e3576c0
872d5a43380752786415bc00d2a12ce0e930cb37
Tiramisu-Cake <igkharin@gmail.com>
Tiramisu-Cake <igkharin@gmail.com>
Add S1 closed sorting model and opt-in controls [skip ci]
```

Only the two allowed new model/control files differ from std872d. Patch:
`model-source.patch`, SHA256 `80ba49248bc72e89d9e86f061cc620b4333d59c7f28ab13163323c5c690d79bb`.
Exact per-file hashes and synthetic results: synthetic-result.json.
Actual Rust/Kani/compiler qualification and six-body contracts: NOT_RUN.
