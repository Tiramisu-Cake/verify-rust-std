# SPECFIX-A2 — feasibility build финального StageA (профили без adapter)

Исполнитель: Claude Code, свежий контекст, tmux 1. Worktree `/root/verify-rust-std-kani-specfix`, та же ветка
`experiment/kani-k1-specfix-20261031`, база — текущий HEAD (StageA final, library tree `31997f7781…` после revert
row 10). Прочитай `research/challenge-8/kani-k1/RESULT-SPECFIX.md`, `specfix/manifest.json`, `specfix/REVIEW.md`,
`TASK-SPECFIX.md` (правила/ограничения действуют, кроме перечисленного ниже).

Цель: впервые исполнить StageA profiles без raw adapter. Library НЕ менять (если нужна правка для компиляции —
остановиться, описать, `PRE-BUILD REVIEW` с delta и ждать GO). Никакой миграции PFC/stub consumers.

Одна сборка, ≤ $2: measurement, controls:true, kani_jobs 1, uninit off, timeout 10 мин, entries = прежние G1 rows
1–9, 11, 12 (row 10 удалён) — 11 entries, envelope 140 мин ≈ $1.89. expect_check для FAILED — точные literal
`kani::assert` messages; сверить file:line по финальному дереву (row 11 теперь merge/specfix.rs:588 по отчёту —
перепроверить). Подготовить request (новый request_id), validate, commit+push research, `PRE-BUILD REVIEW <sha>`,
ждать GO. После — `k1g.sh wait` в фоне, затем bounded summary/peaks/check-tooling (база 30f77e8599).

Итог: дописать в `RESULT-SPECFIX.md` раздел «A2» (≤ 40 строк): по каждой row статус/VT/RSS/covers/failure location,
cfg-on compile финального дерева (подтверждён самой сборкой), что это значит для гейта P1-clean. Маркеры
`REVIEW REQUEST <sha>` / `SPECFIX-A2 ЗАВЕРШЁН`. Глобальные правила Evidence Brief/Select-Merge не применяются.
