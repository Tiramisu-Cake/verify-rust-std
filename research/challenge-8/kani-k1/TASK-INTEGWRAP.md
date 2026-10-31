# INTEGWRAP — WRAP-N2 в обычный набор Part 1 (кандидат P1 v3)

Исполнитель: Claude Code, свежий контекст, tmux 4. Worktree `/root/verify-rust-std-kani-integwrap`, ветка
`experiment/kani-k1-integwrap-20261101` (создана координатором) от `f000cb484e` (итог P1-CLEAN: library
tree `73e902bec8`, ordinary exact 197, cfg-on 377). Cap 88.96 унаследован. Ожидание Build —
`k1g.sh wait UUID` в фоне. Evidence Brief / Select-Merge к K-1 не относятся. Владелец до утра
недоступен — все GO даёт координатор.

Прочитать: `RESULT-PONECLEAN.md`, `TASK-SPECFIX.md` (запреты, логи, rustfmt, expect_check — действуют),
отчёт WRAP-N2 в ветке `experiment/kani-k1-wraptwo-20261031` (`research/challenge-8/kani-k1/RESULT-WRAPTWO.md`
и `wraptwo/` на `73336711b0`; читать через `git show`, worktree `/root/verify-rust-std-kani-wraptwo` не трогать).

## Цель

1. Перенести library-изменения WRAP-N2 (коммиты `4777a344ea`, `471db13c99`, `811c78777d`: новый
   `verify/wrap.rs` и регистрация в `verify.rs`) — только `library/`, без research WRAP.
2. Сделать три wrapper PFC обычными: `stable_cell_n2`, `unstable_byte_n2`, `freeze_noncopy_n2`
   попадают в ordinary; контроли `rejects_always_true`, `rejects_payload_corruption` остаются под
   `#[cfg(kani_smallsort_controls)]`. Wrapper-функции, модели и guard должны компилироваться в обоих cfg.
   Ordinary = exact 197 + 3 = **200**; cfg-on = 377 + 5 = **382** (сверить по source, не угадывать).
3. Правок в других verify-модулях и `smallsort.rs` нет; регистрация в `verify.rs` — без перестановки
   модулей; doc-комментарий `verify.rs` обновить одной строкой о wrappers. Комментарии в `wrap.rs`
   оставить сжатыми (бюджет комментариев проекта), rustfmt `--check` чистый (wrapper из TASK-SPECFIX).
   Runtime bodies/signatures не меняются (статическая проверка, как в P1-CLEAN).

## Сборки (≤ 2 builds, ≤ $1.5)

- G1 measurement, controls:true, kani_jobs 1, uninit off, timeout 10 мин: 3 wrapper PFC (SUCCESS) +
  2 controls (FAILED с exact expect_check из WRAP-N2). Компилирует cfg-on дерево целиком.
- G2 inventory controls:false: ordinary exact 200 по именам (197 frozen + 3 wrap).
PRE-BUILD REVIEW → GO координатора → G1 и G2 (можно отправить подряд, если library не меняется).
Library commit отдельно от research, всё `[skip ci]`, push без force.

## Итог

`RESULT-INTEGWRAP.md` ≤ 50 строк: library commit/tree, exact 200 / 382 (имена — файлы рядом), G1 rows
(status/VT/RSS/covers/failure location), G2, стоимость. Строка для координатора:
`P1 V3 CANDIDATE library tree <sha>`. Маркеры `REVIEW REQUEST <sha>` / `INTEGWRAP ЗАВЕРШЁН`.
