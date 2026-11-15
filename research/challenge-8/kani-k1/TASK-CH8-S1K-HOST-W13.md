# TASK — worker13: S1 CI control на хосте kani-форка (одна стадия, contingency)

Это верификация корректности, не security-работа. Отвечай кратко.

## Контекст

Твой S1 пакет (g0 `e6ee41020e`, control `f88bf3f0ea0ef1f87ca01ba5da11b57be574adf1`, parent std
`75a4d1ea6eb60c63c27c1b18e662740d93bafb08`) координатор запушил в `Tiramisu-Cake/verify-rust-std`
ветку `uninit-ci/ch8-s1-a` 2026-11-15 ~23:11 UTC. На std-форке GitHub Actions не создал ни run,
ни check suite (только чужое приложение); то же для same-tree sibling-коммита и минимального
probe workflow. YAML валиден, Actions enabled, push-runs на этом форке работали до 2026-11-01.
На `Tiramisu-Cake/kani` push-trigger в ту же ночь работает (A1, B census). Причину std-форка
пока не знаем; если run там всё же появится, координатор оставит один из двух и отменит другой.

## Что сделать

Подготовить вариант того же S1 batch, который запускается из `Tiramisu-Cake/kani`:

1. CI-only control commit в kani-клоне (worktree `/root/kani-ch8-s1k-w13`), parent = upstream tool
   `0aac16ef62da9e9d5645782d458593e5d78143ba`; изменены только `.github/workflows/` и один каталог
   control (например `ch8-s1-control/`). Stock push workflows удалить в этом коммите.
2. Workflow: push на `uninit-ci/ch8-s1k-*`, guard `github.repository == 'Tiramisu-Cake/kani'`.
   Checkouts: control (github.sha, depth 2) + production std export `75a4d1ea…` из
   `Tiramisu-Cake/verify-rust-std` (public, depth 2, submodules как раньше) + tool
   `model-checking/kani@0aac16ef62…`. Чеклист: `runner.*` только в step env, sibling layout,
   path normalization от cwd, static YAML/actionlint.
3. Binding: переписать только проверки хоста (repository, ref prefix, HEAD^ == tool sha, single
   parent, changed paths, единственный workflow). `runner.py`, rows/oracles/caps/23 строки — байт
   в байт как в `f88bf3f0ea`; если иначе нельзя — показать минимальный diff и причину.
4. Synthetic tests на новые проверки + прежние error paths. Независимое review (обычный reviewer
   этой среды), findings исправить.
5. g0: `kani3300/ch8-s1/kani-host/` — CI-REQUEST (SHA/tree, SHA256 manifest), REVIEW, HANDOFF.
   Коммиты `[skip ci]`, author `Tiramisu-Cake <igkharin@gmail.com>` в команде.
   Последней строкой: `READY <control-sha> <g0-sha>` или `STOP <причина>`.

## Ограничения

Без push/CI/публикаций/ledger. Без локальных cargo/rustc/Kani/CBMC. Production std commits не
менять. Raw logs не читать.
