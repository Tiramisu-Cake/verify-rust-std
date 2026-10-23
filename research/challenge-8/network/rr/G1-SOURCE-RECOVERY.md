# SOURCE AVAILABLE

2026-10-12. Baseline `42d01e4c0ad136aa81f95575703c8661998b61c5`;
policy/AGENTS/WORK-POLICY/runbooks прочитаны на origin/main
`6e1a8e59c56669abe5e6ec2013478e45ed2cc267`. Source recovery + cleanup only;
Cloud budget/charge **0/0**, compiler/extraction/proof/Cloud **NOT_RUN**.

## Exact source

Исходный собственный clone обнаружен в
`research/challenge-8/refinedrust-feasibility/.sources/refinedrust`.
Он уже упоминался в первоначальном FEASIBILITY-REPORT; последующие проверки
пропустили вложенную `.sources/`. Прежнее утверждение EXTERNAL TRANSFER REQUIRED
было ошибочным и здесь исправлено. Другой pin/July artifact не использовался.

Устойчивый путь вне `/tmp` и вне project Git:

```text
/root/refinedrust-feasibility-sources/refinedrust-332d945fafa14bf55c0c8390cb35ec4b0c012cff
```

Clone перенесён на том же filesystem; старый ignored `.sources/refinedrust`
оставлен symlink на этот путь. Source не добавлен в Git, дубликат не создан.
Отдельная object database clone содержит нужный commit; в project object database
этого RR object нет. Сеть для recovery не использовалась; внешний bundle не нужен.

- HEAD: `332d945fafa14bf55c0c8390cb35ec4b0c012cff`.
- Tree: `b33bcccbbbd6168ac73e0c7238a1edddbe34057c`.
- `git fsck --full` PASS до/после переноса, working tree clean.
- Все **2569 tracked files** сверены с Git blob SHA1 и mode/symlink bytes.
  Шесть SHA256/размеров совпали с existing pinned inputs; таблица ниже.
- Clone shallow: полная ancestry не заявляется; exact commit/tree/source доступны.

| Путь относительно source root | Git blob | SHA256 |
| --- | --- | --- |
| rr_frontend/Cargo.toml | 1d7891a06d5dc4e5e5d5f8566f25526968f25331 | 5c8636be6c5f25949e57d07b8462c636aa2f2d91d91da12c66234477bc9290f7 |
| rr_frontend/Cargo.lock | d357fa171478753f558fede6ec0131194099e0f7 | b66b9e281478be8263eab9ba210964cdd8f1db92535b7b81305f50dea03682aa |
| rr_frontend/rust-toolchain.toml | 1c9f8e2eac71626fee9584d8a27d5b944e0ff7df | 79ef42e730fcc0bc23bde84ca0509970d4e1702d59e92300c85108488cf24aba |
| rr_frontend/refinedrust_frontend/src/bin/cargo-refinedrust.rs | 4de3d90610e0a3c40620ce9ef034ecfa7f58495a | 8f811a28f21a373048004b17c499b91b8f99b8d292492705cdf2d5677b8f8c56 |
| rr_frontend/refinedrust_frontend/src/bin/refinedrust-rustc.rs | 2e0a15eb4d22a3e1bc0a0b4028f66c4ababb43b3 | d09d07f730ca7a47dd0e2dfcf6bb33f3047d02951d4a331a57ac84f6a91e7131 |
| rr_frontend/rrconfig/src/lib.rs | d3635e40ea569949addf02ca4f0bf7f2bfc473ce | 2b0a0da357204bbe5794cdf4fcc78dc37452ff71927f7cbcbdb0fcc1f3522228 |

Local receipt: `/root/refinedrust-feasibility-sources/SOURCE-RECEIPT-2026-10-12.json`.
Это source identity, не frontend replay, workflow compatibility или safety proof.
Runner/parser/CI/Cloud integration не менялись.

## Cleanup

`df -h`/`df -i` проверены до/после: root 50G, used 48G, free около **2.4G**,
96%; inode usage **20%**. После cleanup `df -B1`: available **2553573376 bytes**.
Global free-space delta не приписывается этой задаче: другие процессы меняют disk.

В `/tmp` собственные `rr-g1-*` test dirs прошлой подготовки отсутствуют — их
TemporaryDirectory уже убрал. Похожие `g1-cb-old.patch`, `g1-cb61-h2b-static-20261008`,
`g1-cb61-h2c-static-20261008`, `g1-cfg-patch`, `g1-cfg-v2` и
`g1-remediation-review-217c939` оставлены: принадлежность этой миссии/ненужность
не установлена, review data могут быть evidence. Массовой очистки не было.

Удалены только generated Git metadata собственного clone, под устойчивым source
root выше: `.git/hooks/` с 14 неактивными `*.sample` и необязательный
`.git/objects/pack/pack-3bb8b1e741812f019ae3a1c484a0a4e9db878ca5.rev`.
Samples: applypatch-msg, commit-msg, fsmonitor-watchman, post-update,
pre-applypatch, pre-commit, pre-merge-commit, pre-push, pre-rebase, pre-receive,
prepare-commit-msg, push-to-checkout, sendemail-validate, update (все `.sample`).
Скан `/proc` cwd/exe/fd/maps не нашёл активных references на clone или недоступных
process records. Working source, pack/idx/refs/shallow и provenance logs сохранены.

Освобождённые allocated blocks: **81920 bytes (80 KiB)**; logical file bytes
**37225**, 15 файлов + пустой hooks directory. Полный path/size receipt:
`/root/refinedrust-feasibility-sources/CLEANUP-2026-10-12.json`.
Исторический `.sources/artifact-v2.tar.gz` сохранён как evidence, SHA256
`34573bac60de68c3597c23136cd5221a7129f89a24b69340f8e361750f331d53`.
Shared caches/worktrees/ledgers/coordinator/raw evidence не удалялись.
Новых временных файлов не оставлено. После documentation commit/push **STOP**.
