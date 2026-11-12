# KANI B3P tree identity check

Static acceptance: PASS. This checks Git tree identity, not a new Kani/CBMC result.

- Repository: `/root/kani-fix-zst-b3`.
- Initial branch: `fix/zst-union-codegen`; clean.
- Base: `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`; tree `22641d9be125b05846c0e3fc21c09fc230f57076`.
- Old head: `6db3c4dabd4a368314eb8e2b71d21d1eee721593`; tree `c9b9bafdeca616fac235574f33dad477c25ad90b`.
- New local head: `83a413f9be2d57389c991d9f5d1250b4e4386203` on `fix/zst-union-codegen-v2`; tree `c9b9bafdeca616fac235574f33dad477c25ad90b`.
- Sole parent: `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`; commits in base..new: 1.
- Old branch remains at `6db3c4dabd4a368314eb8e2b71d21d1eee721593`.
- New author and committer: `Tiramisu-Cake <igkharin@gmail.com>`.
- Exact three-file composition and empty old..new diff: PASS.
- No Kani push or new compiler/verifier/CI run. New head: NOT_RUN.

## Commands and outcomes

Commands ran sequentially in the repository above. Empty output is shown explicitly.

```text
$ git status --porcelain=v1
exit: 0
(empty output)
```

```text
$ git branch --show-current
exit: 0
fix/zst-union-codegen
```

```text
$ git rev-parse HEAD
exit: 0
6db3c4dabd4a368314eb8e2b71d21d1eee721593
```

```text
$ git rev-parse HEAD^{tree}
exit: 0
c9b9bafdeca616fac235574f33dad477c25ad90b
```

```text
$ git branch --list fix/zst-union-codegen-v2
exit: 0
(empty output)
```

```text
$ git rev-parse bf9c58e662fd65c64381ef2ac97a6397ffc0693a^{tree}
exit: 0
22641d9be125b05846c0e3fc21c09fc230f57076
```

```text
$ git switch -c fix/zst-union-codegen-v2 bf9c58e662fd65c64381ef2ac97a6397ffc0693a
exit: 0
Switched to a new branch 'fix/zst-union-codegen-v2'
```

```text
$ git restore --source=6db3c4dabd4a368314eb8e2b71d21d1eee721593 --staged --worktree -- kani-compiler/src/codegen_cprover_gotoc/codegen/typ.rs tests/expected/zst-union-arm/main.rs tests/expected/zst-union-arm/expected
exit: 0
(empty output)
```

```text
$ git write-tree
exit: 0
c9b9bafdeca616fac235574f33dad477c25ad90b
```

```text
$ git -c user.name=Tiramisu-Cake -c user.email=igkharin@gmail.com commit -m Fix padded union codegen for zero-sized fields
exit: 0
[fix/zst-union-codegen-v2 83a413f9b] Fix padded union codegen for zero-sized fields
 3 files changed, 184 insertions(+), 2 deletions(-)
 create mode 100644 tests/expected/zst-union-arm/expected
 create mode 100644 tests/expected/zst-union-arm/main.rs
```

```text
$ git rev-parse HEAD
exit: 0
83a413f9be2d57389c991d9f5d1250b4e4386203
```

```text
$ git rev-list --parents -n 1 HEAD
exit: 0
83a413f9be2d57389c991d9f5d1250b4e4386203 bf9c58e662fd65c64381ef2ac97a6397ffc0693a
```

```text
$ git rev-list --count bf9c58e662fd65c64381ef2ac97a6397ffc0693a..HEAD
exit: 0
1
```

```text
$ git rev-parse HEAD^{tree}
exit: 0
c9b9bafdeca616fac235574f33dad477c25ad90b
```

```text
$ git rev-parse 6db3c4dabd4a368314eb8e2b71d21d1eee721593^{tree}
exit: 0
c9b9bafdeca616fac235574f33dad477c25ad90b
```

```text
$ git diff --exit-code 6db3c4dabd4a368314eb8e2b71d21d1eee721593 HEAD
exit: 0
(empty output)
```

```text
$ git diff --check bf9c58e662fd65c64381ef2ac97a6397ffc0693a..HEAD
exit: 0
(empty output)
```

```text
$ git diff --name-only bf9c58e662fd65c64381ef2ac97a6397ffc0693a..HEAD
exit: 0
kani-compiler/src/codegen_cprover_gotoc/codegen/typ.rs
tests/expected/zst-union-arm/expected
tests/expected/zst-union-arm/main.rs
```

```text
$ git status --porcelain=v1
exit: 0
(empty output)
```

```text
$ git rev-parse refs/heads/fix/zst-union-codegen
exit: 0
6db3c4dabd4a368314eb8e2b71d21d1eee721593
```

```text
$ git show -s --format=%an <%ae>%n%cn <%ce>%n%s HEAD
exit: 0
Tiramisu-Cake <igkharin@gmail.com>
Tiramisu-Cake <igkharin@gmail.com>
Fix padded union codegen for zero-sized fields
```
