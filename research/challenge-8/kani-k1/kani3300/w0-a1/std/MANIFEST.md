# W0-A1 std test-only overlay manifest

## Identities

| Identity | Commit | Tree | Library subtree |
|---|---|---|---|
| Frozen std source | `70ba5befc617627073738e26cb1466bd4fb76e41` | `84ab170ccdcc29fba69e55e0a46e6acdf52d9704` | `6ea9d3425f6d0478cfc2517cbdd2fb7d7b32a53f` |
| Accepted SEL1 test-only base | `6075e7ce17179f45642c9ffe8fe09e3ec9395726` | `a7795c5a49a4f3f00b774356c0ae3fb2a89c6825` | `12e87bd4a4e141a8f829d8a0519efc09260c5059` |
| A1 test-only package | `65864680a145c90c583dcba7efd1d569475519fc` | `318753826afce4c952e8210b67a8b5919f646f9b` | `93d2f428370a2a9dbedafd6dd598305b46aac50c` |

The local source commit has subject `Add opt-in CH8 W0-A1 actual body probes [skip ci]`, branch `work/ch8-w0-a1-w15`, parent exactly `6075e7ce17179f45642c9ffe8fe09e3ec9395726`, and author/committer `Tiramisu-Cake <igkharin@gmail.com>`. It is local only and is not pushed or dispatched.

`base_tree` means the full 6075 accepted-package tree (`a7795c5…`); `base_library_tree` means its `library/` subtree (`12e87bd…`). The frozen 70ba identities are included to make the full CI export patch reproducible.

## Scope and files

The A1 overlay changes exactly:

1. `library/core/src/slice/sort/shared/smallsort/verify.rs` — adds only `#[cfg(kani_smallsort_controls)] mod wave0_a1;`.
2. `library/core/src/slice/sort/shared/smallsort/verify/wave0_a1.rs` — adds eight exact roots, three small macros, a verification-only transparent `A1FreezeNonCopy(u64)`, and the existing panic-stub replacement.

No production file, compiler/runtime code, algorithm, existing fixture, or ordinary CI root changes. The conditional registration is opt-in; ordinary CI leaves it disabled.

| Artifact | Meaning | SHA-256 |
|---|---|---|
| `overlay-from-6075.patch` | Exact A1 diff applied to 6075 accepted package | `05da44f4ded67994140025607666037911e2105ae613c002451dea39618fa2d5` |
| `combined-from-70ba.patch` | Complete `library/` diff from frozen 70ba through accepted 6075 package plus A1, for std CI export; excludes unrelated research paths | `bb076677040e5da399df6a1751814add5ba4f2a8d4c58ee02e78a95022ac918a` |
| `verify.rs` | Final registration source | `f7741fde76545b53c98742149c2081c3ef6de8c7f004fe4522473cd64a611f1c` |
| `wave0_a1.rs` | Final eight-root module source | `453218bd78b39d8e30881ada9bc442b50d3e1d63b81151410ec25b2ecf467299` |

Patch application, source code, and package identity are statically recorded; neither patch was applied in a separate checkout as that would create unnecessary worktree state. `git diff --check` passed on the final source edit. No local compiler or verifier validation is claimed. The frozen→final patch is restricted to the six listed `library/` paths; the accepted upstream research additions are excluded.

## Selectors and covers

Exact selectors and route expectations are documented in [`../ROUTE-MAP.md`](../ROUTE-MAP.md). The selector prefix is `slice::sort::shared::smallsort::verify::wave0_a1::`; the suffixes are:

- `stable_freeze_u64_n8`, `stable_freeze_u64_n16`, `stable_freeze_u64_n32`
- `unstable_general_nocopy_u64_n8`, `unstable_general_nocopy_u64_n16`, `unstable_general_nocopy_u64_n32`
- `unstable_network_u64_n18`, `unstable_network_u64_n32`

Each root contains four regular useful covers: call-begins, comparator-invoked, call-returns, and readbacks-complete. The exact copied `cut_merge_order_violation` body from `verify/helper_contracts.rs` retains the conditional `helper contract merge order violation reachable` cover; that additional cover is separate and its reachability is not presumed. It volatile-reads exactly N output payloads after return, for a combined static count of 162 across the eight independent selectors. Guard/frame assertions are used only where initialized adjacent/tail storage is present. No scratch is read as initialized `T`.

## Unwind and validation status

All roots use the existing source fixture bound `#[kani::unwind(34)]`. In the selected source routes, all sort, insertion, merge, and readback loop extents are finite and at most 32 active elements, with loop termination; the 34 bound is a static initial bound. Every unwinding assertion must still be inspected in future CI. Any unwinding failure is a STOP condition; this package authorizes neither bound increases nor disabling checks.

Static checks only: exact parent/tree identities; allowed path list; source route/type/length/offset review; output count; patch SHA-256; and `git diff --check` on the final source edit. Compiler acceptance, route reachability, comparator/event coverage, runtime normal return, and unwinding-check results are `NOT_RUN`. No local Cargo/rustc/Kani/CBMC/Miri/build/setup or CI command was run.
