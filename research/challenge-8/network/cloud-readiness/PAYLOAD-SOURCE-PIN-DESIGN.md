# Pinned-source fetch for unchanged `library/core` files — PREPARED_NOT_REGISTERED

N2 (2026-10-22), budget 0. Design only: no client, recipe, runner or transport change is made or registered here. Implementation and adoption are separate reviewed tasks per owner/lane.

## Problem

`pinned-objects` ships every recipe file as gzip+base64 bytes inside Build substitutions. The cap is 191 source chunks of 3990 bytes (≈762 KB encoded; Select `control.py` line ~496). Proof recipes carry up to 14 `library/core` files that are **byte-identical to the source pin** `cd371e035c7e573760c43bf934d53e8118ee3e7d` in all three owner branches (checked 2026-10-22 by blob ID at Select `b96f16be`, Merge `0c0b48f2`, Network HEAD):

| path | blob | raw B | gz+b64 B |
| --- | --- | ---: | ---: |
| library/core/src/hint.rs | 8d7c2a16 | 39646 | 15568 |
| library/core/src/intrinsics/mod.rs | 062a626f | 190319 | 46328 |
| library/core/src/marker.rs | 64a67bbd | 52725 | 19996 |
| library/core/src/mem/manually_drop.rs | 3fb844c7 | 11051 | 4904 |
| library/core/src/mem/maybe_dangling.rs | 46e5228a | 4388 | 2284 |
| library/core/src/mem/maybe_uninit.rs | 94703940 | 66146 | 18400 |
| library/core/src/mem/mod.rs | c36e94c8 | 64406 | 24600 |
| library/core/src/ptr/mod.rs | 7e568140 | 130865 | 44548 |
| library/core/src/ptr/mut_ptr.rs | c9d3c8d7 | 133785 | 29340 |
| library/core/src/slice/mod.rs | 16b5766b | 229683 | 51044 |
| library/core/src/slice/sort/shared/mod.rs | e1977d79 | 1548 | 952 |
| library/core/src/slice/sort/shared/smallsort.rs | 40939f92 | 32293 | 10488 |
| library/core/src/slice/sort/stable/quicksort.rs | acc8a5e8 | 10557 | 4972 |
| library/core/src/slice/sort/unstable/mod.rs | 7ca95a3b | 4971 | 2604 |
| **total** | | **972383** | **276028 (≈70 chunks)** |

Sizes are per-file gzip -9 + base64. The real transport gzips per original object and deduplicates a shared pool, so the numbers are estimates.

## Design

1. **Recipe field** (schema stays `smallsort-cloud-recipe-v1`, new optional key): `source_pin = {repository, commit, paths: [{path, mode, blob, sha256}]}`. `repository` is the public fork URL; `commit` is the full source SHA. Each pinned path must also be listed in `proof_paths`, so the closure inventory is unchanged.
2. **Client preflight** (VPS, before reservation): for each pinned path, require `git rev-parse <proof_sha>:<path>` == `git rev-parse <commit>:<path>` == `blob`, the same mode, and `sha256(bytes) == sha256`. Require the commit to be reachable from a published ref (`git ls-remote` plus `merge-base --is-ancestor`). Then leave these bytes out of the encoded payload and add the manifest (≈14×120 B) to the config. If any check fails: refuse, with no reservation and 0 s spent.
3. **Cloud restore step** (before `source-input.py` closure check): `git init` and `git fetch --depth=1 --filter=blob:none <repository> <commit>`. Then, per path, run `git cat-file blob <blob>`, which fetches the blob lazily. Verify `git hash-object` == `blob` and SHA-256 == `sha256`, and write it with the pinned mode. Any fetch or verification failure ends the Build as `ERROR` before proof tools run; there is no unpinned fallback.
4. **Closure check unchanged:** the restored tree must pass the existing exact closure/union check against original commit/root/tree/blob identities. Evidence records the manifest SHA-256 and the per-path blob/sha256.

## Per-lane estimate (chunks saved at 3990 B)

| owner / recipe | library files | unchanged | saved gz+b64 B | chunks |
| --- | ---: | ---: | ---: | ---: |
| Select `o26-sort4-c1-current-recovery` | 14 | 14 | 276028 | ≈70 |
| Select `o26-sort4-caller-entry`, `o26-compatible-strict-cut-test` | 12 | 12 | 268452 | ≈68 |
| Select `o26-select-callee-r20` | 8 | 8 | 185972 | ≈47 |
| Merge `merge.json` | 2 | 2 | 11440 | ≈3 |
| Merge `coordination-regression` | 0 | 0 | 0 | 0 |
| Network (no recipe yet; the R4/W7 runner needs the `slice/sort` files) | ≤14 | ≤14 | ≤276028 | ≤70 |

## Risks / open (owner decision)

- **Cloud egress and Build seconds:** fetching from GitHub (a partial clone with a blob filter keeps transfer small), and the dependency on GitHub availability. The existing `public-git` source mode already implies egress, so this adds no new trust class. Even so, the new restore step changes the runner and needs service error-path tests: fetch failure, wrong blob, wrong sha256, missing path, mode mismatch, unreachable commit.
- **Hashes:** blob IDs are SHA-1. The per-file SHA-256 binds the content independently.
- **Shared code:** the change touches shared files (`control.py` transport, `source-input.py`, recipe schema). It has to be adopted per owner branch with identical bytes, like the coordinator, or kept owner-local.
