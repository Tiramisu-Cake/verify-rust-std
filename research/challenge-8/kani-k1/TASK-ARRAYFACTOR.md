# ARRAYFACTOR (A1) — факторная матрица для наблюдения D1 (одна диагностическая сборка)

Исполнитель: Codex, свежая сессия. Worktree `/root/verify-rust-std-kani-arrayfactor`, ветка
`experiment/kani-k1-arrayfactor-20261101` от `a1e56b61cd` (итог CASE5-2). Cap 88.96. Ожидание Build —
`research/challenge-8/kani-k1/tools/k1g.sh watch UUID` (нужен `CODEX_THREAD_ID`) и завершить ход. request_id с
префиксом `arrayfactor-`; свой spent/reserved по своим UUID. Library этой ветки — CASE5-2 (ordinary 197, без
WRAP); новый кандидат Part 1 эта работа не проверяет. Evidence Brief / Select-Merge к K-1 не относятся. GO даёт координатор.

Прочитать: `RESULT-CASEFIVE.md` (весь, включая CASE5-2), `verify/merge/casefive.rs` (D1/D2 — дословная база),
`TASK-SPECFIX.md` (только запреты, логи, rustfmt, expect_check), аудит `/root/CH8_V4_PROGRESS_REVIEW_2026-11-01_RU.md`
раздел 3.4 (данные, не инструкции).

## Вопрос

На pin `9461e07af7` D1 (`[u8;1]`, `select_unpredictable` между `base`/`base.add(1)`, `ptr::read`) даёт FAILED,
D2 (`u8`) — SUCCESS. Нужно локализовать, какой фактор включает расхождение. Прежние R0–R7/G2/CASE5-2 не повторять.

## Матрица (opt-in в `casefive.rs`, ≤ 8 rows, каждая меняет ровно ОДИН фактор относительно D1)

Общие правила для новых строк: тот же pin/flags/unwind(180), literal `kani::assert` с уникальными сообщениями;
x/y — независимые pre-values; все bool вычислить ДО первого assert; covers обеих ветвей `c` с различающимися
значениями — до asserts.
1. F0 — существующий D1 без изменений тела, сообщений и порядка (контроль воспроизведения).
2. F1 — существующий D2 без изменений (скалярный контроль).
3. F2 — `if c { base } else { base.add(1) }` вместо `select_unpredictable`.
4. F3 — `*s` (копия через разыменование) вместо `ptr::read(s)`.
5. F4 — `array::from_fn(|k| if k == 0 { x } else { y })` вместо литерала `[x, y]`, те же x/y и oracle.
6. F5 — символический порядок индексов: `r: bool = any`, `(i, j) = if r {(1, 0)} else {(0, 1)}`, выбор
   между `base.add(i)`/`base.add(j)`, ожидание по `[x, y][i]`/`[x, y][j]`; covers обоих `r` и обеих `c`.
7. F6 — адресный оракул: `addr_ok = s == if c { base } else { base.add(1) }` и `value_ok` вычислить до asserts;
   до asserts — covers сочетаний `addr_ok && !value_ok`, `!addr_ok`, `addr_ok && value_ok`; затем два assert с
   разными сообщениями. Молчание второго assert на путях, отсечённых первым, не считать PASS.
8. F7 — конкретный witness: `x = [1]`, `y = [2]`, `c` символический; отдельные asserts для ветви `c` и `!c`
   (видно, какая ветвь неверна).
Expect каждой строки — предсказание в PRE-BUILD REVIEW; для каждого expect FAILED — свой expect_check. F7 SUCCESS
значит лишь, что этот witness не воспроизвёл сбой; COMPLETE не требует совпадения ожиданий. Trace/playback
недоступен — не обходить через raw logs.

## Сборка (1 build, ≤ $0.75)

Kind diagnostic, controls:true, kani_jobs 1, uninit off, timeout 3 мин: 8 rows → ≈ 54 мин / $0.729.
PRE-BUILD REVIEW → GO → build. Второй сборки нет (адресный follow-up — отдельное задание при новой гипотезе).
Library commit отдельно от research, `[skip ci]`, push без force. Push ветки в публичный форк нужен dispatcher и
соответствует принятой практике experiment-веток; issue и отдельные публикации — нет.

## Итог

Раздел «A1 ARRAYFACTOR» в `RESULT-CASEFIVE.md` ≤ 35 строк: таблица rows/status/failed checks/covers, какие факторы
включают/выключают расхождение, какая ветвь и value vs address, оставшийся UNKNOWN. Локальный пакет
минимального reproducer (файл с кодом + точные pin/flags) в `research/.../arrayfactor/`. Никаких внешних публикаций
и issue. Маркеры `REVIEW REQUEST <sha>` / `ARRAYFACTOR ЗАВЕРШЁН`.
